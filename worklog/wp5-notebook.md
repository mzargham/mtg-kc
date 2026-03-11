# WP5 — Marimo Notebook

## Status: In Review

## Scope

Complete rewrite of `demo/demo.py` — 9-cell narrative arc for knowledge engineers, published to GitHub Pages as an interactive WASM app.

### Cell Structure

0. **Title & Introduction** — knowledge complex concept, 2x2 map, MTG as demo domain, roadmap
1. **Schema Authoring** — SchemaBuilder DSL with enriched attributes, OWL/SHACL in accordion (H3)
2. **The Five Colors** — pentagon visualization (networkx + matplotlib), color persona cards
3. **The Ten Pairs** — edge cards grouped by disposition (adjacent/opposite) in tabs
4. **Verification** — element counts, deliberate failure with `goal="chaos"`, SHACL report (H4)
5. **Discovery** — `faces_by_edge_pattern` query, shard/wedge classification, compare with essay (H5)
6. **Promotion** — `promote_to_attribute` makes structure required, schema/data tension
7. **Horizon** — dual: query API (tooling) + Person vertex type (application)
8. **References** — essay credits + WotC trademark disclosure

### Design Decisions

- **Audience**: Knowledge engineers
- **Essay content**: Showcased heavily via marimo `callout()` cards
- **Card organization**: Progressive reveal — colors with vertices, pairs with edges, triples with faces
- **Discovery arc**: Compare and contrast — topology reproduces domain knowledge
- **Visualization**: Static matplotlib (WASM-compatible)
- **Schema dumps**: Accordion/collapsible
- **Horizon**: Dual — query API + Person vertex type

## Quality Criteria (human review)

- [ ] Does the narrative arc tell the story you want to tell?
- [ ] Is the pentagon visualization clear and does it convey the K5 structure?
- [ ] Do the persona cards do justice to the essay content?
- [ ] Does the discovery → compare-and-contrast → promotion sequence land?
- [ ] Is the horizon (query API + Person) the right teaser for future work?
- [ ] Is the tone appropriate for knowledge engineers?
- [ ] Do the OWL/SHACL accordions add value without cluttering the narrative?

## Verification (machine — Claude runs these)

```bash
# Notebook module loads without error
uv run python -c "import importlib.util; spec = importlib.util.spec_from_file_location('demo', 'demo/demo.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print('OK')"

# H6 check: no forbidden imports
grep -E "^(from|import) (rdflib|pyshacl|owlrl)" demo/demo.py
# Expected: no matches

# All tests pass (203 passed, 5 skipped)
uv run pytest tests/ -v
```

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
| 2026-03-10 | Implement WP5 notebook | Complete rewrite of demo/demo.py — 9 cells with progressive reveal, persona cards, pentagon viz, discovery with compare-and-contrast, dual horizon. H1-H6 covered. 203 tests pass, 5 skip. |
| 2026-03-10 | Delete session prompt | Removed `worklog/wp5-session-prompt.md` (wrong format, content absorbed into plan). |
| 2026-03-10 | Fix H6 test false positive | Rephrased docstring to avoid regex match on "from rdflib" in comment text. |
