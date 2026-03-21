"""
tests/test_schema_builder_contract.py

Tests for SchemaBuilder API contract properties beyond the existing tests.
All tests will fail with NotImplementedError since WP3 is stubbed — this is
informative, creating a concrete implementation checklist.

Traceability: see tests/requirements.md
"""

import pytest
from rdflib import Graph, Namespace, RDFS, OWL, URIRef

from knowledgecomplex import SchemaBuilder, vocab, SchemaError
from knowledgecomplex.schema import VocabDescriptor

KC = Namespace("https://example.org/kc#")


# ---------------------------------------------------------------------------
# Method chaining
# ---------------------------------------------------------------------------

def test_add_vertex_type_returns_self():
    """add_vertex_type() should return the SchemaBuilder instance for chaining."""
    sb = SchemaBuilder(namespace="chain")
    result = sb.add_vertex_type("V")
    assert result is sb


def test_add_edge_type_returns_self():
    """add_edge_type() should return the SchemaBuilder instance for chaining."""
    sb = SchemaBuilder(namespace="chain")
    result = sb.add_edge_type("E")
    assert result is sb


def test_add_face_type_returns_self():
    """add_face_type() should return the SchemaBuilder instance for chaining."""
    sb = SchemaBuilder(namespace="chain")
    result = sb.add_face_type("F")
    assert result is sb


def test_promote_to_attribute_returns_self():
    """promote_to_attribute() should return the SchemaBuilder instance for chaining."""
    sb = SchemaBuilder(namespace="chain")
    sb.add_face_type("F", attributes={"x": {"vocab": vocab("a"), "required": False}})
    result = sb.promote_to_attribute("F", "x", vocab("a", "b"), required=True)
    assert result is sb


def test_chaining_all_methods():
    """All add_*_type methods should chain in a single expression."""
    sb = SchemaBuilder(namespace="chain")
    result = (
        sb.add_vertex_type("V")
          .add_edge_type("E", attributes={"x": vocab("a")})
          .add_face_type("F")
    )
    assert result is sb


# ---------------------------------------------------------------------------
# Namespace isolation
# ---------------------------------------------------------------------------

def test_namespace_isolation():
    """Two SchemaBuilders with different namespaces should produce distinct IRIs."""
    sb1 = SchemaBuilder(namespace="ns1")
    sb1.add_vertex_type("X")
    sb2 = SchemaBuilder(namespace="ns2")
    sb2.add_vertex_type("X")

    g1 = Graph()
    g1.parse(data=sb1.dump_owl(), format="turtle")
    g2 = Graph()
    g2.parse(data=sb2.dump_owl(), format="turtle")

    x_ns1 = URIRef("https://example.org/ns1#X")
    x_ns2 = URIRef("https://example.org/ns2#X")
    assert (x_ns1, RDFS.subClassOf, KC.Vertex) in g1
    assert (x_ns2, RDFS.subClassOf, KC.Vertex) in g2
    # Cross-namespace should NOT appear
    assert (x_ns2, RDFS.subClassOf, KC.Vertex) not in g1
    assert (x_ns1, RDFS.subClassOf, KC.Vertex) not in g2


# ---------------------------------------------------------------------------
# Duplicate type names
# ---------------------------------------------------------------------------

def test_duplicate_vertex_type_name_raises():
    """Calling add_vertex_type() twice with the same name should raise SchemaError."""
    sb = SchemaBuilder(namespace="dup")
    sb.add_vertex_type("Color")
    with pytest.raises(SchemaError):
        sb.add_vertex_type("Color")


def test_duplicate_edge_type_name_raises():
    """Calling add_edge_type() twice with the same name should raise SchemaError."""
    sb = SchemaBuilder(namespace="dup")
    sb.add_edge_type("Rel")
    with pytest.raises(SchemaError):
        sb.add_edge_type("Rel")


# ---------------------------------------------------------------------------
# Types without attributes
# ---------------------------------------------------------------------------

def test_add_edge_type_without_attributes():
    """add_edge_type() with no attributes kwarg should still produce a valid schema."""
    sb = SchemaBuilder(namespace="bare")
    sb.add_edge_type("BareEdge")
    owl_ttl = sb.dump_owl()
    g = Graph()
    g.parse(data=owl_ttl, format="turtle")
    bare = URIRef("https://example.org/bare#BareEdge")
    assert (bare, RDFS.subClassOf, KC.Edge) in g


def test_add_face_type_without_attributes():
    """add_face_type() with no attributes should still produce a valid schema."""
    sb = SchemaBuilder(namespace="bare")
    sb.add_face_type("BareFace")
    owl_ttl = sb.dump_owl()
    g = Graph()
    g.parse(data=owl_ttl, format="turtle")
    bare = URIRef("https://example.org/bare#BareFace")
    assert (bare, RDFS.subClassOf, KC.Face) in g


# ---------------------------------------------------------------------------
# Type registry
# ---------------------------------------------------------------------------

def test_type_registry_contains_registered_types():
    """_types should contain entries for all registered types."""
    sb = SchemaBuilder(namespace="reg")
    sb.add_vertex_type("Color")
    sb.add_edge_type("Rel")
    sb.add_face_type("Tri")
    assert "Color" in sb._types
    assert "Rel" in sb._types
    assert "Tri" in sb._types


# ---------------------------------------------------------------------------
# promote_to_attribute error paths
# ---------------------------------------------------------------------------

def test_promote_on_unregistered_type_raises():
    """promote_to_attribute on an unregistered type should raise SchemaError."""
    sb = SchemaBuilder(namespace="promo")
    sb.add_vertex_type("V")
    with pytest.raises(SchemaError):
        sb.promote_to_attribute("NonExistent", "attr", vocab("a"), required=True)


def test_promote_on_vertex_type_succeeds():
    """Vertex attributes are valid (e.g. Color.hex_code) — promote should work on vertex types."""
    sb = SchemaBuilder(namespace="promo")
    sb.add_vertex_type("V")
    result = sb.promote_to_attribute("V", "attr", vocab("a", "b"), required=True)
    assert result is sb
    # Verify the attribute appears in both dumps
    assert "attr" in sb.dump_owl()
    assert "attr" in sb.dump_shacl()


# ---------------------------------------------------------------------------
# Dump output validity
# ---------------------------------------------------------------------------

def test_dump_owl_is_valid_turtle():
    """dump_owl() should return a string parseable as Turtle."""
    sb = SchemaBuilder(namespace="valid")
    sb.add_vertex_type("V")
    ttl = sb.dump_owl()
    assert isinstance(ttl, str)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    assert len(g) > 0


def test_dump_shacl_is_valid_turtle():
    """dump_shacl() should return a string parseable as Turtle."""
    sb = SchemaBuilder(namespace="valid")
    sb.add_vertex_type("V")
    ttl = sb.dump_shacl()
    assert isinstance(ttl, str)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    assert len(g) > 0


def test_dump_owl_preserves_core_ontology_header():
    """The merged OWL should still contain the core ontology header."""
    sb = SchemaBuilder(namespace="hdr")
    sb.add_vertex_type("V")
    ttl = sb.dump_owl()
    g = Graph()
    g.parse(data=ttl, format="turtle")
    ont = URIRef("https://example.org/kc")
    assert (ont, RDF.type, OWL.Ontology) in g


# Need RDF import for the last test
from rdflib import RDF
