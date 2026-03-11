"""
tests/test_text_descriptor.py

Tests for the text() descriptor framework extension.
Validates TextDescriptor creation, schema generation (OWL + SHACL),
shared property domain handling, and instance attribute assertion.

Traceability: WP4.5 framework extension
"""

import pytest
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL, XSD

from kc.schema import SchemaBuilder, vocab, text, TextDescriptor, VocabDescriptor
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError

_SH = Namespace("http://www.w3.org/ns/shacl#")
_KC = Namespace("https://example.org/kc#")


# ---------------------------------------------------------------------------
# text() factory
# ---------------------------------------------------------------------------

def test_text_returns_descriptor():
    t = text()
    assert isinstance(t, TextDescriptor)
    assert t.required is True
    assert t.multiple is False


def test_text_optional():
    t = text(required=False)
    assert t.required is False
    assert t.multiple is False


def test_text_multiple():
    t = text(multiple=True)
    assert t.required is True
    assert t.multiple is True


def test_text_optional_multiple():
    t = text(required=False, multiple=True)
    assert t.required is False
    assert t.multiple is True


def test_text_repr():
    assert repr(text()) == "text()"
    assert repr(text(required=False)) == "text(required=False)"
    assert repr(text(multiple=True)) == "text(multiple=True)"
    assert repr(text(required=False, multiple=True)) == "text(required=False, multiple=True)"


def test_text_is_frozen():
    t = text()
    with pytest.raises(AttributeError):
        t.required = False


# ---------------------------------------------------------------------------
# OWL generation for text attributes
# ---------------------------------------------------------------------------

def test_text_generates_owl_datatype_property():
    """text() attribute should produce an OWL DatatypeProperty with xsd:string range."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"name": text()})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    attr = URIRef("https://example.org/ttest#name")
    assert (attr, RDF.type, OWL.DatatypeProperty) in g
    assert (attr, RDFS.range, XSD.string) in g


def test_text_no_rdfs_comment():
    """text() attribute should NOT produce an rdfs:comment (unlike vocab)."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"name": text()})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    attr = URIRef("https://example.org/ttest#name")
    comments = list(g.objects(attr, RDFS.comment))
    assert len(comments) == 0


# ---------------------------------------------------------------------------
# SHACL generation for text attributes
# ---------------------------------------------------------------------------

def _get_prop_shapes(shacl_ttl, shape_name, attr_name, ns="ttest"):
    """Parse SHACL and find property shapes for a given attr on a given shape."""
    g = Graph()
    g.parse(data=shacl_ttl, format="turtle")
    nss = Namespace(f"https://example.org/{ns}/shape#")
    ns_ = Namespace(f"https://example.org/{ns}#")
    shape_iri = nss[shape_name]
    attr_iri = ns_[attr_name]
    results = []
    for prop in g.objects(shape_iri, _SH.property):
        if (prop, _SH.path, attr_iri) in g:
            results.append((g, prop))
    return results


def test_text_required_single_shacl():
    """text() → sh:minCount 1, sh:maxCount 1, sh:datatype xsd:string, no sh:in."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"name": text()})
    shapes = _get_prop_shapes(sb.dump_shacl(), "VShape", "name")
    assert len(shapes) == 1
    g, prop = shapes[0]
    assert g.value(prop, _SH.minCount).toPython() == 1
    assert g.value(prop, _SH.maxCount).toPython() == 1
    assert g.value(prop, _SH.datatype) == XSD.string
    assert g.value(prop, _SH["in"]) is None  # no sh:in for text


def test_text_optional_single_shacl():
    """text(required=False) → sh:minCount 0, sh:maxCount 1."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"name": text(required=False)})
    shapes = _get_prop_shapes(sb.dump_shacl(), "VShape", "name")
    assert len(shapes) == 1
    g, prop = shapes[0]
    assert g.value(prop, _SH.minCount).toPython() == 0
    assert g.value(prop, _SH.maxCount).toPython() == 1


def test_text_required_multiple_shacl():
    """text(multiple=True) → sh:minCount 1, no sh:maxCount."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"tags": text(multiple=True)})
    shapes = _get_prop_shapes(sb.dump_shacl(), "VShape", "tags")
    assert len(shapes) == 1
    g, prop = shapes[0]
    assert g.value(prop, _SH.minCount).toPython() == 1
    assert g.value(prop, _SH.maxCount) is None  # unbounded


def test_text_optional_multiple_shacl():
    """text(required=False, multiple=True) → sh:minCount 0, no sh:maxCount."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"tags": text(required=False, multiple=True)})
    shapes = _get_prop_shapes(sb.dump_shacl(), "VShape", "tags")
    assert len(shapes) == 1
    g, prop = shapes[0]
    assert g.value(prop, _SH.minCount).toPython() == 0
    assert g.value(prop, _SH.maxCount) is None


# ---------------------------------------------------------------------------
# text() on all element types (vertex, edge, face)
# ---------------------------------------------------------------------------

