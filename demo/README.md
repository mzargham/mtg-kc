# Demo: MTG Color Wheel Knowledge Complex

This directory contains the concrete MTG demonstrator — Layer 3 of the project stack.

## Contents

```
demo/
  demo.py              Marimo notebook (the published artifact)
  demo_instance.py     build_mtg_instance() — 5 colors, 10 edges, 10 faces
  src/                  Pre-exported model (load without running Python)
    ontology.ttl        OWL ontology (core + MTG types)
    shapes.ttl          SHACL shapes (core + MTG constraints)
    instance.ttl        All vertices, edges, faces with attributes
    queries/            SPARQL templates
```

## Quick Start

### Option 1: Run the notebook

```bash
uv run marimo run demo/demo.py       # read-only
uv run marimo edit demo/demo.py      # interactive
```

### Option 2: Build from Python

```python
from demo.demo_instance import build_mtg_instance

kc = build_mtg_instance()
df = kc.query("faces_by_edge_pattern")
print(df)
```

### Option 3: Load from exported files

Skip Python model construction entirely — load the pre-built Turtle files:

```python
from knowledgecomplex import KnowledgeComplex

kc = KnowledgeComplex.load("demo/src")
df = kc.query("faces_by_edge_pattern")
print(df)
```

This is useful for exploring the RDF directly, or for testing `load()` without running `build_mtg_instance()`.

### Option 4: Inspect the RDF directly

The `.ttl` files in `src/` are standard Turtle. Open them in any RDF tool (Protégé, RDFLib, a triple store) or read them as text:

```bash
cat demo/src/ontology.ttl    # OWL class hierarchy
cat demo/src/shapes.ttl      # SHACL constraints
cat demo/src/instance.ttl    # 5 vertices, 10 edges, 10 faces
```

## What's in the Model

| Element | Count | Type | Key Attributes |
|---------|-------|------|----------------|
| Vertices | 5 | `Color` | persona, at_best, at_worst, goal, method, example_behaviors |
| Edges | 10 | `ColorPair` | disposition (adjacent/opposite), guild, theme |
| Faces | 10 | `ColorTriple` | structure (discoverable via query, not pre-asserted) |

The `shard`/`wedge` classification of faces is the central demonstration: it is *discovered* via SPARQL query, not stored in the data. Running `promote_to_attribute("ColorTriple", "structure", ...)` upgrades it to a required attribute, causing all 10 faces to fail validation — motivating the annotation step.

## Regenerating `src/`

If you modify the schema or instance data:

```python
from demo.demo_instance import build_mtg_instance

kc = build_mtg_instance()
kc.export("demo/src")
```

Then commit the updated files.
