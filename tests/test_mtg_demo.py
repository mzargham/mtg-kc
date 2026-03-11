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

# Ground-truth face classification (sorted color triple → structure)
# wedge = two opposite edges + one adjacent (ooa); shard = one opposite + two adjacent (oaa)
# Computed from MTG color wheel: adjacent = pentagon edges, opposite = diagonals.
# 5 wedge + 5 shard = 10 total.
_FACE_STRUCTURES: dict[frozenset, str] = {
    frozenset({"White", "Blue", "Black"}):  "shard",
    frozenset({"White", "Blue", "Red"}):    "wedge",
    frozenset({"White", "Blue", "Green"}):  "shard",
    frozenset({"White", "Black", "Red"}):   "wedge",
    frozenset({"White", "Black", "Green"}): "wedge",
    frozenset({"White", "Red", "Green"}):   "shard",
    frozenset({"Blue", "Black", "Red"}):    "shard",
    frozenset({"Blue", "Black", "Green"}):  "wedge",
    frozenset({"Blue", "Red", "Green"}):    "wedge",
    frozenset({"Black", "Red", "Green"}):   "shard",
}


@pytest.fixture(scope="module")
def mtg_kc() -> KnowledgeComplex:
    """Full MTG demo instance with all 10 faces (no structure attribute asserted)."""
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

def test_no_structure_asserted(mtg_kc):
    """REQ-DEMO-05: no face has a structure attribute value in the raw instance.

    The OWL schema contains 'shard'/'wedge' in the rdfs:comment annotation for
    the structure property definition, but no instance should have a structure value.
    """
    ttl = mtg_kc.dump_graph()
    # No face instance should have mtg:structure "shard" or "wedge" as a triple value.
    # The schema annotation (rdfs:comment "Allowed values: shard, wedge") is expected.
    assert 'mtg:structure "shard"' not in ttl
    assert 'mtg:structure "wedge"' not in ttl


def test_structure_discovery_shard_wedge(mtg_kc):
    """REQ-DEMO-05, REQ-VV-05: SPARQL correctly classifies all 10 faces into shard/wedge."""
    df = mtg_kc.query("faces_by_edge_pattern")
    # Derive structure from the three disposition values
    def classify(row):
        dispositions = sorted([row["d1"], row["d2"], row["d3"]])
        # wedge: adjacent, opposite, opposite (2 opposite + 1 adjacent)
        # shard: adjacent, adjacent, opposite (1 opposite + 2 adjacent)
        if dispositions.count("opposite") == 2:
            return "wedge"
        elif dispositions.count("opposite") == 1:
            return "shard"
        else:
            return "unknown"
    df["discovered_structure"] = df.apply(classify, axis=1)
    assert set(df["discovered_structure"]) == {"shard", "wedge"}
    assert "unknown" not in df["discovered_structure"].values
    assert len(df[df["discovered_structure"] == "shard"]) == 5
    assert len(df[df["discovered_structure"] == "wedge"]) == 5


# --- REQ-DEMO-06, REQ-VV-03, REQ-VV-04 ---

@pytest.mark.skip(reason="WP5: promote demonstration not yet implemented")
def test_promote_causes_validation_fail(mtg_kc):
    """REQ-DEMO-06: after promoting structure to required, all 10 faces fail SHACL."""
    # promote_to_attribute modifies the schema in place;
    # use a fresh schema + instance for isolation
    sb = SchemaBuilder(namespace="mtg_promote")
    sb.add_vertex_type("Color")
    sb.add_edge_type("ColorPair",
                     attributes={"disposition": vocab("adjacent", "opposite")})
    sb.add_face_type("ColorTriple",
                     attributes={"structure": {"vocab": vocab("shard", "wedge"), "required": False}})

    sb.promote_to_attribute(
        type="ColorTriple",
        attribute="structure",
        vocab=vocab("shard", "wedge"),
        required=True,
    )
    pytest.skip("Full implementation pending WP5")
