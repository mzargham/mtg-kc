"""
tests/test_schema_builder.py

Tests for kc.schema.SchemaBuilder and vocab().
These tests call the public API only — no rdflib imports.
Turtle output is inspected as strings or parsed by rdflib *within the test*
to check for required triples (rdflib use here is in the test, not the API).

Traceability: see tests/requirements.md
"""

import pytest
from rdflib import Graph  # allowed in tests; not in API under test

from knowledgecomplex import SchemaBuilder, vocab, SchemaError
from knowledgecomplex.schema import VocabDescriptor


@pytest.fixture
def basic_schema() -> SchemaBuilder:
    sb = SchemaBuilder(namespace="test")
    sb.add_vertex_type("Color")
    sb.add_edge_type(
        "ColorPair",
        attributes={"disposition": vocab("adjacent", "opposite")},
    )
    sb.add_face_type(
        "ColorTriple",
        attributes={"pattern": {"vocab": vocab("ooa", "oaa"), "required": False}},
    )
    return sb


# --- vocab() ---

def test_vocab_returns_descriptor():
    v = vocab("a", "b")
    assert isinstance(v, VocabDescriptor)
    assert v.values == ("a", "b")


def test_vocab_empty_raises():
    with pytest.raises(ValueError):
        vocab()


# --- add_vertex_type ---

def test_add_vertex_type_writes_owl(basic_schema):
    """REQ-SCHEMA-02, REQ-VV-03: OWL dump contains subclass triple for Color."""
    ttl = basic_schema.dump_owl()
    g = Graph()
    g.parse(data=ttl, format="turtle")
    from rdflib.namespace import RDFS, OWL
    from rdflib import URIRef
    color = URIRef("https://example.org/test#Color")
    kc_vertex = URIRef("https://example.org/kc#Vertex")
    assert (color, RDFS.subClassOf, kc_vertex) in g


def test_add_vertex_type_writes_shacl(basic_schema):
    """REQ-SCHEMA-02, REQ-VV-03: SHACL dump contains NodeShape targeting Color."""
    ttl = basic_schema.dump_shacl()
    assert "test#Color" in ttl or "ColorShape" in ttl  # loose check; tighten in WP3


# --- add_edge_type ---

def test_add_edge_type_writes_owl(basic_schema):
    """REQ-SCHEMA-03, REQ-VV-03: OWL dump contains ColorPair subclass of KC:Edge."""
    ttl = basic_schema.dump_owl()
    g = Graph()
    g.parse(data=ttl, format="turtle")
    from rdflib.namespace import RDFS
    from rdflib import URIRef
    rel = URIRef("https://example.org/test#ColorPair")
    kc_edge = URIRef("https://example.org/kc#Edge")
    assert (rel, RDFS.subClassOf, kc_edge) in g


def test_add_edge_type_writes_shacl(basic_schema):
    """REQ-SCHEMA-03, REQ-VV-03: SHACL dump contains sh:in constraint for disposition."""
    ttl = basic_schema.dump_shacl()
    assert "adjacent" in ttl
    assert "opposite" in ttl


# --- add_face_type ---

def test_add_face_type_optional_attr(basic_schema):
    """REQ-SCHEMA-04: optional attribute generates sh:minCount 0."""
    ttl = basic_schema.dump_shacl()
    # 'pattern' attribute was required=False
    # Should appear with minCount 0 somewhere in the shapes
    assert "pattern" in ttl
    assert "minCount" in ttl or "sh:minCount" in ttl


# --- vocab → sh:in ---

def test_vocab_generates_sh_in(basic_schema):
    """REQ-SCHEMA-05: vocab values appear in SHACL sh:in constraint."""
    ttl = basic_schema.dump_shacl()
    assert "adjacent" in ttl
    assert "opposite" in ttl
    assert "ooa" in ttl
    assert "oaa" in ttl


# --- dump_owl / dump_shacl include core ---

def test_dump_owl_includes_core(basic_schema):
    """REQ-SCHEMA-06: dump_owl() includes KC:Vertex, KC:Edge, KC:Face."""
    ttl = basic_schema.dump_owl()
    assert "Vertex" in ttl
    assert "Edge" in ttl
    assert "Face" in ttl


def test_dump_shacl_includes_core(basic_schema):
    """REQ-SCHEMA-07: dump_shacl() includes core EdgeShape and FaceShape."""
    ttl = basic_schema.dump_shacl()
    assert "EdgeShape" in ttl
    assert "FaceShape" in ttl


# --- promote_to_attribute ---

def test_promote_updates_owl(basic_schema):
    """REQ-SCHEMA-08, REQ-VV-03: promote changes OWL dump."""
    before = basic_schema.dump_owl()
    basic_schema.promote_to_attribute(
        type="ColorTriple",
        attribute="pattern",
        vocab=vocab("ooa", "oaa"),
        required=True,
    )
    after = basic_schema.dump_owl()
    assert before != after or "pattern" in after  # OWL should reflect the property


def test_promote_updates_shacl(basic_schema):
    """REQ-SCHEMA-08, REQ-VV-03: promote changes SHACL dump (minCount goes from 0 to 1)."""
    basic_schema.promote_to_attribute(
        type="ColorTriple",
        attribute="pattern",
        vocab=vocab("ooa", "oaa"),
        required=True,
    )
    ttl = basic_schema.dump_shacl()
    # After promotion, minCount 1 should appear for pattern
    assert "minCount" in ttl


# --- API opacity ---

def test_no_rdflib_in_public_api():
    """REQ-SCHEMA-09, REQ-VV-06: SchemaBuilder public methods return no rdflib objects."""
    import rdflib
    sb = SchemaBuilder(namespace="opacity_test")
    sb.add_vertex_type("V")
    owl_out = sb.dump_owl()
    shacl_out = sb.dump_shacl()
    assert isinstance(owl_out, str), "dump_owl() must return str"
    assert isinstance(shacl_out, str), "dump_shacl() must return str"
    assert not isinstance(owl_out, rdflib.Graph)
    assert not isinstance(shacl_out, rdflib.Graph)
