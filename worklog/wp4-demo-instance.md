# WP4 — MTG Demo Instance

## Status: Not Started

## Scope

Complete the MTG color pentagon instance in `demo/demo_instance.py`:

- 5 `Color` vertices already defined (White, Blue, Black, Red, Green)
- 10 `Relationship` edges already defined (5 adjacent, 5 opposite)
- **Remaining:** 10 `ColorTriple` faces — one per valid triangle in the complete pentagon graph
- No `pattern` attribute asserted on any face (discovery via SPARQL only)
- Un-skip tests in `tests/test_mtg_demo.py`

## Quality Criteria

- [ ] REQ-DEMO-01: Exactly 5 Color vertices
- [ ] REQ-DEMO-02: Exactly 5 adjacent edges (W-U, U-B, B-R, R-G, G-W)
- [ ] REQ-DEMO-03: Exactly 5 opposite edges (W-B, W-R, U-G, U-R, B-G)
- [ ] REQ-DEMO-04: Exactly 10 ColorTriple faces, all pass SHACL validation
- [ ] REQ-DEMO-05: No face has `pattern` asserted; ooa/oaa discoverable only via query (H5)
- [ ] REQ-DEMO-06: After `promote_to_attribute("ColorTriple", "pattern", ..., required=True)`, all 10 faces fail SHACL (H4, H3)
- [ ] H5: `faces_by_edge_pattern` query correctly classifies all 10 triangles into ooa and oaa groups

## Verification

```bash
pytest tests/test_mtg_demo.py -v
```

Expected: all tests pass, no skipped tests.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
