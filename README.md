# Knowledge Complex — Semantic Web Toolchain Proof of Concept

## Hypothesis

The semantic web toolchain (OWL + SHACL + SPARQL via `rdflib`/`pyshacl`) is sufficient to implement the three-layer knowledge complex framework. A Python package abstraction can hide the internal 2×2 complexity — {topological, ontological} × {OWL, SHACL} — behind a DSL that feels like dataclass-style modeling.

## What This Is

A demonstrator, not production code. End-to-end, fully working, but scoped to validate the toolchain hypothesis. The concrete instance is a knowledge complex over the five Magic: The Gathering colors, used because it is simple enough to understand immediately but non-trivial enough to exercise all framework layers.

This repo uses the [`knowledgecomplex`](https://github.com/BlockScience/knowledgecomplex) Python package as its framework layer. The package provides `SchemaBuilder`, `KnowledgeComplex`, and the full OWL/SHACL/SPARQL machinery — this repo provides the MTG domain model and demo on top of it.

## Installation

```bash
pip install knowledgecomplex
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras
```

## Repository Layout

```text
models/
  mtg/                       # Domain model (Color, ColorPair, ColorTriple)
    schema.py                #   build_mtg_schema() — type definitions + SPARQL constraints
    queries/                 #   model-specific SPARQL templates
    __init__.py

demo/                        # Concrete instance + published notebook
  demo_instance.py           #   build_mtg_instance() — 5 colors, 10 edges, 10 faces
  demo.py                    #   marimo notebook (published to GitHub Pages)

tests/                       # pytest suite (203 passed)

docs/
  ARCHITECTURE.md            # 2×2 responsibility map and design decisions
  REQUIREMENTS.md            # REQ-* identifiers (tests trace back to these)

references/                  # reference materials (e.g. source articles)
```

The **framework layer** (OWL ontology, SHACL shapes, `SchemaBuilder`, `KnowledgeComplex`) lives in the [`knowledgecomplex`](https://pypi.org/project/knowledgecomplex/) package — installed as a dependency, not vendored in this repo.

## Dependencies

```toml
knowledgecomplex = ">=0.1.0"   # framework (transitively brings rdflib, pyshacl, owlrl)
pandas = ">=2.0"

# optional extras:
marimo = ">=0.6"               # [notebook]
networkx = ">=3.0"             # [notebook]
matplotlib = ">=3.8"           # [notebook]
```

## Usage Sketch

```python
# Layer 2: domain model defines types and queries
from models.mtg import build_mtg_schema, QUERIES_DIR

# Layer 1: generic framework
from knowledgecomplex import KnowledgeComplex

sb = build_mtg_schema()
kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])

# Layer 3: concrete data — vocab and text attributes
kc.add_vertex("White", type="Color",
    goal="peace", method="order",
    persona="Believes the solution to suffering is...",
    at_best="Protective and principled.",
    at_worst="Rigid and authoritarian.",
    example_behaviors=["Creating fair rules", "Building institutions"])

kc.add_edge("WU", type="ColorPair",
    vertices={"White", "Blue"}, disposition="adjacent",
    guild="azorius", theme="design",
    persona="The marriage of structure and knowledge.",
    at_best="Principled innovation.", at_worst="Bureaucratic control.",
    example_behaviors=["Designing governance systems"])

# add_face triggers SHACL validation on write
# SPARQL discovers shard/wedge classification from edge dispositions
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

The notebook is published to GitHub Pages via GitHub Actions. The review gate and tests run in parallel; both must pass before the build and deploy steps.

Before deployment can proceed, a human must review the HTML export locally:

```bash
# 1. Export and review in browser
uv run marimo export html demo/demo.py -o _site/index.html

# 2. Record approval (must be less than 10 min old — do this last before pushing)
echo "mzargham $(date -u +%Y-%m-%dT%H:%M:%SZ)" > _review/approval

# 3. Commit and push
git add _review/approval
git commit -m "approve deploy"
git push
```

## References & Acknowledgements

This project uses the five Magic: The Gathering colors as its test case. The philosophical framework for the color wheel is drawn from the following source, which we gratefully acknowledge:

- **"The MTG Color Wheel (& Humanity)"** by Duncan Sabien
  - Original: <https://homosabiens.substack.com/p/the-mtg-color-wheel>
  - Local copy: [`references/the-mtg-color-wheel.md`](references/the-mtg-color-wheel.md)

The local copy is maintained for convenient reference. All credit for the color wheel analysis belongs to the original author.

Magic: The Gathering is a trademark and © Wizards of the Coast, a subsidiary of Hasbro, Inc. This project is not affiliated with, endorsed by, or sponsored by Wizards of the Coast. MTG content is used here for educational and analytical purposes only.

## See Also

- `docs/ROADMAP.md` — completed work summary, open issues, and forward direction
- `docs/PLAN.md` — original project plan (historical)
- `docs/ARCHITECTURE.md` — the 2×2 responsibility map, design decisions, known OWL limits
- `docs/REQUIREMENTS.md` — numbered requirements; all tests trace back to these
