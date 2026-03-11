"""
tests/test_text_descriptor.py

Tests for the text() descriptor framework extension (WP4.5).
Covers: factory, repr, frozen, OWL/SHACL generation, shared domain handling,
list value assertion, dict-style spec, promote with text, regression tests.

Traceability: WP4.5 worklog, ARCHITECTURE.md
"""

import pytest
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, URIRef

from kc.schema import SchemaBuilder, vocab, text, TextDescriptor, VocabDescriptor
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError

_SH = Namespace("http://www.w3.org/ns/shacl#")


# ---------------------------------------------------------------------------
# text() factory and TextDescriptor basics
# ---------------------------------------------------------------------------

class TestTextFactory:
    def test_text_returns_text_descriptor(self):
        td = text()
        assert isinstance(td, TextDescriptor)

    def test_text_defaults(self):
        td = text()
        assert td.required is True
        assert td.multiple is False

    def test_text_required_false(self):
        td = text(required=False)
        assert td.required is False
        assert td.multiple is False

    def test_text_multiple_true(self):
        td = text(multiple=True)
        assert td.required is True
        assert td.multiple is True

    def test_text_both_flags(self):
        td = text(required=False, multiple=True)
        assert td.required is False
        assert td.multiple is True

    def test_text_repr_default(self):
        assert repr(text()) == "text()"

    def test_text_repr_required_false(self):
        assert repr(text(required=False)) == "text(required=False)"

    def test_text_repr_multiple(self):
        assert repr(text(multiple=True)) == "text(multiple=True)"

    def test_text_repr_both(self):
        assert repr(text(required=False, multiple=True)) == "text(required=False, multiple=True)"

    def test_text_descriptor_frozen(self):
        td = text()
        with pytest.raises(AttributeError):
            td.required = False


# ---------------------------------------------------------------------------
# OWL generation for text attributes
# ---------------------------------------------------------------------------

class TestTextOWL:
    def _build_and_parse_owl(self, **kwargs):
        sb = SchemaBuilder(namespace="towl")
        sb.add_vertex_type("Thing", attributes={"desc": text(**kwargs)})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        return g, Namespace("https://example.org/towl#")

    def test_text_generates_datatype_property(self):
        g, ns = self._build_and_parse_owl()
        assert (ns.desc, RDF.type, OWL.DatatypeProperty) in g

    def test_text_has_string_range(self):
        g, ns = self._build_and_parse_owl()
        assert (ns.desc, RDFS.range, XSD.string) in g

    def test_text_has_domain_for_single_type(self):
        g, ns = self._build_and_parse_owl()
        assert (ns.desc, RDFS.domain, ns.Thing) in g

    def test_text_no_rdfs_comment(self):
        """text() should NOT generate rdfs:comment (unlike vocab())."""
        g, ns = self._build_and_parse_owl()
        comments = list(g.objects(ns.desc, RDFS.comment))
        assert len(comments) == 0


# ---------------------------------------------------------------------------
# SHACL generation for text attributes — all 4 required×multiple combos
# ---------------------------------------------------------------------------

class TestTextSHACL:
    def _get_prop_shape(self, attr_name="desc", **text_kwargs):
        sb = SchemaBuilder(namespace="tshacl")
        sb.add_vertex_type("Thing", attributes={attr_name: text(**text_kwargs)})
        g = Graph()
        g.parse(data=sb.dump_shacl(), format="turtle")
        ns = Namespace("https://example.org/tshacl#")
        nss = Namespace("https://example.org/tshacl/shape#")
        # Find the property shape
        for prop_node in g.objects(nss.ThingShape, _SH.property):
            if (prop_node, _SH.path, ns[attr_name]) in g:
                return g, prop_node
        pytest.fail(f"No SHACL property shape found for {attr_name}")

    def test_required_single_min1_max1(self):
        g, ps = self._get_prop_shape(required=True, multiple=False)
        assert int(g.value(ps, _SH.minCount)) == 1
        assert int(g.value(ps, _SH.maxCount)) == 1

    def test_optional_single_min0_max1(self):
        g, ps = self._get_prop_shape(required=False, multiple=False)
        assert int(g.value(ps, _SH.minCount)) == 0
        assert int(g.value(ps, _SH.maxCount)) == 1

    def test_required_multiple_min1_no_max(self):
        g, ps = self._get_prop_shape(required=True, multiple=True)
        assert int(g.value(ps, _SH.minCount)) == 1
        assert g.value(ps, _SH.maxCount) is None

    def test_optional_multiple_min0_no_max(self):
        g, ps = self._get_prop_shape(required=False, multiple=True)
        assert int(g.value(ps, _SH.minCount)) == 0
        assert g.value(ps, _SH.maxCount) is None

    def test_no_sh_in_constraint(self):
        """text() must NOT generate sh:in (unlike vocab())."""
        g, ps = self._get_prop_shape()
        assert g.value(ps, _SH["in"]) is None

    def test_has_sh_datatype_string(self):
        g, ps = self._get_prop_shape()
        assert (ps, _SH.datatype, XSD.string) in g


