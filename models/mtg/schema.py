"""
models.mtg.schema — MTG color wheel schema definition.

Defines the domain-specific types for the MTG knowledge complex:
- Color (vertex type)
- ColorPair (edge type) with disposition ∈ {adjacent, opposite}
- ColorTriple (face type) with optional pattern ∈ {ooa, oaa}
"""

from kc.schema import SchemaBuilder, vocab


def build_mtg_schema() -> SchemaBuilder:
    """Build and return the MTG color wheel schema."""
    sb = SchemaBuilder(namespace="mtg")
    sb.add_vertex_type("Color")
    sb.add_edge_type(
        "ColorPair",
        attributes={"disposition": vocab("adjacent", "opposite")},
    )
    sb.add_face_type(
        "ColorTriple",
        # pattern is optional here — to be discovered, not pre-asserted (REQ-DEMO-05)
        attributes={"pattern": {"vocab": vocab("ooa", "oaa"), "required": False}},
    )
    return sb
