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
    import numpy as np
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
        """Extract attribute values for an element from Turtle dump.

        Handles rdflib Turtle serialization where multiple values for the
        same property are comma-separated across lines.
        """
        _prop_pattern = _re.compile(
            rf'mtg:{attr}\s+((?:"[^"]*"(?:\s*,\s*)*\s*)+)',
            _re.DOTALL,
        )
        _val_pattern = _re.compile(r'"([^"]*)"')
        for _block in ttl.split("\n\n"):
            if element_id in _block:
                _match = _prop_pattern.search(_block)
                if _match:
                    return _val_pattern.findall(_match.group(1))
        return []

    return (mo, pd, nx, plt, np, SchemaBuilder, vocab, text, ValidationError,
            build_mtg_instance, extract_attr)


# ============================================================
# Cell 0: Title & Introduction
# ============================================================
@app.cell
def cell_0_intro(mo):
    mo.md("""
# Knowledge Complex: The MTG Color Wheel

This notebook demonstrates the **knowledge complex** framework — a typed
[simplicial complex](https://en.wikipedia.org/wiki/Simplicial_complex)
with schema-driven verification, encapsulated queries, and a clean Python API
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

## Table of Contents

1. **Schema** — define types and attributes with the `SchemaBuilder` DSL
2. **Colors** — meet the five colors and their philosophies
3. **Pairs** — the ten guilds, grouped by disposition (adjacent vs. opposite)
4. **Verification** — SHACL catches structural violations
5. **Discovery** — SPARQL reveals shard/wedge structure without pre-assertion
6. **Promotion** — codify the discovery; observe schema/data tension
7. **Horizon** — where this goes next

> **Note:** Initial load takes ~30–60 seconds while the framework verifies
> all elements against the SHACL schema. A spinner will appear below
> while this runs.
""")
    return


# ============================================================
# Cell 1: Schema Authoring + Instance Build
# ============================================================
@app.cell
def cell_1_schema(mo, SchemaBuilder, vocab, text, build_mtg_instance):
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

    # Build the full instance (25 elements — takes ~30s for SHACL verification)
    with mo.status.spinner(title="Building knowledge complex",
                           subtitle="Verifying elements against SHACL schema ..."):
        kc = build_mtg_instance(schema=sb)

    mo.vstack([
        mo.md("""
## 1. Schema Authoring

We define three types using the `SchemaBuilder` DSL. Each `add_*_type` call
simultaneously generates OWL class axioms (for inference) and SHACL shapes
(for verification) — the **single-call invariant** (H3). No RDF is written
directly; the internal representation is accessible via `dump_owl()` and
`dump_shacl()` but never required.
"""),
        mo.accordion({
            "OWL Ontology (Turtle)": mo.md(f"```turtle\n{sb.dump_owl()}\n```"),
            "SHACL Shapes (Turtle)": mo.md(f"```turtle\n{sb.dump_shacl()}\n```"),
        }),
    ])
    return sb, kc


