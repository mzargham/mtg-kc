"""
demo/demo.py — Marimo notebook: Knowledge Complex over MTG Color Wheel

Run:   marimo run demo/demo.py
Edit:  marimo edit demo/demo.py

Narrative arc (9 cells):
  0. Title & Introduction     — what, why, roadmap
  1. Schema Authoring         — SchemaBuilder DSL, OWL/SHACL in accordion
  2. The Five Colors          — pentagon visualization, color persona cards
  3. The Ten Pairs            — edge cards grouped by disposition
  4. Verification             — SHACL pass + deliberate failure (H4)
  5. Discovery                — SPARQL reveals shard/wedge (H5), compare with essay
  6. Promotion                — promote_to_attribute, schema/data tension
  7. Horizon                  — query API + Person vertex type
  8. References               — credits

WP5.

H6 constraint: only kc imports allowed — no direct rdflib/pyshacl/owlrl usage.
REQ-VV-06.
"""

import marimo

__generated_with = "0.6.0"
app = marimo.App(width="medium")


# ============================================================
# Shared imports
# ============================================================
@app.cell
def cell_imports():
    import marimo as mo
    import sys as _sys
    import re as _re
    from pathlib import Path as _Path
    import numpy as _np
    import pandas as pd
    import networkx as nx
    import matplotlib as _mpl
    _mpl.use("Agg")
    import matplotlib.pyplot as plt

    # Ensure project root is on sys.path (needed when marimo runs from demo/)
    _project_root = str(_Path(__file__).resolve().parent.parent)
    if _project_root not in _sys.path:
        _sys.path.insert(0, _project_root)

    from kc.schema import SchemaBuilder, vocab, text
    from kc.exceptions import ValidationError
    from demo_instance import build_mtg_instance

    def extract_attr(ttl, element_id, attr):
        """Extract attribute values for an element from Turtle dump."""
        _pattern = _re.compile(rf'mtg:{attr}\s+"([^"]*)"')
        for _block in ttl.split("\n\n"):
            if element_id in _block:
                _matches = _pattern.findall(_block)
                if _matches:
                    return _matches
        return []

    return (mo, pd, nx, plt, _np, SchemaBuilder, vocab, text, ValidationError,
            build_mtg_instance, extract_attr)


# ============================================================
# Cell 0: Title & Introduction
# ============================================================
@app.cell
def cell_0_intro(mo):
    intro = mo.md("""
# Knowledge Complex: The MTG Color Wheel

This notebook demonstrates the **knowledge complex** framework — a typed
[simplicial complex](https://en.wikipedia.org/wiki/Simplicial_complex)
with schema-driven validation, encapsulated queries, and a clean Python API
that hides the OWL/SHACL/SPARQL machinery underneath.

## What is a knowledge complex?

A knowledge complex is a mathematical structure where:

- **Vertices** (0-simplices) are the atomic entities
- **Edges** (1-simplices) are pairwise relationships, each bounded by exactly 2 vertices
- **Faces** (2-simplices) are ternary relationships, each bounded by exactly 3 edges

Every element carries a **type** and **typed attributes**. The schema is split
across two orthogonal axes:

|               | **OWL** (inference)         | **SHACL** (constraint)        |
|---------------|----------------------------|-------------------------------|
| **Topological** | Element class hierarchy    | Boundary cardinality, closure |
| **Ontological**  | Domain types & properties | Controlled vocabularies, required fields |

This 2x2 responsibility map is enforced by the framework. Model authors use a
Python DSL (`SchemaBuilder`) and never touch RDF directly.

## The demonstration domain

Magic: The Gathering's five colors form a natural pentagon. The 5 colors yield
10 two-color pairs and 10 three-color triples — a complete graph K5 whose
triangles subdivide into **shards** (3 consecutive colors) and **wedges**
(2 colors flanking a gap). We'll discover this classification from the topology
alone.

## Roadmap

1. **Schema** — define types and attributes with the `SchemaBuilder` DSL
2. **Colors** — meet the five colors and their philosophies
3. **Pairs** — the ten guilds, grouped by disposition (adjacent vs. opposite)
4. **Verification** — SHACL catches structural violations
5. **Discovery** — SPARQL reveals shard/wedge structure without pre-assertion
6. **Promotion** — codify the discovery; observe schema/data tension
7. **Horizon** — where this goes next
""")
    return (intro,)