def test_text_on_vertex_type():
    sb = SchemaBuilder(namespace="ttest")
    sb.add_vertex_type("V", attributes={"desc": text()})
    assert "desc" in sb.dump_shacl()


def test_text_on_edge_type():
    sb = SchemaBuilder(namespace="ttest")
    sb.add_edge_type("E", attributes={"desc": text()})
    assert "desc" in sb.dump_shacl()


def test_text_on_face_type():
    sb = SchemaBuilder(namespace="ttest")
    sb.add_face_type("F", attributes={"desc": text()})
    assert "desc" in sb.dump_shacl()


# ---------------------------------------------------------------------------
# Mixed vocab + text attributes
# ---------------------------------------------------------------------------

def test_mixed_vocab_and_text():
    """A type can have both vocab and text attributes."""
    sb = SchemaBuilder(namespace="ttest")
    sb.add_edge_type("E", attributes={
        "kind": vocab("a", "b"),
        "notes": text(required=False),
    })
    shacl = sb.dump_shacl()
    assert "kind" in shacl
    assert "notes" in shacl
    # vocab attr has sh:in, text attr doesn't
    owl = sb.dump_owl()
    assert "Allowed values: a, b" in owl


# ---------------------------------------------------------------------------
# Shared property names across types (domain handling)
# ---------------------------------------------------------------------------

def test_shared_property_no_domain_in_owl():
    """When the same property name appears on multiple types, rdfs:domain is omitted."""
    sb = SchemaBuilder(namespace="shared")
    sb.add_vertex_type("V", attributes={"desc": text()})
    sb.add_edge_type("E", attributes={"desc": text()})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    attr = URIRef("https://example.org/shared#desc")
    domains = list(g.objects(attr, RDFS.domain))
    assert len(domains) == 0, f"Shared property should have no domain, found: {domains}"


def test_unique_property_has_domain_in_owl():
    """When a property name is unique to one type, rdfs:domain is set."""
    sb = SchemaBuilder(namespace="unique")
    sb.add_vertex_type("V", attributes={"color_name": text()})
    sb.add_edge_type("E", attributes={"weight": text()})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    cn = URIRef("https://example.org/unique#color_name")
    wt = URIRef("https://example.org/unique#weight")
    assert list(g.objects(cn, RDFS.domain)) == [URIRef("https://example.org/unique#V")]
    assert list(g.objects(wt, RDFS.domain)) == [URIRef("https://example.org/unique#E")]


def test_shared_property_three_types_no_domain():
    """Property shared across all three simplex types has no rdfs:domain."""
    sb = SchemaBuilder(namespace="tri")
    sb.add_vertex_type("V", attributes={"note": text()})
    sb.add_edge_type("E", attributes={"note": text()})
    sb.add_face_type("F", attributes={"note": text()})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    attr = URIRef("https://example.org/tri#note")
    assert len(list(g.objects(attr, RDFS.domain))) == 0


def test_shared_property_shacl_per_type():
    """Even with no OWL domain, each type's SHACL shape has its own property constraint."""
    sb = SchemaBuilder(namespace="shp")
    sb.add_vertex_type("V", attributes={"note": text()})
    sb.add_edge_type("E", attributes={"note": text(required=False)})
    v_shapes = _get_prop_shapes(sb.dump_shacl(), "VShape", "note", ns="shp")
    e_shapes = _get_prop_shapes(sb.dump_shacl(), "EShape", "note", ns="shp")
    assert len(v_shapes) == 1
    assert len(e_shapes) == 1
    # V's note is required, E's is optional
    g_v, prop_v = v_shapes[0]
    g_e, prop_e = e_shapes[0]
    assert g_v.value(prop_v, _SH.minCount).toPython() == 1
    assert g_e.value(prop_e, _SH.minCount).toPython() == 0


# ---------------------------------------------------------------------------
# Shared property does not cause cross-type SHACL violations
# ---------------------------------------------------------------------------

def test_shared_text_no_cross_type_validation_failure():
    """Adding a vertex with a shared text attr should not fail edge/face SHACL checks."""
    sb = SchemaBuilder(namespace="cross")
    sb.add_vertex_type("V", attributes={"desc": text()})
    sb.add_edge_type("E", attributes={
        "desc": text(),
        "kind": vocab("a"),
    })
    kc = KnowledgeComplex(schema=sb)
    # This should succeed — vertex has desc but shouldn't trigger EdgeShape's kind constraint
    kc.add_vertex("v1", type="V", desc="hello")


# ---------------------------------------------------------------------------
# Instance assertion: list values for text(multiple=True)
# ---------------------------------------------------------------------------

def test_multiple_text_values_asserted():
    """text(multiple=True) attribute accepts a list and asserts multiple triples."""
    sb = SchemaBuilder(namespace="multi")
    sb.add_vertex_type("V", attributes={"tags": text(multiple=True)})
    kc = KnowledgeComplex(schema=sb)
    kc.add_vertex("v1", type="V", tags=["alpha", "beta", "gamma"])
    ttl = kc.dump_graph()
    assert "alpha" in ttl
    assert "beta" in ttl
    assert "gamma" in ttl


