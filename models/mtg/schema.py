"""
models.mtg.schema — MTG color wheel schema definition.

Defines the domain-specific types for the MTG knowledge complex:
- Color (vertex type) with goal, method, persona, at_best, at_worst, example_behaviors
- ColorPair (edge type) with disposition, guild, theme, synergies, tensions,
  persona, at_best, at_worst, example_behaviors
- ColorTriple (face type) with clan, optional structure, thematic_triad, closure,
  persona, at_best, at_worst, example_behaviors

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

Design note — thematic_triad constraint:
    thematic_triad on ColorTriple must equal exactly the themes of the three
    bounding ColorPair edges. This is enforced by two SPARQL SHACL constraints
    (one per direction of the set-equality check). The stored values can be
    verified by re-deriving them from topology — the derivation IS the check.
"""

from knowledgecomplex import SchemaBuilder, vocab, text

# Shared theme vocabulary — used in both ColorPair.theme and
# ColorTriple.thematic_triad to enforce referential consistency.
_THEMES = (
    "design", "growth_mindset", "independence", "authenticity", "community",
    "tribalism", "heroism", "truth_seeking", "creativity", "profanity",
)

_KC = "https://example.org/kc#"
_MTG = "https://example.org/mtg#"

_THEMATIC_TRIAD_MISSING = f"""\
    PREFIX kc: <{_KC}>
    PREFIX mtg: <{_MTG}>
    SELECT $this WHERE {{
        $this kc:boundedBy ?edge .
        ?edge mtg:theme ?edgeTheme .
        FILTER NOT EXISTS {{
            $this mtg:thematic_triad ?edgeTheme .
        }}
    }}
"""

_THEMATIC_TRIAD_EXTRA = f"""\
    PREFIX kc: <{_KC}>
    PREFIX mtg: <{_MTG}>
    SELECT $this WHERE {{
        $this mtg:thematic_triad ?triadTheme .
        FILTER NOT EXISTS {{
            $this kc:boundedBy ?edge .
            ?edge mtg:theme ?triadTheme .
        }}
    }}
"""


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
        "theme": vocab(*_THEMES),
        "synergies": text(),
        "tensions": text(),
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
        "thematic_triad": vocab(*_THEMES, multiple=True),
        "closure": text(),
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })

    # SPARQL constraint: thematic_triad must exactly match the themes of
    # the bounding edges. Two directions enforced separately.
    sb.add_sparql_constraint(
        "ColorTriple",
        _THEMATIC_TRIAD_MISSING,
        "thematic_triad is missing at least one theme from a bounding edge.",
    )
    sb.add_sparql_constraint(
        "ColorTriple",
        _THEMATIC_TRIAD_EXTRA,
        "thematic_triad contains a value that is not a theme of any bounding edge.",
    )

    return sb
