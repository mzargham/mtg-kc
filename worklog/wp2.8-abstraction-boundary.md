# WP2.8 — Abstraction Boundary Definition

## Status: In Review

## Scope

Define the abstraction boundary between the core framework (kc/kcs) and model
families (mtg/mtgs). Resolve three design issues flagged during WP2.5 review.
Document vocabulary tiers and create a deferred SKOS issue.

**A. Abstraction boundary documentation:**

- Core framework: topological rule enforcement + ontological rule authoring tools
- Model families: ontological rule enforcement + concrete complex authoring
- Three vocabulary tiers (structural → type → value), each extending but never
  replacing the tier above
- Layer ownership of the 2×2 responsibility map

**B. Design issue resolutions:**

1. `add_face_type` attributes dict format: fixed from ambiguous flat dict to
   nested `{"vocab": VocabDescriptor, "required": bool}` convention
2. Unregistered type detection: documented as Python-side guard (step 0 in
   add_* methods), not a SHACL concern
3. Multiple shapes on boundary violations: documented as intentional —
   ValidationError.report includes all violations

**C. Deferred issue:**

- SKOS vocabulary formalization (`docs/issues/skos-vocabularies.md`)

## Files modified

| File | Change |
|------|--------|
| `docs/ARCHITECTURE.md` | New "Abstraction Boundary" section: layer responsibilities, type inheritance chain, 2×2 layer ownership, vocabulary tiers, Python-side guards |
| `kc/schema.py` | `add_face_type` docstring + class docstring example: attribute value format convention |
| `kc/graph.py` | `_validate()` docstring: multi-shape note; add_* TODO comments: type registration as step 0 |
| `tests/test_schema_builder.py` | `basic_schema` fixture: nested attribute dict format |
| `tests/test_knowledge_complex.py` | `schema` fixture: nested attribute dict format; boundary-closure test docstring: multi-shape note |
| `tests/test_mtg_demo.py` | Fixture: nested attribute dict format |
| `models/mtg/schema.py` | `build_mtg_schema()`: nested attribute dict format |
| `demo/demo.py` | Nested attribute dict format |
| `docs/PLAN.md` | Example code: nested attribute dict format |
| `docs/issues/skos-vocabularies.md` | New deferred issue |
| `worklog/wp2.8-abstraction-boundary.md` | This file |

## Quality Criteria (human review)

- [ ] Does the core vs. model boundary description match your mental model?
- [ ] Does the vocabulary tiers table (structural → type → value) capture the right abstraction?
- [ ] Is the nested attribute dict format (`{"vocab": ..., "required": bool}`) the right API?
- [ ] Are the three design issue resolutions satisfactory?
- [ ] Is deferring SKOS the right call for this proof-of-concept?

## Verification (machine — Claude runs these)

```bash
# Core tests still pass (15 tests: 7 OWL, 8 SHACL)
uv run pytest tests/test_core_owl.py tests/test_core_shacl.py -v

# Attribute dict format is consistent (all should show nested format)
grep -n "required.*False" models/mtg/schema.py tests/test_schema_builder.py tests/test_knowledge_complex.py tests/test_mtg_demo.py demo/demo.py
```

Expected: 15 core tests pass. All `required: False` occurrences use nested dict format.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
| 2026-03-10 | Define abstraction boundary between core (kc/kcs) and model families (mtg/mtgs); resolve three flagged design issues | Added ARCHITECTURE.md section (layer responsibilities, vocabulary tiers, Python-side guards). Fixed attributes dict format across 6 files. Updated graph.py stubs with type registration guards. Created SKOS deferred issue. |
| 2026-03-10 | Component Layers diagram missing model family layer | Updated ASCII diagram to four layers: Demo/Notebook → Model Family → kc Package → static resources → rdflib. Added prose describing the model family layer as analogous to a dataclass/ML model class. |
| 2026-03-10 | Consistency sweep: "two layers" text vs four-layer diagram; File Inventory incomplete | Clarified Abstraction Boundary intro to reference four implementation layers with the boundary between core and model. Added models/mtg/schema.py and models/mtg/queries/*.sparql to File Inventory table. |
