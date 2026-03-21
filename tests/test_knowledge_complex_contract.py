"""
tests/test_knowledge_complex_contract.py

Tests for KnowledgeComplex API contract: boundary-count validation,
duplicate handling, shared edges, interleaved construction order.

Traceability: REQ-CORE-02, REQ-CORE-03, REQ-GRAPH-02/03/04.
"""

import pytest
import pandas as pd

from knowledgecomplex import SchemaBuilder, vocab, KnowledgeComplex, ValidationError
from models.mtg import QUERIES_DIR


def _make_schema() -> SchemaBuilder:
    sb = SchemaBuilder(namespace="mtg")
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


# ---------------------------------------------------------------------------
# Boundary-count validation (REQ-CORE-02, REQ-CORE-03)
# ---------------------------------------------------------------------------

def test_add_edge_one_vertex_raises_value_error():
    """REQ-CORE-02: add_edge with 1 vertex should raise ValueError."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("A", type="Color")
    with pytest.raises(ValueError):
        kc.add_edge("e1", type="ColorPair", vertices={"A"}, disposition="adjacent")


def test_add_edge_three_vertices_raises_value_error():
    """REQ-CORE-02: add_edge with 3 vertices should raise ValueError."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    for v in ["A", "B", "C"]:
        kc.add_vertex(v, type="Color")
    with pytest.raises(ValueError):
        kc.add_edge("e1", type="ColorPair", vertices={"A", "B", "C"}, disposition="adjacent")


def test_add_face_one_edge_raises_value_error():
    """REQ-CORE-03: add_face with 1 boundary edge should raise ValueError."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    for v in ["A", "B"]:
        kc.add_vertex(v, type="Color")
    kc.add_edge("AB", type="ColorPair", vertices={"A", "B"}, disposition="adjacent")
    with pytest.raises(ValueError):
        kc.add_face("f1", type="ColorTriple", boundary=["AB"])


def test_add_face_four_edges_raises_value_error():
    """REQ-CORE-03: add_face with 4 boundary edges should raise ValueError."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    for v in ["A", "B", "C", "D"]:
        kc.add_vertex(v, type="Color")
    kc.add_edge("AB", type="ColorPair", vertices={"A", "B"}, disposition="adjacent")
    kc.add_edge("BC", type="ColorPair", vertices={"B", "C"}, disposition="adjacent")
    kc.add_edge("CA", type="ColorPair", vertices={"C", "A"}, disposition="opposite")
    kc.add_edge("AD", type="ColorPair", vertices={"A", "D"}, disposition="opposite")
    with pytest.raises(ValueError):
        kc.add_face("f1", type="ColorTriple", boundary=["AB", "BC", "CA", "AD"])


# ---------------------------------------------------------------------------
# API behavior (REQ-GRAPH-02/08)
# ---------------------------------------------------------------------------

def test_duplicate_vertex_id_behavior():
    """Adding the same vertex ID twice should raise or be handled gracefully.

    Documents expected behavior for implementation: either raise SchemaError/ValueError
    on duplicate, or silently overwrite. Test should be updated when WP3 decides.
    """
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("White", type="Color")
    # Second add with same ID — document whichever behavior is chosen
    kc.add_vertex("White", type="Color")  # should not crash at minimum


def test_empty_graph_query_returns_empty_dataframe():
    """query('vertices') on a fresh complex with no data should return empty DataFrame."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    df = kc.query("vertices")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_two_triangles_sharing_edge():
    """Two valid faces sharing one edge should coexist in the same complex."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    # 4 vertices
    for v in ["A", "B", "C", "D"]:
        kc.add_vertex(v, type="Color")
    # 5 edges forming two triangles sharing AB
    kc.add_edge("AB", type="ColorPair", vertices={"A", "B"}, disposition="adjacent")
    kc.add_edge("BC", type="ColorPair", vertices={"B", "C"}, disposition="adjacent")
    kc.add_edge("CA", type="ColorPair", vertices={"C", "A"}, disposition="opposite")
    kc.add_edge("BD", type="ColorPair", vertices={"B", "D"}, disposition="opposite")
    kc.add_edge("DA", type="ColorPair", vertices={"D", "A"}, disposition="opposite")
    # Two faces
    kc.add_face("ABC", type="ColorTriple", boundary=["AB", "BC", "CA"])
    kc.add_face("ABD", type="ColorTriple", boundary=["AB", "BD", "DA"])


def test_slice_rule_interleaved_order():
    """Elements can be added in any order as long as boundary predecessors are present.

    v1 → v2 → edge(v1,v2) → v3 → edge(v2,v3) → edge(v1,v3) → face
    """
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("v1", type="Color")
    kc.add_vertex("v2", type="Color")
    kc.add_edge("e12", type="ColorPair", vertices={"v1", "v2"}, disposition="adjacent")
    kc.add_vertex("v3", type="Color")
    kc.add_edge("e23", type="ColorPair", vertices={"v2", "v3"}, disposition="adjacent")
    kc.add_edge("e13", type="ColorPair", vertices={"v1", "v3"}, disposition="opposite")
    kc.add_face("f123", type="ColorTriple", boundary=["e12", "e23", "e13"])


def test_dump_graph_returns_string():
    """dump_graph() should return a string after adding some data."""
    schema = _make_schema()
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("White", type="Color")
    ttl = kc.dump_graph()
    assert isinstance(ttl, str)
    assert len(ttl) > 0
