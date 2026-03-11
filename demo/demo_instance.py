"""
demo/demo_instance.py

MTG color pentagon knowledge complex — full instance construction.
Layer 3: concrete data built using the models.mtg schema (layer 2)
and the kc framework (layer 1).

Authored in WP4. Returns a ready-to-use KnowledgeComplex for the Marimo notebook.

REQ-DEMO-01 through REQ-DEMO-05.
"""

from kc.schema import SchemaBuilder
from kc.graph import KnowledgeComplex
from models.mtg import build_mtg_schema, QUERIES_DIR


def build_mtg_instance(schema: SchemaBuilder | None = None) -> KnowledgeComplex:
    """Build the MTG color pentagon instance.

    If no schema is provided, builds one from models.mtg.
    """
    if schema is None:
        schema = build_mtg_schema()

    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])

    # REQ-DEMO-01: 5 Color vertices
    for color in ["White", "Blue", "Black", "Red", "Green"]:
        kc.add_vertex(color, type="Color")

    # REQ-DEMO-02: 5 adjacent edges (pentagon neighbors: W-U-B-R-G-W)
    adjacent = [
        ("WU", "White", "Blue"),
        ("UB", "Blue",  "Black"),
        ("BR", "Black", "Red"),
        ("RG", "Red",   "Green"),
        ("GW", "Green", "White"),
    ]
    for eid, v1, v2 in adjacent:
        kc.add_edge(eid, type="ColorPair",
                    vertices={v1, v2}, disposition="adjacent")

    # REQ-DEMO-03: 5 opposite edges (pentagon diagonals)
    opposite = [
        ("WB", "White", "Black"),
        ("WR", "White", "Red"),
        ("UG", "Blue",  "Green"),
        ("UR", "Blue",  "Red"),
        ("BG", "Black", "Green"),
    ]
    for eid, v1, v2 in opposite:
        kc.add_edge(eid, type="ColorPair",
                    vertices={v1, v2}, disposition="opposite")

    # REQ-DEMO-04: 10 valid ColorTriple faces (C(5,3)=10 triangles in K5).
    # No pattern attribute asserted (REQ-DEMO-05) — pattern is discovered via SPARQL.
    # NOTE: MTG explicitly enumerates all faces. This is a model-level choice,
    # not a framework invariant. See deferred issue in models/mtg/schema.py.
    faces = [
        ("WUB", ["WU", "UB", "WB"]),   # White-Blue-Black
        ("WUR", ["WU", "UR", "WR"]),   # White-Blue-Red
        ("WUG", ["WU", "UG", "GW"]),   # White-Blue-Green
        ("WBR", ["WB", "BR", "WR"]),   # White-Black-Red
        ("WBG", ["WB", "BG", "GW"]),   # White-Black-Green
        ("WRG", ["WR", "RG", "GW"]),   # White-Red-Green
        ("UBR", ["UB", "BR", "UR"]),   # Blue-Black-Red
        ("UBG", ["UB", "BG", "UG"]),   # Blue-Black-Green
        ("URG", ["UR", "RG", "UG"]),   # Blue-Red-Green
        ("BRG", ["BR", "RG", "BG"]),   # Black-Red-Green
    ]
    for fid, edges in faces:
        kc.add_face(fid, type="ColorTriple", boundary=edges)

    return kc


if __name__ == "__main__":
    kc = build_mtg_instance()
    print(kc.dump_graph())
