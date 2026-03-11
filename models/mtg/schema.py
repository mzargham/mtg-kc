"""
models.mtg.schema — MTG color wheel schema definition.

Defines the domain-specific types for the MTG knowledge complex:
- Color (vertex type) with goal, method, persona, at_best, at_worst, example_behaviors
- ColorPair (edge type) with disposition, guild, theme, persona, at_best, at_worst, example_behaviors
- ColorTriple (face type) with clan, optional structure, persona, at_best, at_worst, example_behaviors

All types also have optional playstyle and example_decks attributes.

Design note — face enumeration policy:
    MTG explicitly enumerates all C(5,3)=10 ColorTriple faces in K5.
    This is an MTG model-level assertion, NOT a framework invariant.
    Other model families may leave faces absent (holes are meaningful).

Design note — structure replaces pattern:
    The original `pattern in {ooa, oaa}` was a topological placeholder.
    The MTG domain names this distinction: shard (3 consecutive colors,
    1 opposite + 2 adjacent edges) vs wedge (2 adjacent + 1 opposite color,
    2 opposite + 1 adjacent edge). We use the domain's own terminology.
"""

from kc.schema import SchemaBuilder, vocab, text


def build_mtg_schema() -> SchemaBuilder:
    """Build and return the MTG color wheel schema."""
    sb = SchemaBuilder(namespace="mtg")

    sb.add_vertex_type("Color", attributes={
        "goal": vocab("peace", "perfection", "satisfaction", "freedom", "harmony"),
        "method": vocab("order", "knowledge", "ruthlessness", "action", "acceptance"),
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })

    sb.add_edge_type("ColorPair", attributes={
        "disposition": vocab("adjacent", "opposite"),
        "guild": vocab(
            "azorius", "dimir", "rakdos", "gruul", "selesnya",
            "orzhov", "boros", "simic", "izzet", "golgari",
        ),
        "theme": vocab(
            "design", "growth_mindset", "independence", "authenticity", "community",
            "tribalism", "heroism", "truth_seeking", "creativity", "profanity",
        ),
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })

    sb.add_face_type("ColorTriple", attributes={
        "clan": vocab(
            "esper", "grixis", "jund", "naya", "bant",
            "mardu", "temur", "abzan", "jeskai", "sultai",
        ),
        # structure is optional — to be discovered, not pre-asserted (REQ-DEMO-05)
        "structure": {"vocab": vocab("shard", "wedge"), "required": False},
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })

    return sb
