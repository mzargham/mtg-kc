"""
tests/test_core_owl.py

Tests for kc/resources/kc_core.ttl (abstract OWL ontology).
All tests operate on the raw Turtle file via rdflib — these tests are allowed
to use rdflib directly since they are testing the static resource, not the package API.

Traceability: see tests/requirements.md
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL

KC = Namespace("https://example.org/kc#")
_CORE_OWL = Path(__file__).parent.parent / "kc" / "resources" / "kc_core.ttl"


@pytest.fixture(scope="module")
def core_owl() -> Graph:
    g = Graph()
    g.parse(_CORE_OWL, format="turtle")
    return g


def test_core_owl_is_valid_turtle(core_owl):
    """REQ-CORE-06: core OWL file parses without error."""
    assert len(core_owl) > 0


def test_core_classes_exist(core_owl):
    """REQ-CORE-01: KC:Vertex, KC:Edge, KC:Face are declared as owl:Class."""
    for cls in [KC.Vertex, KC.Edge, KC.Face]:
        assert (cls, RDF.type, OWL.Class) in core_owl, f"Missing class: {cls}"


def test_edge_cardinality_axioms(core_owl):
    """REQ-CORE-02: KC:Edge has cardinality restrictions on hasSource and hasTarget."""
    # Check that there exist blank node restrictions on kc:Edge for hasSource and hasTarget
    restrictions = set(core_owl.subjects(RDF.type, OWL.Restriction))
    source_restricted = any(
        (r, OWL.onProperty, KC.hasSource) in core_owl for r in restrictions
    )
    target_restricted = any(
        (r, OWL.onProperty, KC.hasTarget) in core_owl for r in restrictions
    )
    assert source_restricted, "No cardinality restriction on kc:hasSource"
    assert target_restricted, "No cardinality restriction on kc:hasTarget"


def test_face_cardinality_axioms(core_owl):
    """REQ-CORE-03: KC:Face has cardinality restriction on hasEdge."""
    restrictions = set(core_owl.subjects(RDF.type, OWL.Restriction))
    edge_restricted = any(
        (r, OWL.onProperty, KC.hasEdge) in core_owl for r in restrictions
    )
    assert edge_restricted, "No cardinality restriction on kc:hasEdge"
