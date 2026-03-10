"""
tests/test_knowledge_complex.py

Tests for kc.graph.KnowledgeComplex.
All tests call the public API only. No rdflib/pyshacl imports.

Traceability: see tests/requirements.md
"""

import pytest
import pandas as pd

from kc.schema import SchemaBuilder, vocab
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError, UnknownQueryError


@pytest.fixture
def schema() -> SchemaBuilder:
    sb = SchemaBuilder(namespace="test")
    sb.add_vertex_type("Color")
    sb.add_edge_type(
        "Relationship",
        attributes={"disposition": vocab("adjacent", "opposite")},
    )
    sb.add_face_type(
        "ColorTriple",
        attributes={"pattern": vocab("ooa", "oaa"), "required": False},
    )
    return sb


@pytest.fixture
def minimal_kc(schema) -> KnowledgeComplex:
    """3-vertex, 3-edge, 1-face valid closed triangle."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    kc.add_vertex("Black", type="Color")
    kc.add_edge("WU", type="Relationship", source="White", target="Blue",  disposition="adjacent")
    kc.add_edge("UB", type="Relationship", source="Blue",  target="Black", disposition="opposite")
    kc.add_edge("WB", type="Relationship", source="White", target="Black", disposition="opposite")
    kc.add_face("WUB", type="ColorTriple", edges=["WU", "UB", "WB"])
    return kc


# --- add_vertex ---

def test_add_vertex_valid(schema):
    """REQ-GRAPH-02: valid vertex is added without error."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")  # should not raise


def test_add_vertex_invalid_type_fails(schema):
    """REQ-GRAPH-02, REQ-VV-04: unregistered type raises ValidationError."""
    kc = KnowledgeComplex(schema=schema)
    with pytest.raises(ValidationError):
        kc.add_vertex("White", type="UnknownType")


# --- add_edge ---

def test_add_edge_valid(schema):
    """REQ-GRAPH-03: valid edge is added without error."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    kc.add_edge("WU", type="Relationship", source="White", target="Blue",
                disposition="adjacent")


def test_add_edge_invalid_disposition(schema):
    """REQ-GRAPH-03, REQ-VV-04: invalid vocab value raises ValidationError."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    with pytest.raises(ValidationError):
        kc.add_edge("WU", type="Relationship", source="White", target="Blue",
                    disposition="invalid_value")


# --- add_face ---

def test_add_face_valid(minimal_kc):
    """REQ-GRAPH-04: valid closed-triangle face already added in fixture — no error."""
    pass  # fixture construction is the test


def test_add_face_open_triangle_fails(schema):
    """REQ-GRAPH-04, REQ-VV-02: open-triangle face raises ValidationError."""
    kc = KnowledgeComplex(schema=schema)
    for v in ["W", "U", "B", "R"]:
        kc.add_vertex(v, type="Color")
    kc.add_edge("WU", type="Relationship", source="W", target="U", disposition="adjacent")
    kc.add_edge("UB", type="Relationship", source="U", target="B", disposition="adjacent")
    kc.add_edge("WR", type="Relationship", source="W", target="R", disposition="opposite")
    # WU, UB, WR do not form a closed triangle
    with pytest.raises(ValidationError):
        kc.add_face("bad", type="ColorTriple", edges=["WU", "UB", "WR"])


def test_add_face_wrong_count_raises(schema):
    """REQ-GRAPH-04: edges list != 3 raises ValueError (not ValidationError)."""
    kc = KnowledgeComplex(schema=schema)
    with pytest.raises(ValueError):
        kc.add_face("f", type="ColorTriple", edges=["e1", "e2"])


# --- ValidationError ---

def test_validation_error_has_report(schema):
    """REQ-GRAPH-05: ValidationError exposes .report as a non-empty string."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    try:
        kc.add_edge("WU", type="Relationship", source="White", target="Blue",
                    disposition="INVALID")
    except ValidationError as e:
        assert isinstance(e.report, str)
        assert len(e.report) > 0
    else:
        pytest.fail("Expected ValidationError was not raised")


# --- query ---

def test_query_faces_by_edge_pattern(minimal_kc):
    """REQ-GRAPH-06, REQ-QUERY-01, REQ-VV-05: query returns DataFrame."""
    df = minimal_kc.query("faces_by_edge_pattern")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1


def test_query_unknown_template_raises(minimal_kc):
    """REQ-GRAPH-07: unregistered template name raises UnknownQueryError."""
    with pytest.raises(UnknownQueryError):
        minimal_kc.query("no_such_query")


# --- dump_graph ---

def test_dump_graph_is_valid_turtle(minimal_kc):
    """REQ-GRAPH-08: dump_graph() returns parseable Turtle string."""
    from rdflib import Graph  # rdflib allowed in test to verify output
    ttl = minimal_kc.dump_graph()
    assert isinstance(ttl, str)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    assert len(g) > 0


# --- API opacity ---

def test_no_rdflib_in_public_api(minimal_kc):
    """REQ-GRAPH-09, REQ-VV-06: public methods return no rdflib objects."""
    import rdflib
    ttl = minimal_kc.dump_graph()
    df = minimal_kc.query("faces_by_edge_pattern")
    assert isinstance(ttl, str)
    assert isinstance(df, pd.DataFrame)
    assert not isinstance(ttl, rdflib.Graph)