def test_single_text_value_asserted():
    """text() attribute accepts a single string value."""
    sb = SchemaBuilder(namespace="single")
    sb.add_vertex_type("V", attributes={"name": text()})
    kc = KnowledgeComplex(schema=sb)
    kc.add_vertex("v1", type="V", name="test_value")
    ttl = kc.dump_graph()
    assert "test_value" in ttl


# ---------------------------------------------------------------------------
# dict-style text attribute spec
# ---------------------------------------------------------------------------

def test_text_via_dict_spec():
    """text() can be passed via dict with 'text' key for consistency with vocab dict style."""
    sb = SchemaBuilder(namespace="dtest")
    sb.add_edge_type("E", attributes={
        "notes": {"text": text(required=False)},
    })
    shapes = _get_prop_shapes(sb.dump_shacl(), "EShape", "notes", ns="dtest")
    assert len(shapes) == 1
    g, prop = shapes[0]
    assert g.value(prop, _SH.minCount).toPython() == 0


# ---------------------------------------------------------------------------
# promote_to_attribute with text descriptor
# ---------------------------------------------------------------------------

def test_promote_with_text_descriptor():
    """promote_to_attribute can use a text descriptor instead of vocab."""
    sb = SchemaBuilder(namespace="promo")
    sb.add_face_type("F")
    owl_before = sb.dump_owl()
    shacl_before = sb.dump_shacl()

    sb.promote_to_attribute("F", "notes", text=text(), required=True)

    owl_after = sb.dump_owl()
    shacl_after = sb.dump_shacl()
    assert owl_before != owl_after
    assert shacl_before != shacl_after
    assert "notes" in owl_after
    assert "notes" in shacl_after


# ===========================================================================
# Regression tests — bugs found and fixed during WP4.5 implementation
# ===========================================================================

def test_regression_shared_domain_not_reasserted_after_removal():
    """Regression: when property 'p' appears on types A, B, C, the domain must be
    removed on B and must NOT be re-added on C.

    Bug: _set_owl_domain removed domain on second type but re-added it on third
    (because the property was already declared as DatatypeProperty, so the
    'already_declared' check was True but domain list was empty).
    """
    sb = SchemaBuilder(namespace="regr1")
    sb.add_vertex_type("A", attributes={"shared": text()})
    sb.add_edge_type("B", attributes={"shared": text()})
    sb.add_face_type("C", attributes={"shared": text()})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    attr = URIRef("https://example.org/regr1#shared")
    domains = list(g.objects(attr, RDFS.domain))
    assert len(domains) == 0, (
        f"Shared property should have no domain after 3 types, found: {domains}"
    )


def test_regression_shared_vocab_domain_not_reasserted():
    """Same regression test but with vocab() attributes — the shared-domain bug
    applied to both text and vocab descriptors."""
    sb = SchemaBuilder(namespace="regr2")
    sb.add_vertex_type("A", attributes={"kind": vocab("x")})
    sb.add_edge_type("B", attributes={"kind": vocab("y")})
    g = Graph()
    g.parse(data=sb.dump_owl(), format="turtle")
    attr = URIRef("https://example.org/regr2#kind")
    domains = list(g.objects(attr, RDFS.domain))
    assert len(domains) == 0


def test_regression_shared_property_cross_type_shacl_three_types():
    """Regression: shared property across vertex + edge + face must not cause
    SHACL cross-type violations. This is the exact scenario that failed in the
    MTG demo (persona shared across Color, ColorPair, ColorTriple).

    The validation adds a vertex with the shared attr and checks that no
    edge/face SHACL shapes fire on it.
    """
    sb = SchemaBuilder(namespace="regr3")
    sb.add_vertex_type("V", attributes={
        "persona": text(),
        "v_only": vocab("x"),
    })
    sb.add_edge_type("E", attributes={
        "persona": text(),
        "e_only": vocab("a", "b"),
    })
    sb.add_face_type("F", attributes={
        "persona": text(),
        "f_only": vocab("p", "q"),
    })
    kc = KnowledgeComplex(schema=sb)
    # Vertex should validate successfully — persona should NOT trigger
    # EdgeShape's e_only constraint or FaceShape's f_only/boundedBy constraints
    kc.add_vertex("v1", type="V", persona="test", v_only="x")


def test_regression_mtg_full_instance_validates():
    """Regression: the full MTG demo instance (5 vertices + 10 edges + 10 faces)
    must build without SHACL validation failures. This catches the domain inference
    bug that caused mtg:White to be classified as a ColorTriple."""
    from demo.demo_instance import build_mtg_instance
    kc = build_mtg_instance()
    # If we get here without ValidationError, the instance is valid
    ttl = kc.dump_graph()
    assert "White" in ttl
    assert "esper" in ttl  # clan on WUB face
