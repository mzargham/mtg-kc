# Knowledge Complex — Semantic Web Toolchain Proof of Concept

## Hypothesis

The semantic web toolchain (OWL + SHACL + SPARQL via `rdflib`/`pyshacl`) is sufficient to implement the three-layer knowledge complex framework. A Python package abstraction can hide the internal 2×2 complexity — {topological, ontological} × {OWL, SHACL} — behind a DSL that feels like dataclass-style modeling.

## What This Is

A demonstrator, not production code. End-to-end, fully working, but scoped to validate the toolchain hypothesis. The concrete instance is a knowledge complex over the five Magic: The Gathering colors, used because it is simple enough to understand immediately but non-trivial enough to exercise all framework layers.

## Repository Layout

Three layers, designed for future separation:

```
kc/                          # Layer 1: generic KC framework (like numpy)
  resources/
    kc_core.ttl              #   abstract OWL ontology (topological backbone)
    kc_core_shapes.ttl       #   abstract SHACL shapes (topological constraints)
  queries/
    vertices.sparql          #   generic query templates
  schema.py                  #   SchemaBuilder — type and rule authoring API
  graph.py                   #   KnowledgeComplex — instance I/O API
  exceptions.py              #   ValidationError and friends
  __init__.py

models/
  mtg/                       # Layer 2: MTG domain model (like scipy)
    schema.py                #   MTG schema definition (Color, ColorPair, ColorTriple)
    queries/
      edges_by_disposition.sparql
      faces_by_edge_pattern.sparql
    __init__.py

demo/                        # Layer 3: concrete instance + notebook
  demo_instance.py           #   MTG color pentagon (5 colors, 10 edges, 10 faces)
  demo.py                    #   marimo notebook

tests/
  test_core_owl.py
  test_core_shacl.py
  test_schema_builder.py
  test_knowledge_complex.py
  test_mtg_demo.py

docs/
  PLAN.md                    # project plan with work packages and gates
  ARCHITECTURE.md            # 2x2 responsibility map and design decisions
  REQUIREMENTS.md            # full requirements document

references/                  # reference materials (e.g. source articles)

pyproject.toml
```

## Dependencies

```toml
rdflib = ">=7.0"
pyshacl = ">=0.25"
owlrl = ">=6.0"
marimo = ">=0.6"
networkx = ">=3.0"
matplotlib = ">=3.8"
pandas = ">=2.0"
```

## Usage Sketch

```python
# Layer 2: domain model defines types and queries
from models.mtg import build_mtg_schema, QUERIES_DIR

# Layer 1: generic framework
from kc.graph import KnowledgeComplex

sb = build_mtg_schema()
kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])

# Layer 3: concrete data
kc.add_vertex("White", type="Color")
kc.add_vertex("Blue",  type="Color")
kc.add_edge("WU", type="ColorPair", vertices={"White", "Blue"}, disposition="adjacent")
# ... add remaining vertices, edges, faces
# add_face triggers SHACL validation on write

results = kc.query("faces_by_edge_pattern")
```

## Running Tests

```bash
pytest tests/ -v
```

## Notebook

```bash
marimo run demo/demo.py
```

## Deployment

The notebook is published to GitHub Pages via GitHub Actions. The pipeline runs
tests first, then checks for human review approval before building and deploying.

Before deployment can proceed, a human must review the HTML export locally:

```bash
# 1. Export the notebook
uv run marimo export html-wasm demo/demo.py -o _site/index.html --mode run

# 2. Open _site/index.html in your browser and verify the rendering

# 3. Record approval
git rev-parse HEAD > _review/approved.sha

# 4. Commit and push
git add _review/approved.sha
git commit -m "approve HTML export for $(git rev-parse --short HEAD)"
git push
```

CI verifies that the SHA in `_review/approved.sha` matches the current `HEAD`.
If new commits are pushed after the review, the build fails and asks for re-review.

## References & Acknowledgements

This project uses the five Magic: The Gathering colors as its test case. The philosophical framework for the color wheel is drawn from the following source, which we gratefully acknowledge:

- **"The MTG Color Wheel (& Humanity)"** by Homo Sabiens
  - Original: <https://homosabiens.substack.com/p/the-mtg-color-wheel>
  - Local copy: [`references/the-mtg-color-wheel.md`](references/the-mtg-color-wheel.md)

The local copy is maintained for convenient reference. All credit for the color wheel analysis belongs to the original author.

## See Also

- `docs/PLAN.md` — work packages, sequence, review gates
- `docs/ARCHITECTURE.md` — the 2×2 responsibility map, design decisions, known OWL limits
- `docs/REQUIREMENTS.md` — numbered requirements; all tests trace back to these
