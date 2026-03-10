"""
tests/test_core_shacl.py

Tests for kc/resources/kc_core_shapes.ttl (abstract SHACL shapes).
These tests construct minimal RDF graphs inline and validate against the shapes
directly via pyshacl — testing the static resource, not the package API.

Traceability: see tests/requirements.md
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, Literal
import pyshacl

KC = Namespace("https://example.org/kc#")
EX = Namespace("https://example.org/test#")

_CORE_OWL    = Path(__file__).parent.parent / "kc" / "resources" / "kc_core.ttl"
_CORE_SHAPES = Path(__file__).parent.parent / "kc" / "resources" / "kc_core_shapes.ttl"


def _load_shapes() -> Graph:
    g = Graph()
    g.parse(_CORE_SHAPES, format="turtle")
    return g


def _load_ontology() -> Graph:
    g = Graph()
    g.parse(_CORE_OWL, format="turtle")
    return g


def _validate(data_graph: Graph) -> tuple[bool, str]:
    """Run pyshacl and return (conforms, report_text)."""
    conforms, _, report_text = pyshacl.validate(
        data_graph,
        shacl_graph=_load_shapes(),
        ont_graph=_load_ontology(),
        inference="rdfs",
        abort_on_first=False,
    )
    return conforms, report_text


def _minimal_valid_edge() -> Graph:
    """Construct a minimal valid KC:Edge individual."""
    g = Graph()
    g.add((EX.v1, RDF.type, KC.Vertex))
    g.add((EX.v2, RDF.type, KC.Vertex))
    g.add((EX.e1, RDF.type, KC.Edge))
    g.add((EX.e1, KC.hasSource, EX.v1))
    g.add((EX.e1, KC.hasTarget, EX.v2))
    return g


def test_core_shapes_is_valid_turtle():
    """REQ-CORE-06: shapes file parses without error."""
    g = _load_shapes()
    assert len(g) > 0


def test_valid_edge_passes():
    """REQ-CORE-04: a well-formed edge passes SHACL validation."""
    conforms, report = _validate(_minimal_valid_edge())
    assert conforms, f"Expected valid edge to pass.\n{report}"


def test_edge_same_endpoints_fails():
    """REQ-CORE-04, REQ-VV-02: edge with source == target must fail SHACL."""
    g = Graph()
    g.add((EX.v1, RDF.type, KC.Vertex))
    g.add((EX.e1, RDF.type, KC.Edge))
    g.add((EX.e1, KC.hasSource, EX.v1))
    g.add((EX.e1, KC.hasTarget, EX.v1))   # same individual!
    conforms, report = _validate(g)
    assert not conforms, "Expected same-endpoint edge to fail SHACL."


def test_valid_face_passes():
    """REQ-CORE-05: a well-formed closed-triangle face passes SHACL validation."""
    # Triangle: v1-v2, v2-v3, v3-v1
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e31, EX.v3, EX.v1),
    ]
    for e, s, t in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.hasSource, s))
        g.add((e, KC.hasTarget, t))
    g.add((EX.f1, RDF.type, KC.Face))
    for e, _, _ in edges:
        g.add((EX.f1, KC.hasEdge, e))
    conforms, report = _validate(g)
    assert conforms, f"Expected valid face to pass.\n{report}"


def test_open_triangle_face_fails():
    """REQ-CORE-05, REQ-VV-02: face with non-closed edges must fail SHACL sh:sparql constraint."""
    # Edges: v1-v2, v2-v3, v1-v4 (not a closed triangle)
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3, EX.v4]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e14, EX.v1, EX.v4),  # broken — introduces v4, breaks cycle
    ]
    for e, s, t in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.hasSource, s))
        g.add((e, KC.hasTarget, t))
    g.add((EX.f1, RDF.type, KC.Face))
    for e, _, _ in edges:
        g.add((EX.f1, KC.hasEdge, e))
    conforms, report = _validate(g)
    assert not conforms, "Expected open-triangle face to fail SHACL."


def test_face_wrong_edge_count_fails():
    """REQ-CORE-03, REQ-VV-04: face with 2 edges must fail SHACL."""
    g = _minimal_valid_edge()
    g.add((EX.v3, RDF.type, KC.Vertex))
    g.add((EX.e2, RDF.type, KC.Edge))
    g.add((EX.e2, KC.hasSource, EX.v2))
    g.add((EX.e2, KC.hasTarget, EX.v3))
    g.add((EX.f1, RDF.type, KC.Face))
    g.add((EX.f1, KC.hasEdge, EX.e1))
    g.add((EX.f1, KC.hasEdge, EX.e2))  # only 2 edges
    conforms, report = _validate(g)
    assert not conforms, "Expected 2-edge face to fail SHACL."
