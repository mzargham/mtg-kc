# WP4 — MTG Demo Instance

## Status: In Review

## Scope

Complete the MTG color pentagon instance in `demo/demo_instance.py`:

- 5 `Color` vertices (White, Blue, Black, Red, Green)
- 10 `ColorPair` edges (5 adjacent, 5 opposite)
- 10 `ColorTriple` faces — one per valid triangle in the complete pentagon graph
- No `structure` attribute asserted on any face (discovery via SPARQL only)
- Un-skip face-related tests in `tests/test_mtg_demo.py`

## Quality Criteria (human review)

- [ ] Are the 10 triangles the correct ones for the complete graph on the MTG color pentagon?
- [ ] Do the edge dispositions (adjacent/opposite) match the canonical MTG color wheel relationships?
- [ ] Does the shard/wedge classification revealed by SPARQL match your expectations from the reference article?
- [ ] Is the pentagon oriented correctly per MTG convention (W-U-B-R-G)?
- [ ] Are the face names/IDs intuitive and consistent with the vertex/edge naming?

## Verification (machine — Claude runs these)

```bash
pytest tests/test_mtg_demo.py -v
```

Expected: 6 passed, 1 skipped (promote test deferred to WP5).

Requirements covered by tests: REQ-DEMO-01 through REQ-DEMO-05, H5.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
| 2026-03-10 | Add all 10 ColorTriple faces to demo instance | Added 10 faces with correct boundary edges. Unskipped face-related tests. All pass. |
| 2026-03-10 | Document simplex fill policy as deferred issue | Added deferred issue in `models/mtg/schema.py` docstring: simplex inference from closed boundaries is a future framework extension, not a core invariant. MTG explicitly enumerates all faces. |
| 2026-03-10 | Superseded by WP4.5 | Demo instance enriched with essay-derived attributes in WP4.5. `pattern` replaced by `structure`. See `worklog/wp4.5-essay-attributes.md`. |