# ---------------------------------------------------------------------------
# text() on all element types (vertex, edge, face)
# ---------------------------------------------------------------------------

class TestTextAllTypes:
    def test_text_on_vertex(self):
        sb = SchemaBuilder(namespace="tvtx")
        sb.add_vertex_type("V", attributes={"note": text()})
        assert "note" in sb._types["V"]["attributes"]

    def test_text_on_edge(self):
        sb = SchemaBuilder(namespace="tedg")
        sb.add_edge_type("E", attributes={"note": text()})
        assert "note" in sb._types["E"]["attributes"]

    def test_text_on_face(self):
        sb = SchemaBuilder(namespace="tfac")
        sb.add_face_type("F", attributes={"note": text()})
        assert "note" in sb._types["F"]["attributes"]

    def test_mixed_vocab_and_text(self):
        sb = SchemaBuilder(namespace="tmix")
        sb.add_edge_type("E", attributes={
            "kind": vocab("a", "b"),
            "desc": text(),
        })
        assert isinstance(sb._types["E"]["attributes"]["kind"], VocabDescriptor)
        assert isinstance(sb._types["E"]["attributes"]["desc"], TextDescriptor)


# ---------------------------------------------------------------------------
# Shared domain handling — the key regression area
# ---------------------------------------------------------------------------

class TestSharedDomain:
    def test_unique_property_has_domain_in_owl(self):
        """A property that appears on only one type should have rdfs:domain."""
        sb = SchemaBuilder(namespace="tdom1")
        sb.add_vertex_type("V", attributes={"v_only": text()})
        sb.add_edge_type("E", attributes={"e_only": text()})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/tdom1#")
        assert (ns.v_only, RDFS.domain, ns.V) in g
        assert (ns.e_only, RDFS.domain, ns.E) in g

    def test_shared_property_no_domain_in_owl(self):
        """A property appearing on 2+ types should have NO rdfs:domain."""
        sb = SchemaBuilder(namespace="tdom2")
        sb.add_vertex_type("V", attributes={"persona": text()})
        sb.add_edge_type("E", attributes={"persona": text()})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/tdom2#")
        domains = list(g.objects(ns.persona, RDFS.domain))
        assert len(domains) == 0

    def test_shared_property_three_types_no_domain(self):
        """A property appearing on 3 types should still have NO rdfs:domain."""
        sb = SchemaBuilder(namespace="tdom3")
        sb.add_vertex_type("V", attributes={"persona": text()})
        sb.add_edge_type("E", attributes={"persona": text()})
        sb.add_face_type("F", attributes={"persona": text()})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/tdom3#")
        domains = list(g.objects(ns.persona, RDFS.domain))
        assert len(domains) == 0

    def test_per_type_shacl_despite_shared_domain(self):
        """Each type should have its own SHACL property shape for the shared property."""
        sb = SchemaBuilder(namespace="tdom4")
        sb.add_vertex_type("V", attributes={"persona": text()})
        sb.add_edge_type("E", attributes={"persona": text()})
        g = Graph()
        g.parse(data=sb.dump_shacl(), format="turtle")
        ns = Namespace("https://example.org/tdom4#")
        nss = Namespace("https://example.org/tdom4/shape#")
        # Both shapes should have a property shape for persona
        for shape_name in ["VShape", "EShape"]:
            found = False
            for prop_node in g.objects(nss[shape_name], _SH.property):
                if (prop_node, _SH.path, ns.persona) in g:
                    found = True
            assert found, f"{shape_name} missing SHACL property shape for persona"

    def test_shared_vocab_property_no_domain(self):
        """Shared domain removal also works for vocab() properties, not just text()."""
        sb = SchemaBuilder(namespace="tdomv")
        sb.add_vertex_type("V", attributes={"kind": vocab("a", "b")})
        sb.add_edge_type("E", attributes={"kind": vocab("a", "b")})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/tdomv#")
        domains = list(g.objects(ns.kind, RDFS.domain))
        assert len(domains) == 0


# ---------------------------------------------------------------------------
# Cross-type validation safety (integration)
# ---------------------------------------------------------------------------

class TestCrossTypeValidation:
    def test_shared_persona_no_cross_type_violation(self):
        """Adding vertex with 'persona' should NOT trigger edge SHACL violations."""
        sb = SchemaBuilder(namespace="txval")
        sb.add_vertex_type("V", attributes={"persona": text()})
        sb.add_edge_type("E", attributes={"persona": text()})
        kc = KnowledgeComplex(schema=sb)
        # Should not raise — vertex doesn't need edge attributes
        kc.add_vertex("v1", type="V", persona="test persona")


# ---------------------------------------------------------------------------
# List value assertion (kc/graph.py)
# ---------------------------------------------------------------------------

