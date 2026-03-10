# WP2.5 — Stub Alignment with WP1/WP2 Mathematical Foundations

## Status: Accepted (conditional)

## Scope

Refactor downstream stubs and documentation to reflect the WP1/WP2 changes:
Element base class, Complex container, and boundedBy domain/range.

Two categories of change:

**A. Conceptual alignment — KnowledgeComplex maps to kc:Complex:**

- `KnowledgeComplex._init_graph()` creates a `kc:Complex` individual
- `add_vertex()` / `add_edge()` / `add_face()` each assert `kc:hasElement`
- `_validate()` enforces both element shapes and ComplexShape boundary-closure
- Boundary-closure enforced via the "slice rule": every prefix of the insertion sequence is a valid complex (partial ordering — types can be interleaved)

**B. Stale reference cleanup:**

- WP3 worklog had old parameter names (`source, target` → `vertices`; `edges` → `boundary`)
- Docstrings updated to reference Element base class throughout

## Files modified

| File | Change |
|------|--------|
| `kc/graph.py` | Module docstring, class docstring, `_complex_iri` field, all method docstrings updated to reference kc:Complex and kc:hasElement; TODO comments describe WP3 implementation steps |
| `kc/schema.py` | Module docstring and class/method docstrings reference Element base class |
| `tests/test_knowledge_complex.py` | Added `test_add_edge_before_vertices_fails` (ComplexShape boundary-closure) |
| `worklog/wp3-python-api.md` | Fixed stale parameter names; added kc:Complex mapping note |
| `docs/ARCHITECTURE.md` | Added KnowledgeComplex ↔ kc:Complex mapping paragraph |
| `worklog/wp2.5-stub-alignment.md` | This file |

## Quality Criteria (human review)

- [ ] Does the KnowledgeComplex ↔ kc:Complex mapping make sense?
- [ ] Does the slice rule (partial ordering, not strict type ordering) make sense?
- [ ] Are the updated docstrings and TODOs clear enough to guide WP3 implementation?

## Verification (machine — Claude runs these)

```bash
# Core tests still pass (stubs unchanged)
uv run pytest tests/test_core_owl.py tests/test_core_shacl.py -v
```

Expected: 15 tests pass (7 OWL, 8 SHACL). WP3 tests still raise NotImplementedError (expected).

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
| 2026-03-10 | Align downstream stubs with WP1/WP2 Element/Complex foundations | Updated kc/graph.py (KnowledgeComplex ↔ kc:Complex mapping, hasElement assertions, boundary-closure validation), kc/schema.py (Element references in docstrings), tests/test_knowledge_complex.py (boundary-closure ordering test), worklog/wp3-python-api.md (stale param names), docs/ARCHITECTURE.md (Complex mapping paragraph). |
| 2026-03-10 | Slice rule instead of type ordering; temporal ordering as deferred issue | Replaced strict simplex-order language with slice rule (partial ordering). Created docs/issues/temporal-ordering.md. Updated kc/graph.py docstrings and docs/ARCHITECTURE.md. |