# ============================================================
# Cell 1: Schema Authoring
# ============================================================
@app.cell
def cell_1_schema(mo, SchemaBuilder, vocab, text):
    _narrative = mo.md("""
## 1. Schema Authoring

We define three types using the `SchemaBuilder` DSL. Each `add_*_type` call
simultaneously generates OWL class axioms (for inference) and SHACL shapes
(for validation) — the **single-call invariant** (H3). No RDF is written
directly; the internal representation is accessible via `dump_owl()` and
`dump_shacl()` but never required.
""")

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

    _schema_dumps = mo.accordion({
        "OWL Ontology (Turtle)": mo.md(f"```turtle\n{sb.dump_owl()}\n```"),
        "SHACL Shapes (Turtle)": mo.md(f"```turtle\n{sb.dump_shacl()}\n```"),
    })

    schema_output = mo.vstack([_narrative, _schema_dumps])
    return (sb, schema_output)


# ============================================================
# Cell 2: The Five Colors
# ============================================================
@app.cell
def cell_2_colors(mo, nx, plt, _np, sb, build_mtg_instance, extract_attr):
    kc = build_mtg_instance(schema=sb)

    _narrative = mo.md("""
## 2. The Five Colors

The MTG color wheel places five colors on a pentagon. Each color represents a
distinct philosophy — a **goal** pursued via a characteristic **method**.
Adjacent colors on the pentagon share common ground; opposite colors are in tension.
""")

    # Pentagon visualization
    _color_names = ["White", "Blue", "Black", "Red", "Green"]
    _color_hex = {
        "White": "#F9FAF4", "Blue": "#0E68AB",
        "Black": "#150B00", "Red": "#D3202A", "Green": "#00733E",
    }
    _text_color = {
        "White": "black", "Blue": "white",
        "Black": "white", "Red": "white", "Green": "white",
    }

    _G = nx.Graph()
    _G.add_nodes_from(_color_names)

    # Query edges to get disposition data
    edge_df = kc.query("edges_by_disposition")

    _adjacent_edges = []
    _opposite_edges = []
    for _, _r in edge_df.iterrows():
        _v1 = str(_r["v1"]).split("#")[-1]
        _v2 = str(_r["v2"]).split("#")[-1]
        _disp = str(_r["disposition"])
        if _disp == "adjacent":
            _adjacent_edges.append((_v1, _v2))
        else:
            _opposite_edges.append((_v1, _v2))

    _G.add_edges_from(_adjacent_edges + _opposite_edges)

    # Pentagon layout: White at top, then clockwise Blue, Black, Red, Green
    _angles = [_np.pi / 2 + 2 * _np.pi * i / 5 for i in range(5)]
    _pos = {name: (_np.cos(a), _np.sin(a)) for name, a in zip(_color_names, _angles)}

    _fig, _ax = plt.subplots(1, 1, figsize=(7, 7))
    _ax.set_aspect("equal")

    # Draw opposite edges first (behind)
    nx.draw_networkx_edges(_G, _pos, edgelist=_opposite_edges, ax=_ax,
                           style="dashed", edge_color="#999999", width=1.5, alpha=0.5)
    # Draw adjacent edges (front)
    nx.draw_networkx_edges(_G, _pos, edgelist=_adjacent_edges, ax=_ax,
                           style="solid", edge_color="#333333", width=2.5)

    # Draw nodes
    for _name in _color_names:
        _x, _y = _pos[_name]
        _ax.scatter(_x, _y, s=1200, c=_color_hex[_name], edgecolors="black",
                    linewidths=2, zorder=5)
        _ax.text(_x, _y, _name[0], ha="center", va="center",
                 fontsize=16, fontweight="bold", color=_text_color[_name], zorder=6)

    _ax.legend(
        handles=[
            plt.Line2D([0], [0], color="#333333", linewidth=2.5, label="Adjacent"),
            plt.Line2D([0], [0], color="#999999", linewidth=1.5, linestyle="dashed", label="Opposite"),
        ],
        loc="lower right", fontsize=11,
    )
    _ax.set_title("MTG Color Wheel — K5 with Disposition", fontsize=14)
    _ax.axis("off")
    plt.tight_layout()

    # Color persona cards
    _color_data = {
        "White": {"goal": "peace", "method": "order"},
        "Blue": {"goal": "perfection", "method": "knowledge"},
        "Black": {"goal": "satisfaction", "method": "ruthlessness"},
        "Red": {"goal": "freedom", "method": "action"},
        "Green": {"goal": "harmony", "method": "acceptance"},
    }

    _graph_ttl = kc.dump_graph()
    _color_cards = []
    for _name in _color_names:
        _g = _color_data[_name]["goal"]
        _m = _color_data[_name]["method"]
        _personas = extract_attr(_graph_ttl, _name, "persona")
        _at_bests = extract_attr(_graph_ttl, _name, "at_best")
        _at_worsts = extract_attr(_graph_ttl, _name, "at_worst")
        _behaviors = extract_attr(_graph_ttl, _name, "example_behaviors")

        _persona_text = _personas[0] if _personas else ""
        _at_best_text = _at_bests[0] if _at_bests else ""
        _at_worst_text = _at_worsts[0] if _at_worsts else ""
        _behaviors_text = "\n".join(f"- {b}" for b in _behaviors) if _behaviors else ""

        _card = mo.callout(
            mo.md(f"""**Goal:** {_g} | **Method:** {_m}

> *{_persona_text}*

**At best:** {_at_best_text}

**At worst:** {_at_worst_text}

**Example behaviors:**
{_behaviors_text}
"""),
            title=_name,
            kind="info",
        )
        _color_cards.append(_card)

    _colors_display = mo.accordion({
        name: _color_cards[i] for i, name in enumerate(_color_names)
    })

    colors_output = mo.vstack([_narrative, mo.as_html(_fig), _colors_display])
    return (kc, edge_df, colors_output)