class TestListValues:
    def test_list_value_accepted(self):
        """text(multiple=True) values should accept a list."""
        sb = SchemaBuilder(namespace="tlist")
        sb.add_vertex_type("V", attributes={"tags": text(multiple=True)})
        kc = KnowledgeComplex(schema=sb)
        kc.add_vertex("v1", type="V", tags=["a", "b", "c"])

    def test_list_value_in_graph(self):
        """Each list item should become a separate triple."""
        sb = SchemaBuilder(namespace="tlist2")
        sb.add_vertex_type("V", attributes={"tags": text(multiple=True)})
        kc = KnowledgeComplex(schema=sb)
        kc.add_vertex("v1", type="V", tags=["x", "y"])
        ttl = kc.dump_graph()
        assert '"x"' in ttl
        assert '"y"' in ttl


# ---------------------------------------------------------------------------
# Dict-style spec for text attributes
# ---------------------------------------------------------------------------

class TestDictSpec:
    def test_text_via_dict_spec(self):
        sb = SchemaBuilder(namespace="tdict")
        sb.add_face_type("F", attributes={
            "note": {"text": text(required=False), },
        })
        assert "note" in sb._types["F"]["attributes"]


# ---------------------------------------------------------------------------
# promote_to_attribute with text
# ---------------------------------------------------------------------------

class TestPromoteWithText:
    def test_promote_text_attribute(self):
        sb = SchemaBuilder(namespace="tprom")
        sb.add_vertex_type("V")
        sb.promote_to_attribute("V", "desc", text=text(), required=True)
        g = Graph()
        g.parse(data=sb.dump_shacl(), format="turtle")
        ns = Namespace("https://example.org/tprom#")
        nss = Namespace("https://example.org/tprom/shape#")
        found = False
        for prop_node in g.objects(nss.VShape, _SH.property):
            if (prop_node, _SH.path, ns.desc) in g:
                found = True
                assert int(g.value(prop_node, _SH.minCount)) == 1
        assert found

    def test_promote_requires_vocab_or_text(self):
        sb = SchemaBuilder(namespace="tprom2")
        sb.add_vertex_type("V")
        from kc.exceptions import SchemaError
        with pytest.raises(SchemaError):
            sb.promote_to_attribute("V", "x")


# ---------------------------------------------------------------------------
# Regression tests (bugs found during WP4.5 development)
# ---------------------------------------------------------------------------

class TestRegressions:
    def test_regression_shared_domain_no_rdfs_inference_leak(self):
        """Regression: shared property domain must not cause RDFS inference
        to classify a vertex as a face (or vice versa).

        Bug: when persona appeared on Color, ColorPair, and ColorTriple,
        adding rdfs:domain for each type caused RDFS to infer that any
        individual with persona is a member of ALL three classes.
        """
        sb = SchemaBuilder(namespace="treg1")
        sb.add_vertex_type("V", attributes={"persona": text()})
        sb.add_edge_type("E", attributes={"persona": text()})
        sb.add_face_type("F", attributes={"persona": text()})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/treg1#")
        # No domain should exist
        domains = list(g.objects(ns.persona, RDFS.domain))
        assert len(domains) == 0

    def test_regression_domain_not_readded_on_third_type(self):
        """Regression: domain must not be re-added when a 3rd type uses the property.

        Bug: first implementation checked graph triples to detect if domain
        was already set, but since the OWL property was already declared,
        the check was unreliable. Fixed with _attr_domains tracking dict.
        """
        sb = SchemaBuilder(namespace="treg2")
        sb.add_vertex_type("V", attributes={"note": text()})
        sb.add_edge_type("E", attributes={"note": text()})
        # After 2 types, domain should be None in tracker
        assert sb._attr_domains.get("note") is None
        sb.add_face_type("F", attributes={"note": text()})
        # After 3 types, should still be None
        assert sb._attr_domains.get("note") is None
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/treg2#")
        domains = list(g.objects(ns.note, RDFS.domain))
        assert len(domains) == 0

    def test_regression_vocab_shared_domain_same_behavior(self):
        """Regression: shared domain removal must work for vocab() too, not just text().

        Bug: the _set_owl_domain fix only applied to _add_text_attr_to_graphs
        initially. Both vocab and text properties need shared domain handling.
        """
        sb = SchemaBuilder(namespace="treg3")
        sb.add_vertex_type("V", attributes={"kind": vocab("a")})
        sb.add_edge_type("E", attributes={"kind": vocab("a")})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/treg3#")
        domains = list(g.objects(ns.kind, RDFS.domain))
        assert len(domains) == 0

    def test_regression_first_type_keeps_domain(self):
        """Regression sanity: a property used by only one type should KEEP its domain."""
        sb = SchemaBuilder(namespace="treg4")
        sb.add_vertex_type("V", attributes={"unique_attr": text()})
        sb.add_edge_type("E", attributes={"other_attr": text()})
        g = Graph()
        g.parse(data=sb.dump_owl(), format="turtle")
        ns = Namespace("https://example.org/treg4#")
        assert (ns.unique_attr, RDFS.domain, ns.V) in g
        assert (ns.other_attr, RDFS.domain, ns.E) in g
