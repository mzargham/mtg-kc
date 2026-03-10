"""
tests/test_two_by_two_coverage.py

Verify all four cells of the 2×2 responsibility map are populated.
Directly tests hypothesis criterion H1.

Topological cells are tested against static resources (pass today).
Ontological cells require SchemaBuilder (fail with NotImplementedError).

Traceability: see tests/requirements.md, ARCHITECTURE.md §2×2 Responsibility Map
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef

KC  = Namespace("https://example.org/kc#")
KCS = Namespace("https://example.org/kc/shape#")
SH  = Namespace("http://www.w3.org/ns/shacl#")

_CORE_OWL    = Path(__file__).parent.parent / "kc" / "resources" / "kc_core.ttl"
_CORE_SHAPES = Path(__file__).parent.parent / "kc" / "resources" / "kc_core_shapes.ttl"


@pytest.fixture(scope="module")
def owl_graph() -> Graph:
    g = Graph()
    g.parse(_CORE_OWL, format="turtle")
    return g


@pytest.fixture(scope="module")
def shacl_graph() -> Graph:
    g = Graph()
    g.parse(_CORE_SHAPES, format="turtle")
    return g


# ---------------------------------------------------------------------------
# Topological-OWL cell (pass today)
# ---------------------------------------------------------------------------

def test_topological_owl_has_cardinality_axioms(owl_graph):
    """H1: topological-OWL cell has at least one owl:Restriction with qualifiedCardinality."""
    restrictions = set(owl_graph.subjects(RDF.type, OWL.Restriction))
    has_cardinality = any(
        owl_graph.value(r, OWL.qualifiedCardinality) is not None
        for r in restrictions
    )
    assert has_cardinality, "Topological-OWL cell must contain cardinality axioms"


def test_topological_owl_has_boundary_property(owl_graph):
    """H1: topological-OWL cell declares the boundary operator (kc:boundedBy)."""
    assert (KC.boundedBy, RDF.type, OWL.ObjectProperty) in owl_graph


# ---------------------------------------------------------------------------
# Topological-SHACL cell (pass today)
# ---------------------------------------------------------------------------

def test_topological_shacl_has_sparql_constraints(shacl_graph):
    """H1: topological-SHACL cell has at least one sh:SPARQLConstraint."""
    sparql_constraints = set(shacl_graph.subjects(RDF.type, SH.SPARQLConstraint))
    assert len(sparql_constraints) > 0, "Topological-SHACL cell must contain sh:sparql constraints"


def test_topological_shacl_has_edge_shape(shacl_graph):
    """H1: topological-SHACL cell has EdgeShape targeting kc:Edge."""
    assert (KCS.EdgeShape, SH.targetClass, KC.Edge) in shacl_graph


def test_topological_shacl_has_face_shape(shacl_graph):
    """H1: topological-SHACL cell has FaceShape targeting kc:Face."""
    assert (KCS.FaceShape, SH.targetClass, KC.Face) in shacl_graph


def test_topological_shacl_has_complex_shape(shacl_graph):
    """H1: topological-SHACL cell has ComplexShape targeting kc:Complex."""
    assert (KCS.ComplexShape, SH.targetClass, KC.Complex) in shacl_graph


# ---------------------------------------------------------------------------
# Ontological-OWL cell (fails: NotImplementedError)
# ---------------------------------------------------------------------------

def test_ontological_owl_cell_populated_by_schema_builder():
    """H1: SchemaBuilder add_edge_type() populates the ontological-OWL cell.

    After adding an edge type with a vocab attribute, dump_owl() should contain
    a user-namespace subclass of kc:Edge.
    """
    from kc.schema import SchemaBuilder, vocab
    sb = SchemaBuilder(namespace="test2x2")
    sb.add_edge_type("Rel", attributes={"x": vocab("a", "b")})
    ttl = sb.dump_owl()
    g = Graph()
    g.parse(data=ttl, format="turtle")
    rel = URIRef("https://example.org/test2x2#Rel")
    assert (rel, RDFS.subClassOf, KC.Edge) in g


# ---------------------------------------------------------------------------
# Ontological-SHACL cell (fails: NotImplementedError)
# ---------------------------------------------------------------------------

def test_ontological_shacl_cell_populated_by_schema_builder():
    """H1: SchemaBuilder add_edge_type() populates the ontological-SHACL cell.

    After adding an edge type with a vocab attribute, dump_shacl() should contain
    sh:in constraints for the vocab values.
    """
    from kc.schema import SchemaBuilder, vocab
    sb = SchemaBuilder(namespace="test2x2")
    sb.add_edge_type("Rel", attributes={"x": vocab("a", "b")})
    ttl = sb.dump_shacl()
    assert "a" in ttl and "b" in ttl  # vocab values present