# ============================================================
# Cell 2: The Five Colors
# ============================================================
@app.cell
def cell_2_colors(mo, nx, plt, np, kc, extract_attr):
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

    _edge_df = kc.query("edges_by_disposition")
    _adjacent_edges = []
    _opposite_edges = []
    for _, _r in _edge_df.iterrows():
        _v1 = str(_r["v1"]).split("#")[-1]
        _v2 = str(_r["v2"]).split("#")[-1]
        if str(_r["disposition"]) == "adjacent":
            _adjacent_edges.append((_v1, _v2))
        else:
            _opposite_edges.append((_v1, _v2))

    _G.add_edges_from(_adjacent_edges + _opposite_edges)

    _angles = [np.pi / 2 + 2 * np.pi * i / 5 for i in range(5)]
    _pos = {n: (np.cos(a), np.sin(a)) for n, a in zip(_color_names, _angles)}

    _fig, _ax = plt.subplots(1, 1, figsize=(7, 7))
    _ax.set_aspect("equal")
    nx.draw_networkx_edges(_G, _pos, edgelist=_opposite_edges, ax=_ax,
                           style="dashed", edge_color="#999999", width=1.5, alpha=0.5)
    nx.draw_networkx_edges(_G, _pos, edgelist=_adjacent_edges, ax=_ax,
                           style="solid", edge_color="#333333", width=2.5)
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
        _persona = (extract_attr(_graph_ttl, _name, "persona") or [""])[0]
        _at_best = (extract_attr(_graph_ttl, _name, "at_best") or [""])[0]
        _at_worst = (extract_attr(_graph_ttl, _name, "at_worst") or [""])[0]
        _behaviors = extract_attr(_graph_ttl, _name, "example_behaviors")
        _btext = "\n".join(f"- {b}" for b in _behaviors) if _behaviors else ""

        _color_cards.append(mo.callout(
            mo.md(f"""### {_name}

**Goal:** {_g} | **Method:** {_m}

> *{_persona}*

**At best:** {_at_best}

**At worst:** {_at_worst}

**Example behaviors:**
{_btext}
"""),
            kind="info",
        ))

    mo.vstack([
        mo.md("""
## 2. The Five Colors

The MTG color wheel places five colors on a pentagon. Each color represents a
distinct philosophy — a **goal** pursued via a characteristic **method**.
Adjacent colors on the pentagon share common ground; opposite colors are in tension.
"""),
        mo.as_html(_fig),
        mo.accordion({n: _color_cards[i] for i, n in enumerate(_color_names)}),
    ])
    return


# ============================================================
# Cell 3: The Ten Pairs
# ============================================================
@app.cell
def cell_3_pairs(mo, kc, extract_attr):
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

    def _make_pair_card(_pid):
        _guild = _guild_map[_pid]
        _theme = _theme_map[_pid]
        _persona = (extract_attr(_graph_ttl, _pid, "persona") or [""])[0]
        _at_best = (extract_attr(_graph_ttl, _pid, "at_best") or [""])[0]
        _at_worst = (extract_attr(_graph_ttl, _pid, "at_worst") or [""])[0]
        _behaviors = extract_attr(_graph_ttl, _pid, "example_behaviors")
        _btext = "\n".join(f"- {b}" for b in _behaviors) if _behaviors else ""
        return mo.callout(
            mo.md(f"""### {_pid} — {_guild}

**Theme:** {_theme}

> *{_persona}*

**At best:** {_at_best}

**At worst:** {_at_worst}

**Example behaviors:**
{_btext}
"""),
            kind="info",
        )

    _adj = ["WU", "UB", "BR", "RG", "GW"]
    _opp = ["WB", "WR", "UG", "UR", "BG"]

    mo.vstack([
        mo.md("""
## 3. The Ten Pairs

Each pair of colors forms a **guild** with a distinct **theme**. The 10 pairs
split into two groups based on their position on the pentagon:

- **Adjacent** (5 pairs) — neighboring colors that share common ground
- **Opposite** (5 pairs) — colors across the pentagon, in creative tension

This `disposition` attribute is asserted on every edge. It will later become
the key to discovering face structure.
"""),
        mo.ui.tabs({
            "Adjacent (pentagon edges)": mo.accordion({
                f"{p} — {_guild_map[p]}": _make_pair_card(p) for p in _adj
            }),
            "Opposite (star diagonals)": mo.accordion({
                f"{p} — {_guild_map[p]}": _make_pair_card(p) for p in _opp
            }),
        }),
    ])
    return


