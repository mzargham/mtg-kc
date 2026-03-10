"""
tests/test_query_templates.py

Tests for kc.graph._load_query_templates() — the one implemented function in graph.py.
All tests should pass today.

Traceability: see tests/requirements.md
"""

import pytest
from pathlib import Path

from kc.graph import _load_query_templates
from models.mtg import QUERIES_DIR


def test_load_framework_queries():
    """Framework queries dir yields 'vertices' and 'coboundary' templates."""
    templates = _load_query_templates()
    assert "vertices" in templates
    assert "coboundary" in templates


def test_load_with_model_queries():
    """Adding MTG model queries dir yields domain-specific templates."""
    templates = _load_query_templates(extra_dirs=[QUERIES_DIR])
    assert "edges_by_disposition" in templates
    assert "faces_by_edge_pattern" in templates
    # Framework templates should still be present
    assert "vertices" in templates
    assert "coboundary" in templates


def test_model_queries_override_framework(tmp_path):
    """A model query with the same name as a framework query takes precedence."""
    # Create a fake vertices.sparql with distinct content
    override = tmp_path / "vertices.sparql"
    override.write_text("SELECT ?override WHERE { ?s ?p ?o }")

    # Load with the override dir
    templates = _load_query_templates(extra_dirs=[tmp_path])
    assert "override" in templates["vertices"], (
        "Model query should override framework query of same name"
    )


def test_query_template_values_are_strings():
    """Each template value should be a non-empty string."""
    templates = _load_query_templates(extra_dirs=[QUERIES_DIR])
    for name, text in templates.items():
        assert isinstance(text, str), f"Template '{name}' is not a string"
        assert len(text) > 0, f"Template '{name}' is empty"


def test_query_templates_contain_select():
    """Each template should contain a SELECT statement (basic SPARQL validity)."""
    templates = _load_query_templates(extra_dirs=[QUERIES_DIR])
    for name, text in templates.items():
        assert "SELECT" in text, f"Template '{name}' missing SELECT keyword"


def test_coboundary_template_has_placeholder():
    """coboundary.sparql should contain {simplex} substitution token."""
    templates = _load_query_templates()
    assert "{simplex}" in templates["coboundary"]


def test_vertices_template_has_no_placeholders():
    """vertices.sparql operates on full graph — no {placeholder} tokens."""
    templates = _load_query_templates()
    text = templates["vertices"]
    # Check for {word} patterns that aren't part of SPARQL syntax like { }
    import re
    placeholders = re.findall(r"\{[a-zA-Z_]+\}", text)
    assert len(placeholders) == 0, f"Found unexpected placeholders: {placeholders}"


def test_edges_by_disposition_references_disposition():
    """MTG edges_by_disposition template should reference the disposition property."""
    templates = _load_query_templates(extra_dirs=[QUERIES_DIR])
    assert "disposition" in templates["edges_by_disposition"]


def test_faces_by_edge_pattern_references_disposition():
    """MTG faces_by_edge_pattern template should reference the disposition property."""
    templates = _load_query_templates(extra_dirs=[QUERIES_DIR])
    assert "disposition" in templates["faces_by_edge_pattern"]


def test_empty_extra_dirs_same_as_none():
    """_load_query_templates(extra_dirs=[]) should return same keys as no argument."""
    t1 = _load_query_templates()
    t2 = _load_query_templates(extra_dirs=[])
    assert set(t1.keys()) == set(t2.keys())
