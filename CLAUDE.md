# CLAUDE.md — Machine Assistant Guide

This file mirrors `README.md` but is tailored for AI assistants working on this codebase.

## Project Summary

This is a **demonstrator, not production code**. It validates one hypothesis:

> The semantic web toolchain (OWL + SHACL + SPARQL via rdflib/pyshacl) is sufficient
> to implement a three-layer knowledge complex framework, hidden behind a Python DSL
> that feels like dataclass-style modeling.

The concrete instance is a knowledge complex over the five Magic: The Gathering colors. It is simple enough to understand immediately but non-trivial enough to exercise all framework layers.

## Repository Layout

```
kc/                          # Layer 1: generic KC framework
  resources/
    kc_core.ttl              #   OWL ontology (topological backbone)
    kc_core_shapes.ttl       #   SHACL shapes (topological constraints)
  queries/
    vertices.sparql          #   framework query templates
  schema.py                  #   SchemaBuilder — type/rule authoring API
  graph.py                   #   KnowledgeComplex — instance I/O + validation
  exceptions.py              #   ValidationError, SchemaError, UnknownQueryError
  __init__.py                #   public API surface

models/
  mtg/                       # Layer 2: MTG domain model
    schema.py                #   build_mtg_schema() — Color, ColorPair, ColorTriple
    queries/                 #   model-specific SPARQL templates
    __init__.py

demo/                        # Layer 3: concrete instance + published notebook
  demo_instance.py           #   build_mtg_instance() — 5 colors, 10 edges, 10 faces
  demo.py                    #   marimo notebook (published to GitHub Pages)

tests/                       # pytest suite (208 passed)
  qc_io.py                   #   marimo QC notebook for import/export verification

docs/
  PLAN.md                    # work packages and review gates
  ARCHITECTURE.md            # 2×2 responsibility map, design decisions DD1-DD5
  REQUIREMENTS.md            # REQ-* identifiers (tests trace back to these)
  issues/                    # deferred issues (not blocking current scope)
```

## Abstraction Boundary (H6)

**Critical invariant:** Code in `demo/` and `models/` never imports `rdflib`, `pyshacl`, or `owlrl`. These are internal implementation details of the `kc/` package. The public API surface is:

```python
from kc.schema import SchemaBuilder, vocab, text, TextDescriptor, VocabDescriptor
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError, SchemaError, UnknownQueryError
```

If you write code that touches `demo/` or `models/`, do not introduce direct RDF library imports.

## Key Conventions

### Terminology

- **structure** (not "pattern") — the classification of color triples
- **shard / wedge** (not "ooa" / "oaa") — uses MTG domain vocabulary
- **vocab()** — controlled vocabulary attributes (generates sh:in constraints)
- **text()** — free-text string attributes (no sh:in, just xsd:string)

### Work Package Discipline

- One WP at a time. Do not begin the next WP until the current one has Status: Accepted.
- Update the relevant `worklog/wp*.md` changelog after every change.
- Reference `REQ-*` identifiers (from `docs/REQUIREMENTS.md`) and `H1-H6` hypothesis criteria (from `docs/PLAN.md`) in quality criteria and changelog entries.
- Keep entries factual and concise.

### Test Traceability

Tests reference requirement identifiers in docstrings (e.g., `REQ-DEMO-01`, `REQ-VV-05`). When adding tests, include the relevant REQ-* or H* identifier.

## Running Tests

```bash
uv run pytest tests/ -v
```

Expected: 208 passed, 0 skipped.

## Running the Notebook

```bash
uv run marimo edit demo/demo.py      # interactive editing
uv run marimo run demo/demo.py       # read-only viewing
```

## Deployment Review Process

The notebook is published to GitHub Pages via GitHub Actions (`.github/workflows/deploy.yml`). The pipeline is: **review-gate + test → build → deploy** (review-gate and test run in parallel; both must pass before build).

**Human review gates deployment.** The `_review/approval` file must contain the approver's username and an ISO timestamp less than 10 minutes old. Approval is the last step before pushing.

### The review/signoff workflow

1. **Export locally:**
   ```bash
   uv run marimo export html demo/demo.py -o _site/index.html
   ```

2. **Review in browser:** Open `_site/index.html` and verify rendering.

3. **Record approval:**
   ```bash
   echo "mzargham $(date -u +%Y-%m-%dT%H:%M:%SZ)" > _review/approval
   ```

4. **Commit and push:**
   ```bash
   git add _review/approval
   git commit -m "approve deploy"
   git push
   ```

### When the review gate blocks

If CI fails with "Approval is X minutes old", re-approve by updating the timestamp and pushing.

## What Not To Do

- Do not commit `.env`, credentials, or secrets
- Do not push to main without tests passing
- Do not bypass the review gate — if the export looks wrong, fix it
- Do not add `rdflib`/`pyshacl`/`owlrl` imports to demo or model code
- Do not use `git push --force` to main
- Do not create new work packages without the current one being accepted

## Architecture Quick Reference

The framework uses a 2×2 responsibility map:

|                | OWL (schema)           | SHACL (constraints)        |
|----------------|------------------------|----------------------------|
| **Topological** | Vertex/Edge/Face classes, cardinality | Closed-triangle rule (SPARQL) |
| **Ontological** | User subclasses, vocab properties | sh:in value constraints |

- `kc_core.ttl` + `kc_core_shapes.ttl` = topological layer (framework)
- `SchemaBuilder` generates the ontological layer (model-specific)
- `KnowledgeComplex` manages instance data + validation

See `docs/ARCHITECTURE.md` for the full design document.

## See Also

- `README.md` — human-facing project introduction
- `docs/ARCHITECTURE.md` — design decisions, OWL limits, namespace conventions
- `docs/REQUIREMENTS.md` — requirement identifiers
- `docs/PLAN.md` — work package sequence and review gates
- `worklog/CLAUDE.md` — worklog conventions and status values