# ============================================================
# Cell 4: Verification (H4)
# ============================================================
@app.cell
def cell_4_verification(mo, kc, ValidationError):
    _n_v = len(kc.query("vertices"))
    _n_e = len(kc.query("edges_by_disposition"))
    _n_f = len(kc.query("faces_by_edge_pattern"))

    _counts = mo.callout(
        mo.md(f"**Current complex:** {_n_v} vertices (Colors) + {_n_e} edges (ColorPairs) + {_n_f} faces (ColorTriples) = **{_n_v + _n_e + _n_f} elements** — all valid."),
        kind="success",
    )

    try:
        kc.add_vertex("InvalidColor", type="Color",
            goal="chaos", method="order",
            persona="This should fail.", at_best="N/A.", at_worst="N/A.",
            example_behaviors=["Failing"])
        _error = mo.callout(mo.md("Unexpectedly succeeded."), kind="danger")
    except ValidationError as _e:
        _error = mo.callout(
            mo.md(f"""**SHACL verification failure (expected)**

Attempting to add a Color with `goal="chaos"` — a value not in the
controlled vocabulary `{{peace, perfection, satisfaction, freedom, harmony}}`.

The framework rejects it immediately:

```
{_e.report[:1500]}
```
"""),
            kind="danger",
        )

    mo.vstack([
        mo.md("""
## 4. Verification

SHACL verification runs on every `add_*` call — the **verification-on-write**
invariant. If an element violates the schema (wrong vocabulary value, missing
required attribute, broken boundary), the framework rejects it immediately
and rolls back the assertion.

Our instance contains 25 valid elements. Let's demonstrate what happens
when we try to add a malformed one.
"""),
        _counts,
        _error,
    ])
    return


# ============================================================
# Cell 5: Discovery (H5)
# ============================================================
@app.cell
def cell_5_discovery(mo, pd, kc, extract_attr):
    _df = kc.query("faces_by_edge_pattern")

    _results = []
    for _, _r in _df.iterrows():
        _face = str(_r["face"]).split("#")[-1]
        _disps = [str(_r["d1"]), str(_r["d2"]), str(_r["d3"])]
        _n_adj = _disps.count("adjacent")
        _n_opp = _disps.count("opposite")
        _results.append({
            "face": _face,
            "adjacent": _n_adj,
            "opposite": _n_opp,
            "discovered_structure": "shard" if _n_adj == 2 else "wedge",
        })
    _discovery_df = pd.DataFrame(_results)

    _essay = {
        "WUB": ("esper", "shard"), "WUG": ("bant", "shard"),
        "WRG": ("naya", "shard"), "UBR": ("grixis", "shard"),
        "BRG": ("jund", "shard"),
        "WUR": ("jeskai", "wedge"), "WBR": ("mardu", "wedge"),
        "WBG": ("abzan", "wedge"), "UBG": ("sultai", "wedge"),
        "URG": ("temur", "wedge"),
    }

    _comparison = []
    for _, _r in _discovery_df.iterrows():
        _f = _r["face"]
        _clan, _es = _essay.get(_f, ("?", "?"))
        _comparison.append({
            "Face": _f, "Clan": _clan,
            "Adj edges": _r["adjacent"], "Opp edges": _r["opposite"],
            "Discovered": _r["discovered_structure"],
            "Community says": _es,
            "Match": "yes" if _r["discovered_structure"] == _es else "NO",
        })
    _comp_df = pd.DataFrame(_comparison)

    _all_match = all(r["Match"] == "yes" for r in _comparison)

    # Triple persona cards
    _graph_ttl = kc.dump_graph()
    _shards = [r for r in _comparison if r["Discovered"] == "shard"]
    _wedges = [r for r in _comparison if r["Discovered"] == "wedge"]

    def _make_triple_card(_fid, _clan):
        _persona = (extract_attr(_graph_ttl, _fid, "persona") or [""])[0]
        _at_best = (extract_attr(_graph_ttl, _fid, "at_best") or [""])[0]
        _at_worst = (extract_attr(_graph_ttl, _fid, "at_worst") or [""])[0]
        _behaviors = extract_attr(_graph_ttl, _fid, "example_behaviors")
        _btext = "\n".join(f"- {b}" for b in _behaviors) if _behaviors else ""
        return mo.callout(
            mo.md(f"""### {_fid} — {_clan.capitalize()}

> *{_persona}*

**At best:** {_at_best}

**At worst:** {_at_worst}

**Example behaviors:**
{_btext}
"""),
            kind="info",
        )

    mo.vstack([
        mo.md("""
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
"""),
        mo.as_html(_comp_df),
        mo.md("""
### Compare with MTG community knowledge

The terms "shard" and "wedge" are not from the essay — they come from
Magic: The Gathering community lore (named after the card sets *Shards of Alara*
and the wedge-colored *Khans of Tarkir* clans). We initially called them "ooa" and "oaa" for opposite-opposite-adjacent and opposite-adjacent-adjacent, respectively. Our knowledge complex
independently surfaced a relevant topological feature but the MTG community forums validated that this feature is semantically meaningful.
"""),
        mo.callout(
            mo.md("**Result:** All 10 classifications match. Topology reproduces community knowledge."),
            kind="success" if _all_match else "warn",
        ),
        mo.md("""
### The Ten Triples

Now grouped by their **discovered** structure — not an asserted attribute,
but a classification that emerged from counting edge dispositions.
"""),
        mo.ui.tabs({
            "Shards (2 adj + 1 opp)": mo.accordion({
                f"{r['Face']} — {r['Clan'].capitalize()}": _make_triple_card(r["Face"], r["Clan"])
                for r in _shards
            }),
            "Wedges (1 adj + 2 opp)": mo.accordion({
                f"{r['Face']} — {r['Clan'].capitalize()}": _make_triple_card(r["Face"], r["Clan"])
                for r in _wedges
            }),
        }),
    ])
    return