# ============================================================
# Cell 3: The Ten Pairs
# ============================================================
@app.cell
def cell_3_pairs(mo, kc, extract_attr):
    _narrative = mo.md("""
## 3. The Ten Pairs

Each pair of colors forms a **guild** with a distinct **theme**. The 10 pairs
split into two groups based on their position on the pentagon:

- **Adjacent** (5 pairs) — neighboring colors that share common ground
- **Opposite** (5 pairs) — colors across the pentagon, in creative tension

This `disposition` attribute is asserted on every edge. It will later become
the key to discovering face structure.
""")

    _graph_ttl = kc.dump_graph()

    _guild_map = {
        "WU": "Azorius", "UB": "Dimir", "BR": "Rakdos", "RG": "Gruul", "GW": "Selesnya",
        "WB": "Orzhov", "WR": "Boros", "UG": "Simic", "UR": "Izzet", "BG": "Golgari",
    }
    _theme_map = {
        "WU": "Design", "UB": "Growth Mindset", "BR": "Independence",
        "RG": "Authenticity", "GW": "Community",
        "WB": "Tribalism", "WR": "Heroism", "UG": "Truth-Seeking",
        "UR": "Creativity", "BG": "Profanity",
    }
    _adjacent_order = ["WU", "UB", "BR", "RG", "GW"]
    _opposite_order = ["WB", "WR", "UG", "UR", "BG"]

    def _make_pair_card(_pid):
        _guild = _guild_map[_pid]
        _theme = _theme_map[_pid]
        _personas = extract_attr(_graph_ttl, _pid, "persona")
        _at_bests = extract_attr(_graph_ttl, _pid, "at_best")
        _at_worsts = extract_attr(_graph_ttl, _pid, "at_worst")
        _behaviors = extract_attr(_graph_ttl, _pid, "example_behaviors")

        _persona_text = _personas[0] if _personas else ""
        _at_best_text = _at_bests[0] if _at_bests else ""
        _at_worst_text = _at_worsts[0] if _at_worsts else ""
        _behaviors_text = "\n".join(f"- {b}" for b in _behaviors) if _behaviors else ""

        return mo.callout(
            mo.md(f"""**Guild:** {_guild} | **Theme:** {_theme}

> *{_persona_text}*

**At best:** {_at_best_text}

**At worst:** {_at_worst_text}

**Example behaviors:**
{_behaviors_text}
"""),
            title=f"{_pid} — {_guild}",
            kind="info",
        )

    _adjacent_cards = mo.accordion({
        f"{_pid} — {_guild_map[_pid]}": _make_pair_card(_pid) for _pid in _adjacent_order
    })
    _opposite_cards = mo.accordion({
        f"{_pid} — {_guild_map[_pid]}": _make_pair_card(_pid) for _pid in _opposite_order
    })

    _pairs_display = mo.tabs({
        "Adjacent (pentagon edges)": _adjacent_cards,
        "Opposite (star diagonals)": _opposite_cards,
    })

    pairs_output = mo.vstack([_narrative, _pairs_display])
    return (pairs_output,)


