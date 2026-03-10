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
from models.mtg import QUERIES_DIR


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
    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    kc.add_vertex("Black", type="Color")
    kc.add_edge("WU", type="Relationship", vertices={"White", "Blue"},  disposition="adjacent")
    kc.add_edge("UB", type="Relationship", vertices={"Blue", "Black"}, disposition="opposite")
    kc.add_edge("WB", type="Relationship", vertices={"White", "Black"}, disposition="opposite")
    kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"])
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
    kc.add_edge("WU", type="Relationship", vertices={"White", "Blue"},
                disposition="adjacent")


def test_add_edge_invalid_disposition(schema):
    """REQ-GRAPH-03, REQ-VV-04: invalid vocab value raises ValidationError."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    with pytest.raises(ValidationError):
        kc.add_edge("WU", type="Relationship", vertices={"White", "Blue"},
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
    kc.add_edge("WU", type="Relationship", vertices={"W", "U"}, disposition="adjacent")
    kc.add_edge("UB", type="Relationship", vertices={"U", "B"}, disposition="adjacent")
    kc.add_edge("WR", type="Relationship", vertices={"W", "R"}, disposition="opposite")
    # WU, UB, WR do not form a closed triangle
    with pytest.raises(ValidationError):
        kc.add_face("bad", type="ColorTriple", boundary=["WU", "UB", "WR"])


def test_add_face_wrong_count_raises(schema):
    """REQ-GRAPH-04: boundary list != 3 raises ValueError (not ValidationError)."""
    kc = KnowledgeComplex(schema=schema)
    with pytest.raises(ValueError):
        kc.add_face("f", type="ColorTriple", boundary=["e1", "e2"])


# --- boundary-closure (ComplexShape) ---

def test_add_edge_before_vertices_fails(schema):
    """ComplexShape: adding an edge before its boundary vertices raises ValidationError.

    Boundary-closure requires that all boundary elements of a simplex are
    already members of the complex. Adding an edge whose vertices haven't
    been added yet violates this constraint.
    """
    kc = KnowledgeComplex(schema=schema)
    # Do NOT add vertices first — edge's boundary vertices are not in the complex
    with pytest.raises(ValidationError):
        kc.add_edge("WU", type="Relationship", vertices={"White", "Blue"},
                    disposition="adjacent")


# --- ValidationError ---

def test_validation_error_has_report(schema):
    """REQ-GRAPH-05: ValidationError exposes .report as a non-empty string."""
    kc = KnowledgeComplex(schema=schema)
    kc.add_vertex("White", type="Color")
    kc.add_vertex("Blue",  type="Color")
    try:
        kc.add_edge("WU", type="Relationship", vertices={"White", "Blue"},
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
