# WP4 — MTG Demo Instance

## Status: Not Started

## Scope

Complete the MTG color pentagon instance in `demo/demo_instance.py`:

- 5 `Color` vertices already defined (White, Blue, Black, Red, Green)
- 10 `Relationship` edges already defined (5 adjacent, 5 opposite)
- **Remaining:** 10 `ColorTriple` faces — one per valid triangle in the complete pentagon graph
- No `pattern` attribute asserted on any face (discovery via SPARQL only)
- Un-skip tests in `tests/test_mtg_demo.py`

## Quality Criteria (human review)

- [ ] Are the 10 triangles the correct ones for the complete graph on the MTG color pentagon?
- [ ] Do the edge dispositions (adjacent/opposite) match the canonical MTG color wheel relationships?
- [ ] Does the ooa/oaa classification revealed by SPARQL match your expectations from the reference article?
- [ ] Is the pentagon oriented correctly per MTG convention (W-U-B-R-G)?
- [ ] Are the face names/IDs intuitive and consistent with the vertex/edge naming?

## Verification (machine — Claude runs these)

```bash
pytest tests/test_mtg_demo.py -v
```

Expected: all tests pass, no skipped tests.

Requirements covered by tests: REQ-DEMO-01 through REQ-DEMO-06, H4, H5.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