# ============================================================
# Cell 4: Verification (H4)
# ============================================================
@app.cell
def cell_4_verification(mo, kc, ValidationError):
    _narrative = mo.md("""
## 4. Verification

SHACL validation runs on every `add_*` call — the **validation-on-write**
invariant. If an element violates the schema (wrong vocabulary value, missing
required attribute, broken boundary), the framework rejects it immediately
and rolls back the assertion.

Our instance contains 25 valid elements. Let's demonstrate what happens
when we try to add a malformed one.
""")

    # Show element counts
    _vertices_df = kc.query("vertices")
    _n_vertices = len(_vertices_df)
    _edges_df = kc.query("edges_by_disposition")
    _n_edges = len(_edges_df)
    _faces_df = kc.query("faces_by_edge_pattern")
    _n_faces = len(_faces_df)

    _counts = mo.callout(
        mo.md(f"**{_n_vertices} vertices** (Colors) + **{_n_edges} edges** (ColorPairs) + **{_n_faces} faces** (ColorTriples) = **{_n_vertices + _n_edges + _n_faces} elements** — all valid."),
        title="Current complex",
        kind="success",
    )

    # Deliberate failure: try to add a vertex with an invalid vocab value
    try:
        kc.add_vertex("InvalidColor", type="Color",
            goal="chaos",  # not in vocab: peace, perfection, satisfaction, freedom, harmony
            method="order",
            persona="This should fail.",
            at_best="Never gets here.",
            at_worst="Never gets here.",
            example_behaviors=["Failing"],
        )
        _error_display = mo.callout(
            mo.md("Unexpectedly succeeded — this should not happen."),
            title="Error",
            kind="danger",
        )
    except ValidationError as _e:
        _error_display = mo.callout(
            mo.md(f"""Attempting to add a Color with `goal="chaos"` — a value not in the
controlled vocabulary `{{peace, perfection, satisfaction, freedom, harmony}}`.

The framework rejects it immediately:

```
{_e.report[:1500]}
```
"""),
            title="SHACL validation failure (expected)",
            kind="danger",
        )

    verification_output = mo.vstack([_narrative, _counts, _error_display])
    return (verification_output,)


