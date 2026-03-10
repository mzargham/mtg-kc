"""
demo/demo_instance.py

MTG color pentagon knowledge complex — full instance construction.
Authored in WP4. Returns a ready-to-use KnowledgeComplex for the Marimo notebook.

REQ-DEMO-01 through REQ-DEMO-05.
"""

from kc.schema import SchemaBuilder, vocab
from kc.graph import KnowledgeComplex


def build_mtg_schema() -> SchemaBuilder:
    sb = SchemaBuilder(namespace="mtg")
    sb.add_vertex_type("Color")
    sb.add_edge_type(
        "Relationship",
        attributes={"disposition": vocab("adjacent", "opposite")},
    )
    sb.add_face_type(
        "ColorTriple",
        # pattern is optional here — to be discovered, not pre-asserted (REQ-DEMO-05)
        attributes={"pattern": vocab("ooa", "oaa"), "required": False},
    )
    return sb


def build_mtg_instance(schema: SchemaBuilder) -> KnowledgeComplex:
    kc = KnowledgeComplex(schema=schema)

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
    for eid, src, tgt in adjacent:
        kc.add_edge(eid, type="Relationship",
                    source=src, target=tgt, disposition="adjacent")

    # REQ-DEMO-03: 5 opposite edges (pentagon diagonals)
    opposite = [
        ("WB", "White", "Black"),
        ("WR", "White", "Red"),
        ("UG", "Blue",  "Green"),
        ("UR", "Blue",  "Red"),
        ("BG", "Black", "Green"),
    ]
    for eid, src, tgt in opposite:
        kc.add_edge(eid, type="Relationship",
                    source=src, target=tgt, disposition="opposite")

    # REQ-DEMO-04: 10 valid ColorTriple faces
    # Each face is a valid closed triangle in the 10-edge graph.
    # No pattern attribute asserted (REQ-DEMO-05).
    # TODO (WP4): enumerate all 10 triangles and uncomment.
    # The 10 triangles are the C(5,3)=10 color triples for which all 3 pairs
    # have edges (they all do, since the graph is K5). List them explicitly:
    #
    # faces = [
    #     ("WUB", ["WU", "UB", "WB"]),  # White-Blue-Black
    #     ("WUR", ["WU", "UR", "WR"]),  # White-Blue-Red
    #     ("WUG", ["WU", "UG", "GW"]),  # White-Blue-Green  (GW reversed → need directed check)
    #     ...
    # ]
    # for fid, edges in faces:
    #     kc.add_face(fid, type="ColorTriple", edges=edges)

    return kc


if __name__ == "__main__":
    sb = build_mtg_schema()
    kc = build_mtg_instance(sb)
    print(kc.dump_graph())
