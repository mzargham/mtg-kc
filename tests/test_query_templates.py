"""
tests/test_query_templates.py

Tests for SPARQL query template loading via the public KnowledgeComplex API.
Verifies framework and model queries are discoverable and well-formed.

Traceability: see tests/requirements.md
"""

import re
import pytest

from knowledgecomplex import SchemaBuilder, vocab, KnowledgeComplex, UnknownQueryError
from models.mtg import QUERIES_DIR


@pytest.fixture
def schema() -> SchemaBuilder:
    """Minimal schema with one vertex type for query testing."""
    sb = SchemaBuilder(namespace="test")
    sb.add_vertex_type("Node", {"label": vocab("a", "b")})
    return sb


def test_framework_query_vertices(schema):
    """KnowledgeComplex should have the 'vertices' query template available."""
    kc = KnowledgeComplex(schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("n1", "Node", label="a")
    df = kc.query("vertices")
    assert len(df) >= 1


def test_model_queries_available(schema):
    """MTG model queries should be available when query_dirs includes QUERIES_DIR."""
    kc = KnowledgeComplex(schema, query_dirs=[QUERIES_DIR])
    kc.add_vertex("n1", "Node", label="a")
    # These should not raise UnknownQueryError
    # (they may return empty results since we don't have edges/faces)
    try:
        kc.query("edges_by_disposition")
    except UnknownQueryError:
        pytest.fail("edges_by_disposition query should be registered")
    try:
        kc.query("faces_by_edge_pattern")
    except UnknownQueryError:
        pytest.fail("faces_by_edge_pattern query should be registered")


def test_unknown_query_raises(schema):
    """Querying an unregistered template name should raise UnknownQueryError."""
    kc = KnowledgeComplex(schema)
    kc.add_vertex("n1", "Node", label="a")
    with pytest.raises(UnknownQueryError):
        kc.query("nonexistent_query_template")


def test_model_queries_override_framework(schema, tmp_path):
    """A model query with the same name as a framework query takes precedence."""
    override = tmp_path / "vertices.sparql"
    override.write_text("SELECT ?override WHERE { ?s ?p ?o }")
    kc = KnowledgeComplex(schema, query_dirs=[tmp_path])
    kc.add_vertex("n1", "Node", label="a")
    df = kc.query("vertices")
    assert "override" in df.columns, "Model query should override framework query of same name"
