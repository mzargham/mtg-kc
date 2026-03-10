"""
tests/test_core_shacl_extended.py

Extended SHACL shape edge-case tests for kc/resources/kc_core_shapes.ttl.
All tests construct inline RDF graphs and validate via pyshacl directly.

These go beyond test_core_shacl.py to probe boundary conditions, multi-instance
scenarios, and document known blind spots.

Traceability: see tests/requirements.md
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF
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


def _make_valid_triangle() -> Graph:
    """Construct a valid closed triangle: 3 vertices, 3 edges, 1 face."""
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e31, EX.v3, EX.v1),
    ]
    for e, va, vb in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.boundedBy, va))
        g.add((e, KC.boundedBy, vb))
    g.add((EX.f1, RDF.type, KC.Face))
    for e, _, _ in edges:
        g.add((EX.f1, KC.boundedBy, e))
    return g


# ---------------------------------------------------------------------------
# EdgeShape boundary conditions
# ---------------------------------------------------------------------------

def test_edge_with_three_vertices_fails():
    """Edge with 3 distinct boundedBy vertices should fail sh:maxCount 2."""
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3]:
        g.add((v, RDF.type, KC.Vertex))
    g.add((EX.e1, RDF.type, KC.Edge))
    g.add((EX.e1, KC.boundedBy, EX.v1))
    g.add((EX.e1, KC.boundedBy, EX.v2))
    g.add((EX.e1, KC.boundedBy, EX.v3))
    conforms, report = _validate(g)
    assert not conforms, "Expected 3-vertex edge to fail SHACL."


def test_edge_with_one_vertex_fails():
    """Edge with only 1 boundedBy vertex should fail sh:minCount 2."""
    g = Graph()
    g.add((EX.v1, RDF.type, KC.Vertex))
    g.add((EX.e1, RDF.type, KC.Edge))
    g.add((EX.e1, KC.boundedBy, EX.v1))
    conforms, report = _validate(g)
    assert not conforms, "Expected 1-vertex edge to fail SHACL."


def test_edge_with_zero_vertices_fails():
    """Edge with no boundedBy triples at all should fail SHACL."""
    g = Graph()
    g.add((EX.e1, RDF.type, KC.Edge))
    conforms, report = _validate(g)
    assert not conforms, "Expected 0-vertex edge to fail SHACL."


def test_edge_bounded_by_non_vertex_fails():
    """Edge where boundedBy points to a kc:Edge (not kc:Vertex) should fail sh:class."""
    g = Graph()
    g.add((EX.v1, RDF.type, KC.Vertex))
    g.add((EX.other_edge, RDF.type, KC.Edge))
    g.add((EX.other_edge, KC.boundedBy, EX.v1))
    g.add((EX.other_edge, KC.boundedBy, EX.v1))  # dedup → only 1
    # The test edge: bounded by a Vertex and another Edge
    g.add((EX.e1, RDF.type, KC.Edge))
    g.add((EX.e1, KC.boundedBy, EX.v1))
    g.add((EX.e1, KC.boundedBy, EX.other_edge))  # not a Vertex
    conforms, report = _validate(g)
    assert not conforms, "Expected edge bounded by non-Vertex to fail SHACL."


# ---------------------------------------------------------------------------
# FaceShape boundary conditions
# ---------------------------------------------------------------------------

def test_face_with_four_edges_fails():
    """Face with 4 boundedBy edges should fail sh:maxCount 3."""
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3, EX.v4]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e34, EX.v3, EX.v4),
        (EX.e41, EX.v4, EX.v1),
    ]
    for e, va, vb in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.boundedBy, va))
        g.add((e, KC.boundedBy, vb))
    g.add((EX.f1, RDF.type, KC.Face))
    for e, _, _ in edges:
        g.add((EX.f1, KC.boundedBy, e))
    conforms, report = _validate(g)
    assert not conforms, "Expected 4-edge face to fail SHACL."


def test_face_bounded_by_non_edge_fails():
    """Face where boundedBy points to a kc:Vertex should fail sh:class kc:Edge."""
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3]:
        g.add((v, RDF.type, KC.Vertex))
    g.add((EX.f1, RDF.type, KC.Face))
    g.add((EX.f1, KC.boundedBy, EX.v1))
    g.add((EX.f1, KC.boundedBy, EX.v2))
    g.add((EX.f1, KC.boundedBy, EX.v3))
    conforms, report = _validate(g)
    assert not conforms, "Expected face bounded by Vertices (not Edges) to fail SHACL."


def test_face_with_duplicate_edges_fails():
    """Face with 3 boundedBy triples but only 2 distinct IRIs fails (RDF dedup → 2 triples)."""
    g = _make_valid_triangle()
    # Remove the face and re-add with a duplicate edge
    g.remove((EX.f1, KC.boundedBy, EX.e31))
    g.add((EX.f1, KC.boundedBy, EX.e12))  # duplicate — RDF dedup means only 2 distinct triples
    conforms, report = _validate(g)
    assert not conforms, "Expected face with duplicate edges (only 2 distinct) to fail SHACL."


def test_face_with_path_not_cycle_fails():
    """Three edges forming a path (v1-v2, v2-v3, v3-v4) not a cycle should fail closed-triangle."""
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3, EX.v4]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e34, EX.v3, EX.v4),  # path: 4 vertices, not a cycle
    ]
    for e, va, vb in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.boundedBy, va))
        g.add((e, KC.boundedBy, vb))
    g.add((EX.f1, RDF.type, KC.Face))
    for e, _, _ in edges:
        g.add((EX.f1, KC.boundedBy, e))
    conforms, report = _validate(g)
    assert not conforms, "Expected path-not-cycle face to fail SHACL."


# ---------------------------------------------------------------------------
# ComplexShape boundary-closure edge cases
# ---------------------------------------------------------------------------

def test_valid_complex_with_full_triangle():
    """Complex containing a full triangle (3v + 3e + 1f) should pass."""
    g = _make_valid_triangle()
    g.add((EX.cx, RDF.type, KC.Complex))
    for elem in [EX.v1, EX.v2, EX.v3, EX.e12, EX.e23, EX.e31, EX.f1]:
        g.add((EX.cx, KC.hasElement, elem))
    conforms, report = _validate(g)
    assert conforms, f"Expected valid complex with full triangle to pass.\n{report}"


def test_complex_with_face_missing_boundary_edge_fails():
    """Complex with face but one boundary edge NOT in complex should fail boundary-closure."""
    g = _make_valid_triangle()
    g.add((EX.cx, RDF.type, KC.Complex))
    # Add all elements EXCEPT e31
    for elem in [EX.v1, EX.v2, EX.v3, EX.e12, EX.e23, EX.f1]:
        g.add((EX.cx, KC.hasElement, elem))
    conforms, report = _validate(g)
    assert not conforms, "Expected complex missing a boundary edge to fail SHACL."


def test_complex_with_face_missing_all_edges_fails():
    """Complex with face but NO edges as members should fail boundary-closure."""
    g = _make_valid_triangle()
    g.add((EX.cx, RDF.type, KC.Complex))
    # Only vertices and face, no edges
    for elem in [EX.v1, EX.v2, EX.v3, EX.f1]:
        g.add((EX.cx, KC.hasElement, elem))
    conforms, report = _validate(g)
    assert not conforms, "Expected complex with face but no edge members to fail SHACL."


def test_empty_complex_passes():
    """A Complex with no hasElement triples should pass (trivially closed)."""
    g = Graph()
    g.add((EX.cx, RDF.type, KC.Complex))
    conforms, report = _validate(g)
    assert conforms, f"Expected empty complex to pass.\n{report}"


def test_complex_with_only_vertices_passes():
    """A Complex with only vertices (no edges/faces) passes — boundary trivially satisfied."""
    g = Graph()
    g.add((EX.v1, RDF.type, KC.Vertex))
    g.add((EX.v2, RDF.type, KC.Vertex))
    g.add((EX.cx, RDF.type, KC.Complex))
    g.add((EX.cx, KC.hasElement, EX.v1))
    g.add((EX.cx, KC.hasElement, EX.v2))
    conforms, report = _validate(g)
    assert conforms, f"Expected vertex-only complex to pass.\n{report}"


def test_two_faces_sharing_an_edge():
    """Two valid faces sharing one edge should both pass validation."""
    g = Graph()
    # 4 vertices forming a diamond / bowtie
    for v in [EX.v1, EX.v2, EX.v3, EX.v4]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e31, EX.v3, EX.v1),  # triangle 1: v1-v2-v3
        (EX.e24, EX.v2, EX.v4),
        (EX.e41, EX.v4, EX.v1),  # triangle 2: v1-v2-v4 (shares e12)
    ]
    for e, va, vb in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.boundedBy, va))
        g.add((e, KC.boundedBy, vb))
    # Face 1: e12, e23, e31
    g.add((EX.f1, RDF.type, KC.Face))
    g.add((EX.f1, KC.boundedBy, EX.e12))
    g.add((EX.f1, KC.boundedBy, EX.e23))
    g.add((EX.f1, KC.boundedBy, EX.e31))
    # Face 2: e12, e24, e41
    g.add((EX.f2, RDF.type, KC.Face))
    g.add((EX.f2, KC.boundedBy, EX.e12))
    g.add((EX.f2, KC.boundedBy, EX.e24))
    g.add((EX.f2, KC.boundedBy, EX.e41))
    conforms, report = _validate(g)
    assert conforms, f"Expected two faces sharing an edge to pass.\n{report}"


def test_vertex_with_spurious_bounded_by_passes():
    """A vertex with an extra boundedBy triple still passes — no shape targets Vertex for boundedBy.

    Documents a known blind spot: SHACL shapes are class-targeted. EdgeShape targets kc:Edge,
    not kc:Vertex, so spurious triples on vertices are unconstrained.
    """
    g = Graph()
    g.add((EX.v1, RDF.type, KC.Vertex))
    g.add((EX.v2, RDF.type, KC.Vertex))
    g.add((EX.v1, KC.boundedBy, EX.v2))  # spurious — vertices have empty boundary
    conforms, report = _validate(g)
    assert conforms, f"Expected vertex with spurious boundedBy to pass (no shape fires).\n{report}"