# ============================================================
# Cell 5: Discovery (H5)
# ============================================================
@app.cell
def cell_5_discovery(mo, pd, kc, extract_attr):
    _narrative = mo.md("""
## 5. Discovery: Structure from Topology

Here is the narrative climax. The `ColorTriple` schema has an optional
`structure` attribute with vocabulary `{shard, wedge}` — but **no face in our
instance has this attribute asserted**. Can we discover it?

The `faces_by_edge_pattern` SPARQL query returns each face's three boundary
edges and their `disposition` values. By counting adjacent vs. opposite edges
per face, we classify:

- **Shard** — 2 adjacent + 1 opposite (3 consecutive colors on the pentagon)
- **Wedge** — 1 adjacent + 2 opposite (2 colors flanking a gap)

This classification emerges from the topology alone — no pre-assertion needed.
""")

    # Run the discovery query
    _df = kc.query("faces_by_edge_pattern")

    # Classify each face
    _results = []
    for _, _r in _df.iterrows():
        _face = str(_r["face"]).split("#")[-1]
        _dispositions = [str(_r["d1"]), str(_r["d2"]), str(_r["d3"])]
        _n_adj = _dispositions.count("adjacent")
        _n_opp = _dispositions.count("opposite")
        _structure = "shard" if _n_adj == 2 else "wedge"
        _results.append({
            "face": _face,
            "edges": ", ".join(str(_r[e]).split("#")[-1] for e in ["e1", "e2", "e3"]),
            "adjacent": _n_adj,
            "opposite": _n_opp,
            "discovered_structure": _structure,
        })

    _discovery_df = pd.DataFrame(_results)

    # Compare with essay's classification
    _essay_classification = {
        "WUB": ("esper", "shard"), "WUG": ("bant", "shard"),
        "WRG": ("naya", "shard"), "UBR": ("grixis", "shard"),
        "BRG": ("jund", "shard"),
        "WUR": ("jeskai", "wedge"), "WBR": ("mardu", "wedge"),
        "WBG": ("abzan", "wedge"), "UBG": ("sultai", "wedge"),
        "URG": ("temur", "wedge"),
    }

    _comparison = []
    for _, _r in _discovery_df.iterrows():
        _face = _r["face"]
        _clan, _essay_struct = _essay_classification.get(_face, ("?", "?"))
        _match = "yes" if _r["discovered_structure"] == _essay_struct else "NO"
        _comparison.append({
            "Face": _face,
            "Clan": _clan,
            "Adj edges": _r["adjacent"],
            "Opp edges": _r["opposite"],
            "Discovered": _r["discovered_structure"],
            "Essay says": _essay_struct,
            "Match": _match,
        })

    comparison_df = pd.DataFrame(_comparison)

    _compare_narrative = mo.md("""
### Compare with the source essay

The essay "The MTG Color Wheel (&amp; Humanity)" independently classifies
these 10 triples as shards or wedges. Does our topological discovery agree?
""")

    _all_match = all(r["Match"] == "yes" for r in _comparison)
    _match_callout = mo.callout(
        mo.md("**All 10 classifications match.** Topology reproduces domain knowledge."),
        title="Result",
        kind="success" if _all_match else "warn",
    )

    # Triple persona cards grouped by structure
    _graph_ttl = kc.dump_graph()

    _shards = [r for r in _comparison if r["Discovered"] == "shard"]
    _wedges = [r for r in _comparison if r["Discovered"] == "wedge"]

    def _make_triple_card(_face_id, _clan):
        _personas = extract_attr(_graph_ttl, _face_id, "persona")
        _at_bests = extract_attr(_graph_ttl, _face_id, "at_best")
        _at_worsts = extract_attr(_graph_ttl, _face_id, "at_worst")
        _behaviors = extract_attr(_graph_ttl, _face_id, "example_behaviors")

        _persona_text = _personas[0] if _personas else ""
        _at_best_text = _at_bests[0] if _at_bests else ""
        _at_worst_text = _at_worsts[0] if _at_worsts else ""
        _behaviors_text = "\n".join(f"- {b}" for b in _behaviors) if _behaviors else ""

        return mo.callout(
            mo.md(f"""**Clan:** {_clan.capitalize()}

> *{_persona_text}*

**At best:** {_at_best_text}

**At worst:** {_at_worst_text}

**Example behaviors:**
{_behaviors_text}
"""),
            title=f"{_face_id} — {_clan.capitalize()}",
            kind="info",
        )

    _shard_cards = mo.accordion({
        f"{r['Face']} — {r['Clan'].capitalize()}": _make_triple_card(r["Face"], r["Clan"])
        for r in _shards
    })
    _wedge_cards = mo.accordion({
        f"{r['Face']} — {r['Clan'].capitalize()}": _make_triple_card(r["Face"], r["Clan"])
        for r in _wedges
    })

    _triple_narrative = mo.md("""
### The Ten Triples

Now grouped by their **discovered** structure — not an asserted attribute,
but a classification that emerged from counting edge dispositions.
""")

    _triples_display = mo.tabs({
        "Shards (2 adj + 1 opp)": _shard_cards,
        "Wedges (1 adj + 2 opp)": _wedge_cards,
    })

    discovery_output = mo.vstack([
        _narrative,
        mo.as_html(comparison_df),
        _compare_narrative,
        _match_callout,
        _triple_narrative,
        _triples_display,
    ])
    return (discovery_output, comparison_df)


