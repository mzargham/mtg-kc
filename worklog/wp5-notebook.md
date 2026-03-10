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

## Quality Criteria

- [ ] Full narrative arc runs end-to-end without error
- [ ] H1: All four cells of the 2x2 map demonstrated
- [ ] H2: Closed-triangle constraint visible in SHACL dump, OWL limit noted
- [ ] H3: `promote_to_attribute` shown producing changes in both OWL and SHACL
- [ ] H4: SHACL catches malformed face and shows readable report
- [ ] H5: SPARQL discovers ooa/oaa split without pre-assertion
- [ ] H6: Notebook never imports rdflib, pyshacl, or owlrl directly
- [ ] Graph visualization renders with edges colored by disposition

## Verification

```bash
marimo run demo/demo.py
```

Expected: notebook opens in browser, all cells execute, visualizations render.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