# ============================================================
# Cell 6: Promotion
# ============================================================
@app.cell
def cell_6_promotion(mo, sb, kc, vocab, ValidationError):
    sb.promote_to_attribute("ColorTriple", "structure",
                            vocab("shard", "wedge"), required=True)

    try:
        kc.add_vertex("Colorless", type="Color",
            goal="peace", method="order",
            persona="Test.", at_best="Test.", at_worst="Test.",
            example_behaviors=["Test"])
        _result = mo.callout(
            mo.md("**Schema/data tension:** After promotion, `structure` is required on all `ColorTriple` faces. "
                  "Any new face added without `structure` will be rejected. "
                  "The 10 existing faces would also fail re-verification — "
                  "they were valid under the old schema, but the schema has moved on."),
            kind="warn",
        )
    except ValidationError as _e:
        _result = mo.callout(
            mo.md(f"**Schema enforcement:** Verification failed:\n\n```\n{_e.report[:1000]}\n```"),
            kind="danger",
        )

    mo.vstack([
        mo.md("""
## 6. Promotion: Discovery to Schema

We've discovered that every face has a classifiable `structure`. The natural
next step is to **codify** this discovery — make `structure` a required
attribute of `ColorTriple`.

`promote_to_attribute` updates both OWL and SHACL in a single call (H3).
After promotion, **every existing face fails verification** because none has
`structure` asserted. This is the schema/data tension: the ontology has
evolved, but the data hasn't caught up.
"""),
        mo.accordion({
            "Updated SHACL Shapes": mo.md(f"```turtle\n{sb.dump_shacl()}\n```"),
        }),
        _result,
        mo.md("""
This is the **discovery-to-codification** workflow:

1. Build instance with optional attributes
2. Query to discover latent structure
3. Promote discoveries to required schema constraints
4. Data must be updated to satisfy the evolved schema

The framework makes this loop safe: every step is verified, every change
is atomic across OWL and SHACL.
"""),
    ])
    return


# ============================================================
# Cell 7: Horizon
# ============================================================
@app.cell
def cell_7_horizon(mo):
    mo.md("""
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

The color wheel becomes a mirror: not just a taxonomy of philosophies,
but a practical tool for understanding how they combine in individuals.
""")
    return


# ============================================================
# Cell 8: References & Acknowledgements
# ============================================================
@app.cell
def cell_8_references(mo):
    mo.md("""
## References & Acknowledgements

This project uses the five Magic: The Gathering colors as its test case.
The philosophical framework for the color wheel is drawn from the following source,
which we gratefully acknowledge:

- **"The MTG Color Wheel (& Humanity)"** by Duncan Sabien
  - Original: [https://homosabiens.substack.com/p/the-mtg-color-wheel](https://homosabiens.substack.com/p/the-mtg-color-wheel)

The local copy is maintained in the repo for convenient reference.
All credit for the color wheel analysis belongs to the original author.

---

*Magic: The Gathering is a trademark of Wizards of the Coast LLC, a subsidiary
of Hasbro, Inc. This project is not affiliated with, endorsed by, or sponsored
by Wizards of the Coast. All game-related terminology is used for educational
and analytical purposes under fair use.*
""")
    return


if __name__ == "__main__":
    app.run()