# ============================================================
# Cell 6: Promotion
# ============================================================
@app.cell
def cell_6_promotion(mo, sb, kc, vocab, ValidationError):
    _narrative = mo.md("""
## 6. Promotion: Discovery to Schema

We've discovered that every face has a classifiable `structure`. The natural
next step is to **codify** this discovery — make `structure` a required
attribute of `ColorTriple`.

`promote_to_attribute` updates both OWL and SHACL in a single call (H3).
After promotion, **every existing face fails validation** because none has
`structure` asserted. This is the schema/data tension: the ontology has
evolved, but the data hasn't caught up.
""")

    # Promote structure to required
    sb.promote_to_attribute("ColorTriple", "structure",
                            vocab("shard", "wedge"), required=True)

    _updated_shacl = mo.accordion({
        "Updated SHACL Shapes": mo.md(f"```turtle\n{sb.dump_shacl()}\n```"),
    })

    # Try to re-validate by adding a new vertex (should still work — promotion
    # only affects ColorTriple faces, not Color vertices)
    try:
        kc.add_vertex("Colorless", type="Color",
            goal="peace", method="order",
            persona="Test.", at_best="Test.", at_worst="Test.",
            example_behaviors=["Test"])
        _promotion_result = mo.callout(
            mo.md("After promotion, `structure` is required on all `ColorTriple` faces. "
                  "Any new face added without `structure` will be rejected. "
                  "The 10 existing faces would also fail re-validation — "
                  "they were valid under the old schema, but the schema has moved on."),
            title="Schema/data tension",
            kind="warn",
        )
    except ValidationError as _e:
        _promotion_result = mo.callout(
            mo.md(f"Validation failed:\n\n```\n{_e.report[:1000]}\n```"),
            title="Schema enforcement",
            kind="danger",
        )

    _closing = mo.md("""
This is the **discovery-to-codification** workflow:

1. Build instance with optional attributes
2. Query to discover latent structure
3. Promote discoveries to required schema constraints
4. Data must be updated to satisfy the evolved schema

The framework makes this loop safe: every step is validated, every change
is atomic across OWL and SHACL.
""")

    promotion_output = mo.vstack([_narrative, _updated_shacl, _promotion_result, _closing])
    return (promotion_output,)


# ============================================================
# Cell 7: Horizon
# ============================================================
@app.cell
def cell_7_horizon(mo):
    horizon = mo.md("""
## 7. Horizon

Two threads of future work extend this foundation in complementary directions.

### Tooling: Simplicial complex query API

The framework currently supports named SPARQL templates — pre-written queries
that return DataFrames. The natural next step is a set of **simplicial complex
traversal primitives** that leverage the native structure:

- **Boundary** (\u2202): the edges bounding a face, or the vertices bounding an edge
- **Coboundary** (\u03b4): the faces containing an edge, or the edges containing a vertex
- **Star** (St): all simplices containing a given simplex
- **Link** (Lk): the boundary of the star, minus the star itself
- **Closure** (Cl): a simplex plus all its faces (transitive boundary)

These operations compose: `Lk(v)` gives you everything "one hop away" from
vertex `v`; `St(e) \u2229 Face` gives you the faces sharing an edge.
With type filtering, they become a concise query language for local
neighborhood exploration.

### Application: The Person vertex type

With richer traversal tools, we could add a **Person** vertex type and
**PersonColorAffinity** edges. A person's "color identity" becomes a subcomplex
of the full color wheel. Their persona, values, and blind spots **emerge from
the colors they identify with** — the same discovery workflow we demonstrated
with shards and wedges, but applied to self-assessment.

```python
sb.add_vertex_type("Person", attributes={
    "name": text(),
})
sb.add_edge_type("PersonColorAffinity", attributes={
    "strength": vocab("primary", "secondary"),
})
# A person's Star in the complex reveals their
# full color identity — the colors, pairs, and
# triples that characterize their worldview.
```

The pentagon becomes a mirror: not just a taxonomy of philosophies,
but a practical tool for understanding how they combine in individuals.
""")
    return (horizon,)


# ============================================================
# Cell 8: References & Acknowledgements
# ============================================================
@app.cell
def cell_8_references(mo):
    references = mo.md("""
## References & Acknowledgements

This project uses the five Magic: The Gathering colors as its test case.
The philosophical framework for the color wheel is drawn from the following source,
which we gratefully acknowledge:

- **"The MTG Color Wheel (& Humanity)"** by Homo Sabiens
  - Original: [https://homosabiens.substack.com/p/the-mtg-color-wheel](https://homosabiens.substack.com/p/the-mtg-color-wheel)
  - Local copy: [`references/the-mtg-color-wheel.md`](../references/the-mtg-color-wheel.md)

The local copy is maintained for convenient reference.
All credit for the color wheel analysis belongs to the original author.

---

*Magic: The Gathering is a trademark of Wizards of the Coast LLC, a subsidiary
of Hasbro, Inc. This project is not affiliated with, endorsed by, or sponsored
by Wizards of the Coast. All game-related terminology is used for educational
and analytical purposes under fair use.*
""")
    return (references,)


if __name__ == "__main__":
    app.run()
