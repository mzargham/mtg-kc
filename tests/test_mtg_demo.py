"""
tests/test_mtg_demo.py

Integration tests for the full MTG demo instance.
Validates all REQ-DEMO requirements and the end-to-end hypothesis test criteria.

Traceability: see tests/requirements.md
"""

import pytest
import pandas as pd

from kc.schema import SchemaBuilder, vocab
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError
from models.mtg import build_mtg_schema, QUERIES_DIR


# MTG pentagon adjacency and opposition (undirected, represented as sorted pairs)
_ADJACENT_PAIRS = {
    frozenset({"White", "Blue"}),
    frozenset({"Blue",  "Black"}),
    frozenset({"Black", "Red"}),
    frozenset({"Red",   "Green"}),
    frozenset({"Green", "White"}),
}

_OPPOSITE_PAIRS = {
    frozenset({"White", "Black"}),
    frozenset({"White", "Red"}),
    frozenset({"Blue",  "Green"}),
    frozenset({"Blue",  "Red"}),
    frozenset({"Black", "Green"}),
}

# Ground-truth face classification (sorted color triple → pattern)
# ooa = two opposite edges + one adjacent; oaa = one opposite + two adjacent
# Computed by hand from MTG color wheel topology.
_FACE_PATTERNS: dict[frozenset, str] = {
    # TODO (WP4): fill in during demo instance authoring
    # e.g. frozenset({"White", "Blue", "Black"}): "ooa",
}


@pytest.fixture(scope="module")
def mtg_kc() -> KnowledgeComplex:
    """Full MTG demo instance (no pattern attributes asserted)."""
    sb = build_mtg_schema()
    kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])

    colors = ["White", "Blue", "Black", "Red", "Green"]
    for c in colors:
        kc.add_vertex(c, type="Color")

    edge_id = 0
    for pair in _ADJACENT_PAIRS:
        kc.add_edge(f"e{edge_id}", type="Relationship",
                    vertices=pair, disposition="adjacent")
        edge_id += 1

    for pair in _OPPOSITE_PAIRS:
        kc.add_edge(f"e{edge_id}", type="Relationship",
                    vertices=pair, disposition="opposite")
        edge_id += 1

    # TODO (WP4): enumerate all 10 valid triangles and add_face for each
    # For now, a placeholder to make fixture construction non-blocking
    # kc.add_face("f0", type="ColorTriple", boundary=[...])

    return kc


# --- REQ-DEMO-01 ---

def test_five_color_vertices(mtg_kc):
    """REQ-DEMO-01: exactly 5 Color vertices."""
    df = mtg_kc.query("vertices")
    colors = df[df["type"].str.contains("Color")]
    assert len(colors) == 5


# --- REQ-DEMO-02, REQ-DEMO-03 ---

def test_five_adjacent_edges(mtg_kc):
    """REQ-DEMO-02: exactly 5 adjacent edges."""
    df = mtg_kc.query("edges_by_disposition")
    assert len(df[df["disposition"] == "adjacent"]) == 5


def test_five_opposite_edges(mtg_kc):
    """REQ-DEMO-03: exactly 5 opposite edges."""
    df = mtg_kc.query("edges_by_disposition")
    assert len(df[df["disposition"] == "opposite"]) == 5


# --- REQ-DEMO-04 ---

@pytest.mark.skip(reason="WP4: face construction not yet implemented")
def test_ten_faces_valid(mtg_kc):
    """REQ-DEMO-04: exactly 10 ColorTriple faces, all structurally valid."""
    df = mtg_kc.query("faces_by_edge_pattern")
    assert len(df) == 10


# --- REQ-DEMO-05, REQ-VV-05 ---

@pytest.mark.skip(reason="WP4: face construction not yet implemented")
def test_no_pattern_asserted(mtg_kc):
    """REQ-DEMO-05: no face has a pattern attribute in the raw instance."""
    ttl = mtg_kc.dump_graph()
    assert "ooa" not in ttl
    assert "oaa" not in ttl


@pytest.mark.skip(reason="WP4: face construction not yet implemented")
def test_pattern_discovery_ooa_oaa(mtg_kc):
    """REQ-DEMO-05, REQ-VV-05: SPARQL correctly classifies all 10 faces into ooa/oaa."""
    df = mtg_kc.query("faces_by_edge_pattern")
    # Derive pattern from the three disposition values
    def classify(row):
        dispositions = sorted([row["d1"], row["d2"], row["d3"]])
        # ooa: adjacent, opposite, opposite
        # oaa: adjacent, adjacent, opposite
        if dispositions.count("opposite") == 2:
            return "ooa"
        elif dispositions.count("opposite") == 1:
            return "oaa"
        else:
            return "unknown"
    df["discovered_pattern"] = df.apply(classify, axis=1)
    assert set(df["discovered_pattern"]) == {"ooa", "oaa"}
    assert "unknown" not in df["discovered_pattern"].values
    # Verify counts (to be confirmed in WP4 against ground truth)
    # assert len(df[df["discovered_pattern"] == "ooa"]) == ?
    # assert len(df[df["discovered_pattern"] == "oaa"]) == ?


# --- REQ-DEMO-06, REQ-VV-03, REQ-VV-04 ---

@pytest.mark.skip(reason="WP4: face construction not yet implemented")
def test_promote_causes_validation_fail(mtg_kc):
    """REQ-DEMO-06: after promoting pattern to required, all 10 faces fail SHACL."""
    # promote_to_attribute modifies the schema in place;
    # use a fresh schema + instance for isolation
    sb = SchemaBuilder(namespace="mtg_promote")
    sb.add_vertex_type("Color")
    sb.add_edge_type("Relationship",
                     attributes={"disposition": vocab("adjacent", "opposite")})
    sb.add_face_type("ColorTriple",
                     attributes={"pattern": vocab("ooa", "oaa"), "required": False})

    # TODO: build the full MTG instance against sb, then promote
    sb.promote_to_attribute(
        type="ColorTriple",
        attribute="pattern",
        vocab=vocab("ooa", "oaa"),
        required=True,
    )
    # Re-validate: all faces should now fail
    # kc_new = KnowledgeComplex(schema=sb)
    # ... add all vertices, edges, faces without pattern ...
    # for face_id in face_ids:
    #     with pytest.raises(ValidationError):
    #         kc_new.add_face(face_id, ...)
    pytest.skip("Full implementation pending WP4")
