# WP1+WP2 — Abstract OWL + SHACL Core (Combined Review)

## Status: Not Started

## Scope

Review the already-implemented core ontology and shape resources:

- `kc/resources/kc_core.ttl` — abstract OWL ontology (WP1)
- `kc/resources/kc_core_shapes.ttl` — abstract SHACL shapes (WP2)

These were authored during the design phase and have passing tests. This gate is a user validation pass to confirm they meet requirements before building the Python API on top.

## Quality Criteria

- [ ] REQ-CORE-01: OWL ontology defines `KC:Vertex`, `KC:Edge`, `KC:Face`
- [ ] REQ-CORE-02: `KC:Edge` has exactly-1 `hasSource` and exactly-1 `hasTarget` via OWL cardinality
- [ ] REQ-CORE-03: `KC:Face` has exactly-3 `hasEdge` via OWL cardinality
- [ ] REQ-CORE-04: SHACL enforces `hasSource != hasTarget` (distinctness)
- [ ] REQ-CORE-05: SHACL enforces closed-triangle constraint via `sh:sparql`
- [ ] REQ-CORE-06: Both files loadable as static resources without runtime generation
- [ ] H2: Closed-triangle is in SHACL only; OWL expressivity limit documented as design seam comment

## Verification

```bash
pytest tests/test_core_owl.py tests/test_core_shacl.py -v
```

Expected: all tests pass (4 OWL tests, 6 SHACL tests).

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
