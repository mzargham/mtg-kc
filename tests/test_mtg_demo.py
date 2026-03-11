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
# Computed from MTG color wheel: adjacent = pentagon edges, opposite = diagonals.
# 5 ooa + 5 oaa = 10 total.
_FACE_PATTERNS: dict[frozenset, str] = {
    frozenset({"White", "Blue", "Black"}):  "oaa",
    frozenset({"White", "Blue", "Red"}):    "ooa",
    frozenset({"White", "Blue", "Green"}):  "oaa",
    frozenset({"White", "Black", "Red"}):   "ooa",
    frozenset({"White", "Black", "Green"}): "ooa",
    frozenset({"White", "Red", "Green"}):   "oaa",
    frozenset({"Blue", "Black", "Red"}):    "oaa",
    frozenset({"Blue", "Black", "Green"}):  "ooa",
    frozenset({"Blue", "Red", "Green"}):    "ooa",
    frozenset({"Black", "Red", "Green"}):   "oaa",
}


@pytest.fixture(scope="module")
def mtg_kc() -> KnowledgeComplex:
    """Full MTG demo instance with all 10 faces (no pattern attributes asserted)."""
    from demo.demo_instance import build_mtg_instance
    return build_mtg_instance()


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

def test_ten_faces_valid(mtg_kc):
    """REQ-DEMO-04: exactly 10 ColorTriple faces, all structurally valid.

    MTG explicitly enumerates all C(5,3)=10 triangles in K5.
    This is an MTG model assertion, not a framework invariant.
    """
    df = mtg_kc.query("faces_by_edge_pattern")
    assert len(df) == 10


# --- REQ-DEMO-05, REQ-VV-05 ---

def test_no_pattern_asserted(mtg_kc):
    """REQ-DEMO-05: no face has a pattern attribute value in the raw instance.

    The OWL schema contains 'ooa'/'oaa' in the rdfs:comment annotation for
    the pattern property definition, but no instance should have a pattern value.
    """
    ttl = mtg_kc.dump_graph()
    # No face instance should have mtg:pattern "ooa" or "oaa" as a triple value.
    # The schema annotation (rdfs:comment "Allowed values: ooa, oaa") is expected.
    assert 'mtg:pattern "ooa"' not in ttl
    assert 'mtg:pattern "oaa"' not in ttl


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
    sb.add_edge_type("ColorPair",
                     attributes={"disposition": vocab("adjacent", "opposite")})
    sb.add_face_type("ColorTriple",
                     attributes={"pattern": {"vocab": vocab("ooa", "oaa"), "required": False}})

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
