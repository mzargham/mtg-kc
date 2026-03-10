"""
tests/test_core_owl_extended.py

Extended tests for kc/resources/kc_core.ttl — OWL ontology completeness.
All tests operate on the raw Turtle file via rdflib.

These go beyond test_core_owl.py to verify structural properties,
exact cardinality values, and guard against scope creep.

Traceability: see tests/requirements.md
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef

KC = Namespace("https://example.org/kc#")
_CORE_OWL = Path(__file__).parent.parent / "kc" / "resources" / "kc_core.ttl"


@pytest.fixture(scope="module")
def core_owl() -> Graph:
    g = Graph()
    g.parse(_CORE_OWL, format="turtle")
    return g


# --- Ontology header ---

def test_ontology_header_exists(core_owl):
    """The ontology IRI is declared as owl:Ontology with label and comment."""
    ont = URIRef("https://example.org/kc")
    assert (ont, RDF.type, OWL.Ontology) in core_owl, "Missing owl:Ontology declaration"
    assert (ont, RDFS.label, None) in core_owl or any(
        core_owl.triples((ont, RDFS.label, None))
    ), "Ontology missing rdfs:label"
    assert any(
        core_owl.triples((ont, RDFS.comment, None))
    ), "Ontology missing rdfs:comment"


# --- Property type declarations ---

def test_bounded_by_is_object_property(core_owl):
    """kc:boundedBy must be declared as owl:ObjectProperty."""
    assert (KC.boundedBy, RDF.type, OWL.ObjectProperty) in core_owl


# --- Vertex has no cardinality restriction ---

def test_vertex_has_no_cardinality_restriction(core_owl):
    """Vertex (0-simplex) has empty boundary — no cardinality restriction on boundedBy."""
    restrictions = set(core_owl.subjects(RDF.type, OWL.Restriction))
    vertex_has_restriction = any(
        (r, OWL.onProperty, KC.boundedBy) in core_owl
        and (KC.Vertex, RDFS.subClassOf, r) in core_owl
        for r in restrictions
    )
    assert not vertex_has_restriction, (
        "KC:Vertex should NOT have a cardinality restriction on boundedBy"
    )


# --- Exact cardinality values ---

def test_edge_cardinality_is_exactly_two(core_owl):
    """Edge cardinality restriction is qualifiedCardinality=2 on kc:Vertex."""
    restrictions = set(core_owl.subjects(RDF.type, OWL.Restriction))
    for r in restrictions:
        if (r, OWL.onProperty, KC.boundedBy) in core_owl and \
           (KC.Edge, RDFS.subClassOf, r) in core_owl:
            cardinality = core_owl.value(r, OWL.qualifiedCardinality)
            on_class = core_owl.value(r, OWL.onClass)
            assert cardinality is not None, "Edge restriction missing qualifiedCardinality"
            assert int(cardinality) == 2, f"Edge cardinality should be 2, got {cardinality}"
            assert on_class == KC.Vertex, f"Edge restriction should be on Vertex, got {on_class}"
            return
    pytest.fail("No cardinality restriction found on Edge for boundedBy")


def test_face_cardinality_is_exactly_three(core_owl):
    """Face cardinality restriction is qualifiedCardinality=3 on kc:Edge."""
    restrictions = set(core_owl.subjects(RDF.type, OWL.Restriction))
    for r in restrictions:
        if (r, OWL.onProperty, KC.boundedBy) in core_owl and \
           (KC.Face, RDFS.subClassOf, r) in core_owl:
            cardinality = core_owl.value(r, OWL.qualifiedCardinality)
            on_class = core_owl.value(r, OWL.onClass)
            assert cardinality is not None, "Face restriction missing qualifiedCardinality"
            assert int(cardinality) == 3, f"Face cardinality should be 3, got {cardinality}"
            assert on_class == KC.Edge, f"Face restriction should be on Edge, got {on_class}"
            return
    pytest.fail("No cardinality restriction found on Face for boundedBy")


# --- Structural invariants ---

def test_complex_is_not_subclass_of_element(core_owl):
    """Complex is a container, not a simplex — it must NOT be a subclass of Element."""
    assert (KC.Complex, RDFS.subClassOf, KC.Element) not in core_owl


def test_element_has_no_kc_superclass(core_owl):
    """Element is the root — no kc-namespace superclass."""
    for _, _, parent in core_owl.triples((KC.Element, RDFS.subClassOf, None)):
        assert not str(parent).startswith("https://example.org/kc#"), (
            f"KC:Element should not have a kc-namespace superclass, found {parent}"
        )


# --- Documentation completeness ---

def test_all_classes_have_labels(core_owl):
    """Every owl:Class in the ontology should have an rdfs:label."""
    classes = set(core_owl.subjects(RDF.type, OWL.Class))
    for cls in classes:
        if isinstance(cls, URIRef) and str(cls).startswith("https://example.org/kc#"):
            labels = list(core_owl.triples((cls, RDFS.label, None)))
            assert len(labels) > 0, f"Class {cls} is missing rdfs:label"


def test_all_properties_have_labels(core_owl):
    """Every owl:ObjectProperty should have an rdfs:label."""
    props = set(core_owl.subjects(RDF.type, OWL.ObjectProperty))
    for prop in props:
        if isinstance(prop, URIRef) and str(prop).startswith("https://example.org/kc#"):
            labels = list(core_owl.triples((prop, RDFS.label, None)))
            assert len(labels) > 0, f"Property {prop} is missing rdfs:label"


# --- Scope guards ---

def test_exactly_five_named_classes(core_owl):
    """Core ontology should contain exactly 5 named classes: Element, Vertex, Edge, Face, Complex."""
    expected = {KC.Element, KC.Vertex, KC.Edge, KC.Face, KC.Complex}
    actual = {
        s for s in core_owl.subjects(RDF.type, OWL.Class)
        if isinstance(s, URIRef) and str(s).startswith("https://example.org/kc#")
    }
    assert actual == expected, f"Expected classes {expected}, got {actual}"


def test_exactly_two_object_properties(core_owl):
    """Core ontology should contain exactly 2 object properties: boundedBy, hasElement."""
    expected = {KC.boundedBy, KC.hasElement}
    actual = {
        s for s in core_owl.subjects(RDF.type, OWL.ObjectProperty)
        if isinstance(s, URIRef) and str(s).startswith("https://example.org/kc#")
    }
    assert actual == expected, f"Expected properties {expected}, got {actual}"
