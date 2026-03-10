# WP5 — Marimo Notebook

## Status: Not Started

## Scope

Implement cells 2-6 in `demo/demo.py` to complete the narrative arc:

1. Schema authoring (Cell 1) — already implemented
2. **Instance loading** — load MTG instance, visualize graph with disposition coloring
3. **Verification** — SHACL pass on all faces, then deliberate failure with report
4. **Discovery** — `faces_by_edge_pattern` query reveals ooa/oaa without pre-assertion
5. **Promotion** — `promote_to_attribute` call, updated SHACL dump, re-validation failures
6. **Horizon** — Person vertex type stub motivating next work
7. References & Acknowledgements (Cell 7) — already implemented

## Quality Criteria (human review)

- [ ] Does the narrative arc tell the story you want to tell?
- [ ] Is the visualization clear and does it convey the pentagon structure intuitively?
- [ ] Does the discovery → promotion sequence land as a compelling demonstration?
- [ ] Is the "horizon" cell (Person vertex type) the right teaser for future work?
- [ ] Is the tone and exposition appropriate for the intended audience?
- [ ] Do the OWL/SHACL dumps shown in the notebook aid understanding or just add noise?

## Verification (machine — Claude runs these)

```bash
# Notebook executes without error
marimo run demo/demo.py

# H6 check: no forbidden imports
grep -E "^(from|import) (rdflib|pyshacl|owlrl)" demo/demo.py
```

Expected: notebook opens in browser, all cells execute, visualizations render. Grep returns no matches.

Requirements covered by tests/checks: H1 through H6.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
