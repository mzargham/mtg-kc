# WP5 Session Start Prompt

Copy everything below the line into the new session.

---

## Context

This is the mtg-kc project — a knowledge complex framework demonstrated via the Magic: The Gathering color wheel. Read the following files to get oriented:

1. `docs/PLAN.md` — overall project plan, hypothesis criteria H1-H6, WP definitions
2. `worklog/CLAUDE.md` — worklog conventions
3. `worklog/wp4.5-essay-attributes.md` — the most recent completed work package (enriching the MTG schema with essay-derived attributes). **Important: the code changes described in this worklog were NOT persisted to disk. They need to be re-implemented before WP5 can begin.** The full implementation spec is in my memory at `wp4.5-implementation.md`, and the approved plan is at `.claude/plans/rippling-swimming-haven.md`.
4. `worklog/wp5-notebook.md` — current WP5 scope (needs revision — see below)
5. `worklog/wp6-ci-deploy.md` — deployment plan (notebook will be published to GitHub Pages)
6. `demo/demo.py` — current notebook stub (cells 2-6 are TODOs, cell 1 uses old schema)

## Two tasks for this session

### Task 1: Re-implement WP4.5 (code was lost)

The WP4.5 worklog and plan describe all changes in detail. Re-implement them:
- `text()` framework extension in `kc/schema.py` (with shared-domain handling)
- List value support in `kc/graph.py`
- Enriched schema in `models/mtg/schema.py` (structure replaces pattern, new vocab and text attrs)
- Enriched demo instance in `demo/demo_instance.py` (all 25 elements with essay-derived values)
- New tests in `tests/test_text_descriptor.py` (including 4 regression tests)
- Updated tests in `test_mtg_demo.py`, `test_hypothesis_criteria.py`, `test_abstraction_boundary.py`

Verify: `pytest tests/ -v` should give 177 passed, 5 skipped.

### Task 2: Plan WP5 together (enter plan mode)

The WP5 notebook needs a revised plan that accounts for:

1. **WP4.5 enrichment**: The notebook stub references `pattern`/`ooa`/`oaa` — these are now `structure`/`shard`/`wedge`. The schema is much richer (persona, at_best, at_worst, example_behaviors, guild, theme, clan, goal, method). The narrative should showcase these.

2. **GitHub Pages deployment**: The notebook will be published as an interactive WASM app via `marimo export html-wasm`. This means:
   - Visualizations need to work in the browser (matplotlib renders as static images in WASM; consider alternatives)
   - The narrative should be self-contained and compelling for a reader who arrives at the GitHub Pages URL
   - Cell outputs should be informative even without interactivity

3. **Narrative arc revision**: The current 7-cell structure in `demo/demo.py` needs updating. Key questions to discuss:
   - How should we present the enriched attributes (persona cards? comparison tables?)
   - The discovery story is now: SPARQL reveals shard/wedge structure from edge dispositions
   - Should we show the essay-derived content alongside the topological structure?
   - What visualization best conveys the pentagon (networkx? a custom layout?)
   - The "Horizon" cell (Person vertex type) — is this still the right teaser, or should it reference model composition (`docs/issues/model-composition.md`)?

4. **H6 constraint**: The notebook must never import rdflib, pyshacl, or owlrl directly.

Let's plan the notebook together before implementing it. Enter plan mode and we'll iterate on the cell structure and narrative.
