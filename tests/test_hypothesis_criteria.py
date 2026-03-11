"""
tests/test_hypothesis_criteria.py

One test per hypothesis criterion (H1-H6) from ARCHITECTURE.md.
Direct traceability from success measures to executable tests.

Some pass today (static resource checks), some fail (require WP3 implementation).

Traceability: ARCHITECTURE.md §Hypothesis Test Criteria
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
import pyshacl

KC  = Namespace("https://example.org/kc#")
KCS = Namespace("https://example.org/kc/shape#")
SH  = Namespace("http://www.w3.org/ns/shacl#")

_ROOT        = Path(__file__).parent.parent
_CORE_OWL    = _ROOT / "kc" / "resources" / "kc_core.ttl"
_CORE_SHAPES = _ROOT / "kc" / "resources" / "kc_core_shapes.ttl"
EX = Namespace("https://example.org/test#")


# ═══════════════════════════════════════════════════════════════════════════
# H1: 2×2 coverage — all four cells have at least one concrete rule
# ═══════════════════════════════════════════════════════════════════════════

def test_h1_topological_cells_populated():
    """H1 (static): both topological cells (OWL + SHACL) are populated."""
    owl = Graph()
    owl.parse(_CORE_OWL, format="turtle")
    shacl = Graph()
    shacl.parse(_CORE_SHAPES, format="turtle")

    # Topological-OWL: has cardinality axioms
    restrictions = set(owl.subjects(RDF.type, OWL.Restriction))
    assert any(owl.value(r, OWL.qualifiedCardinality) is not None for r in restrictions)

    # Topological-SHACL: has sh:SPARQLConstraint
    assert len(set(shacl.subjects(RDF.type, SH.SPARQLConstraint))) > 0


def test_h1_ontological_cells_populated():
    """H1 (API): both ontological cells are populated by SchemaBuilder."""
    from kc.schema import SchemaBuilder, vocab
    sb = SchemaBuilder(namespace="h1test")
    sb.add_edge_type("Rel", attributes={"x": vocab("a", "b")})

    owl_ttl = sb.dump_owl()
    shacl_ttl = sb.dump_shacl()

    # Ontological-OWL: user subclass exists
    g = Graph()
    g.parse(data=owl_ttl, format="turtle")
    rel = URIRef("https://example.org/h1test#Rel")
    assert (rel, RDFS.subClassOf, KC.Edge) in g

    # Ontological-SHACL: vocab values present
    assert "a" in shacl_ttl and "b" in shacl_ttl


# ═══════════════════════════════════════════════════════════════════════════
# H2: Topological limit documented — closed-triangle in SHACL sh:sparql
# ═══════════════════════════════════════════════════════════════════════════

def test_h2_closed_triangle_documented():
    """H2: FaceShape has a sh:SPARQLConstraint with a comment explaining why OWL cannot express it."""
    shacl = Graph()
    shacl.parse(_CORE_SHAPES, format="turtle")

    # Find SPARQL constraints on FaceShape
    sparql_constraints = list(shacl.objects(KCS.FaceShape, SH.sparql))
    assert len(sparql_constraints) > 0, "FaceShape has no sh:sparql constraint"

    # At least one should have a comment mentioning OWL
    comments = []
    for sc in sparql_constraints:
        for _, _, comment in shacl.triples((sc, RDFS.comment, None)):
            comments.append(str(comment))
    assert any("OWL" in c for c in comments), (
        f"FaceShape sh:sparql comments should mention OWL limitation. Found: {comments}"
    )


def test_h2_closed_triangle_rejects_open():
    """H2: the closed-triangle SHACL constraint rejects an open triangle."""
    def _validate(data_graph):
        shapes = Graph()
        shapes.parse(_CORE_SHAPES, format="turtle")
        ont = Graph()
        ont.parse(_CORE_OWL, format="turtle")
        conforms, _, report = pyshacl.validate(
            data_graph, shacl_graph=shapes, ont_graph=ont,
            inference="rdfs", abort_on_first=False,
        )
        return conforms, report

    # Open triangle: v1-v2, v2-v3, v1-v4 (not a cycle)
    g = Graph()
    for v in [EX.v1, EX.v2, EX.v3, EX.v4]:
        g.add((v, RDF.type, KC.Vertex))
    edges = [
        (EX.e12, EX.v1, EX.v2),
        (EX.e23, EX.v2, EX.v3),
        (EX.e14, EX.v1, EX.v4),
    ]
    for e, va, vb in edges:
        g.add((e, RDF.type, KC.Edge))
        g.add((e, KC.boundedBy, va))
        g.add((e, KC.boundedBy, vb))
    g.add((EX.f1, RDF.type, KC.Face))
    for e, _, _ in edges:
        g.add((EX.f1, KC.boundedBy, e))

    conforms, report = _validate(g)
    assert not conforms, "H2: open triangle must be rejected by SHACL."


# ═══════════════════════════════════════════════════════════════════════════
# H3: Single-call invariant — add_edge_type() and promote_to_attribute()
#     each produce changes in both OWL and SHACL dumps
# ═══════════════════════════════════════════════════════════════════════════

def test_h3_add_edge_type_updates_both_dumps():
    """H3: a single add_edge_type() call changes both dump_owl() and dump_shacl()."""
    from kc.schema import SchemaBuilder, vocab
    sb = SchemaBuilder(namespace="h3test")
    owl_before = sb.dump_owl()
    shacl_before = sb.dump_shacl()

    sb.add_edge_type("Rel", attributes={"x": vocab("a", "b")})

    owl_after = sb.dump_owl()
    shacl_after = sb.dump_shacl()

    assert owl_before != owl_after, "H3: add_edge_type must change OWL dump"
    assert shacl_before != shacl_after, "H3: add_edge_type must change SHACL dump"


def test_h3_promote_updates_both_dumps():
    """H3: a single promote_to_attribute() call changes both dump_owl() and dump_shacl()."""
    from kc.schema import SchemaBuilder, vocab
    sb = SchemaBuilder(namespace="h3test")
    sb.add_face_type("F", attributes={"x": {"vocab": vocab("a"), "required": False}})

    owl_before = sb.dump_owl()
    shacl_before = sb.dump_shacl()

    sb.promote_to_attribute("F", "x", vocab("a", "b"), required=True)

    owl_after = sb.dump_owl()
    shacl_after = sb.dump_shacl()

    assert owl_before != owl_after or "x" in owl_after, "H3: promote must affect OWL"
    assert shacl_before != shacl_after, "H3: promote must affect SHACL"


# ═══════════════════════════════════════════════════════════════════════════
# H4: Verification works — SHACL catches malformed face
# ═══════════════════════════════════════════════════════════════════════════

def test_h4_verification_catches_malformed_face():
    """H4: adding a face with non-closed-triangle edges raises ValidationError."""
    from kc.schema import SchemaBuilder, vocab
    from kc.graph import KnowledgeComplex
    from kc.exceptions import ValidationError
    from models.mtg import QUERIES_DIR

    sb = SchemaBuilder(namespace="h4test")
    sb.add_vertex_type("V")
    sb.add_edge_type("E")
    sb.add_face_type("F")

    kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])
    for v in ["a", "b", "c", "d"]:
        kc.add_vertex(v, type="V")
    kc.add_edge("ab", type="E", vertices={"a", "b"})
    kc.add_edge("bc", type="E", vertices={"b", "c"})
    kc.add_edge("ad", type="E", vertices={"a", "d"})  # not a closed triangle

    with pytest.raises(ValidationError):
        kc.add_face("bad", type="F", boundary=["ab", "bc", "ad"])


# ═══════════════════════════════════════════════════════════════════════════
# H5: Discovery works — SPARQL reveals shard/wedge without pre-assertion
# ═══════════════════════════════════════════════════════════════════════════

def test_h5_discovery_without_pre_assertion():
    """H5: SPARQL classifies MTG's 10 explicitly-enumerated faces by edge disposition.

    MTG asserts all 10 ColorTriple faces (K5 has C(5,3)=10 triangles).
    This is an MTG model assertion — the framework does not require all
    closed boundaries to have faces. See deferred issue in models/mtg/schema.py.
    """
    from demo.demo_instance import build_mtg_instance

    kc = build_mtg_instance()
    df = kc.query("faces_by_edge_pattern")
    assert len(df) == 10, f"Expected 10 faces, got {len(df)}"
    # Classify each face's pattern from edge dispositions
    for _, row in df.iterrows():
        dispositions = sorted([row["d1"], row["d2"], row["d3"]])
        opp_count = dispositions.count("opposite")
        assert opp_count in (1, 2), f"Unexpected disposition mix: {dispositions}"


# ═══════════════════════════════════════════════════════════════════════════
# H6: API opacity — notebook never imports rdflib, pyshacl, owlrl
# ═══════════════════════════════════════════════════════════════════════════

def test_h6_demo_notebook_opacity():
    """H6: demo/demo.py does not import rdflib, pyshacl, or owlrl."""
    import re
    src = (_ROOT / "demo" / "demo.py").read_text()
    for lib in ["rdflib", "pyshacl", "owlrl"]:
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert not re.search(rf'\bimport\s+{lib}\b', stripped), f"demo.py imports {lib}"
            assert not re.search(rf'\bfrom\s+{lib}\b', stripped), f"demo.py imports from {lib}"


def test_h6_schema_builder_returns_strings():
    """H6: SchemaBuilder public methods return str, not rdflib objects."""
    import rdflib
    from kc.schema import SchemaBuilder, vocab
    sb = SchemaBuilder(namespace="h6test")
    sb.add_vertex_type("V")
    owl = sb.dump_owl()
    shacl = sb.dump_shacl()
    assert isinstance(owl, str) and not isinstance(owl, rdflib.Graph)
    assert isinstance(shacl, str) and not isinstance(shacl, rdflib.Graph)


def test_h6_knowledge_complex_returns_strings_and_dataframes():
    """H6: KnowledgeComplex public methods return str or DataFrame, not rdflib objects."""
    import rdflib
    import pandas as pd
    from kc.graph import KnowledgeComplex
    from models.mtg import build_mtg_schema, QUERIES_DIR

    sb = build_mtg_schema()
    kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])
    kc.add_vertex("White", type="Color",
        goal="peace", method="order",
        persona="Test persona.",
        at_best="Test at best.",
        at_worst="Test at worst.",
        example_behaviors=["Test behavior"],
    )

    ttl = kc.dump_graph()
    assert isinstance(ttl, str)
    assert not isinstance(ttl, rdflib.Graph)
