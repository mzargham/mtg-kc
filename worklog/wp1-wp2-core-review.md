# WP1+WP2 — Abstract OWL + SHACL Core (Combined Review)

## Status: Not Started

## Scope

Review the already-implemented core ontology and shape resources:

- `kc/resources/kc_core.ttl` — abstract OWL ontology (WP1)
- `kc/resources/kc_core_shapes.ttl` — abstract SHACL shapes (WP2)

These were authored during the design phase and have passing tests. This gate is a user validation pass to confirm they meet requirements before building the Python API on top.

## Quality Criteria (human review)

- [ ] Does `kc_core.ttl` correctly express the topological backbone you intend? (Vertex/Edge/Face, cardinality axioms)
- [ ] Are the namespace URIs (`kc:`, `kcs:`, `mtg:`, `mtgs:`) the ones you want to commit to?
- [ ] Is the design seam comment (what OWL cannot express) clear and accurate to your understanding?
- [ ] Does the closed-triangle SPARQL constraint in `kc_core_shapes.ttl` capture what you mean by "the three edges of a face form a cycle"?
- [ ] Are there topological constraints you expected to see that are missing?

## Verification (machine — Claude runs these)

```bash
pytest tests/test_core_owl.py tests/test_core_shacl.py -v
```

Expected: all tests pass (4 OWL tests, 6 SHACL tests).

Requirements covered by tests: REQ-CORE-01 through REQ-CORE-06, H2.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
