"""
demo/demo.py — Marimo notebook: Knowledge Complex over MTG Color Pentagon

Run: marimo run demo/demo.py

Narrative arc:
  1. Schema authoring       — build SchemaBuilder; inspect OWL + SHACL dumps
  2. Instance loading       — load MTG instance; visualize graph
  3. Verification           — SHACL validation pass and deliberate failure
  4. Discovery              — SPARQL reveals ooa/oaa without pre-assertion
  5. Promotion              — promote_to_attribute; re-validation fails; motivates annotation
  6. Horizon                — Person vertex type stub motivates next work

WP5 — implementation pending after WP4.
"""

import marimo as mo

# Note: this notebook imports from kc only — never from rdflib, pyshacl, or owlrl.
# REQ-VV-06 / hypothesis H6.

from kc.schema import SchemaBuilder, vocab
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ============================================================
# Cell 1: Schema Authoring
# ============================================================

_schema_cell = mo.md("""
## 1. Schema Authoring

We define three types using the `SchemaBuilder` DSL.
No RDF, OWL, or SHACL is written directly.
The internal representation is hidden; we can inspect it via `dump_owl()` / `dump_shacl()`.
""")

sb = SchemaBuilder(namespace="mtg")
sb.add_vertex_type("Color")
sb.add_edge_type("Relationship",
                 attributes={"disposition": vocab("adjacent", "opposite")})
sb.add_face_type("ColorTriple",
                 attributes={"pattern": vocab("ooa", "oaa"), "required": False})

_owl_dump   = mo.ui.code(sb.dump_owl(),   language="turtle", label="OWL (internal)")
_shacl_dump = mo.ui.code(sb.dump_shacl(), language="turtle", label="SHACL (internal)")

# ============================================================
# Cell 2: Instance Loading
# ============================================================

_instance_cell = mo.md("""
## 2. Instance Loading

Load the MTG color pentagon. 5 vertices, 10 edges (5 adjacent + 5 opposite).
Edges are colored by `disposition`.
""")

# TODO (WP5): import from demo_instance after WP4 is complete
# from demo.demo_instance import build_mtg_schema, build_mtg_instance
# kc = build_mtg_instance(sb)

# Visualization placeholder
def _draw_mtg_graph(kc: KnowledgeComplex):
    # TODO (WP5): query vertices + edges; build networkx graph; draw with disposition coloring
    pass

# ============================================================
# Cell 3: Verification
# ============================================================

_verification_cell = mo.md("""
## 3. Verification (SHACL)

All 10 faces should pass structural validation.
We then deliberately construct a broken face (open triangle) and show the SHACL report.
""")

# TODO (WP5): demonstrate valid face, then ValidationError with report

# ============================================================
# Cell 4: Discovery
# ============================================================

_discovery_cell = mo.md("""
## 4. Discovery via SPARQL

The `faces_by_edge_pattern` query returns the three edge dispositions for each face.
We classify faces as `ooa` (two opposite, one adjacent) or `oaa` (one opposite, two adjacent)
*without any pre-asserted pattern attribute*.

This is the emergent structure of the simplicial complex — visible in the data,
not yet captured in the schema.
""")

# TODO (WP5): df = kc.query("faces_by_edge_pattern"); classify; display table

# ============================================================
# Cell 5: Promotion
# ============================================================

_promotion_cell = mo.md("""
## 5. Promoting a Discovered Pattern to the Schema

`promote_to_attribute` updates both OWL and SHACL in a single call.
After promotion, re-validating the existing instance will fail on every face —
because the data does not yet carry the `pattern` attribute.

This demonstrates:
- The single-call invariant (H3)
- Verification catching a schema/data mismatch (H4)
- Why the Python package earns its abstraction: two internal changes, one API call
""")

# TODO (WP5):
# sb.promote_to_attribute("ColorTriple", "pattern", vocab("ooa","oaa"), required=True)
# show updated dump_shacl()
# attempt re-validate; show failures

# ============================================================
# Cell 6: Horizon
# ============================================================

_horizon_cell = mo.md("""
## 6. Horizon: Adding a Person Vertex Type

```python
sb.add_vertex_type("Person")
sb.add_edge_type("PersonColorAffinity",
                 attributes={"strength": vocab("primary", "secondary")})
# ... immediately motivates new face types involving Person-Color-Color triangles
```

Adding a new vertex type creates demand for:
- New edge types (Person ↔ Color affinities)
- New face types (Person-Color-Color triangles, each with their own attribute schema)

This is the natural growth path of a knowledge complex.
The framework supports it: each new `add_*_type` call updates OWL + SHACL atomically.
""")

# ============================================================
# Cell 7: References & Acknowledgements
# ============================================================

_references_cell = mo.md("""
## References & Acknowledgements

This project uses the five Magic: The Gathering colors as its test case.
The philosophical framework for the color wheel is drawn from the following source,
which we gratefully acknowledge:

- **"The MTG Color Wheel (& Humanity)"** by Homo Sabiens
  - Original: [https://homosabiens.substack.com/p/the-mtg-color-wheel](https://homosabiens.substack.com/p/the-mtg-color-wheel)
  - Local copy: [`references/the-mtg-color-wheel.md`](../references/the-mtg-color-wheel.md)

The local copy is maintained for convenient reference.
All credit for the color wheel analysis belongs to the original author.
""")
