# WP4.5 — Enrich MTG Schema with Essay-Derived Attributes

## Status: In Review

## Scope

Extract semantically meaningful attributes from the essay `references/the-mtg-color-wheel.md` and use them to enrich the MTG model family schema. Demonstrates the layering: concrete content (essay) → abstract attributes (schema) → model family (models/mtg) → framework (kc).

Three categories of change:

**A. Framework extension — `text()` descriptor (`kc/schema.py`):**

- `TextDescriptor` dataclass: `required: bool`, `multiple: bool`
- `text()` factory function (parallel to `vocab()`)
- OWL: `owl:DatatypeProperty` with `xsd:string` range, no `rdfs:comment`
- SHACL: `sh:property` with `sh:datatype xsd:string`, configurable `sh:minCount`/`sh:maxCount`, **no `sh:in`**
- `_set_owl_domain()`: when a property name appears on multiple types, `rdfs:domain` is omitted to prevent RDFS inference from classifying instances as members of all domain types (SHACL shapes handle per-type enforcement)
- `_dispatch_attr()`: unified routing for vocab, text, and dict-style attribute specs
- `add_vertex_type()` now accepts `attributes=` (was previously bare)
- `promote_to_attribute()` accepts `text=` kwarg alongside `vocab=`
- `KnowledgeComplex._assert_element()` handles list values for `text(multiple=True)`

**B. MTG schema enrichment (`models/mtg/schema.py`):**

Replace `pattern ∈ {ooa, oaa}` with `structure ∈ {shard, wedge}` — uses the MTG domain's own terminology instead of an invented encoding.

New attributes by element type:

| Type | Vocab attributes | Text attributes |
|------|-----------------|-----------------|
| Color | `goal`, `method` | `persona`, `at_best`, `at_worst`, `example_behaviors` (multiple) |
| ColorPair | `disposition`, `guild`, `theme` | `persona`, `at_best`, `at_worst`, `example_behaviors` (multiple) |
| ColorTriple | `clan`, `structure` (optional) | `persona`, `at_best`, `at_worst`, `example_behaviors` (multiple) |

All types also have optional `playstyle` and `example_decks` (multiple, not asserted in demo).

**C. Demo instance enrichment (`demo/demo_instance.py`):**

All 25 elements (5 vertices, 10 edges, 10 faces) now carry full attribute values derived from the essay: persona descriptions, at_best/at_worst characterizations, behavioral examples, guild names, clan names, thematic labels, goals, and methods.

## Files modified

| File | Change |
|------|--------|
| `kc/schema.py` | Added `TextDescriptor`, `text()`, `_set_owl_domain()`, `_dispatch_attr()`, `_add_text_attr_to_graphs()`. Updated `add_vertex_type()` to accept attributes. Updated `promote_to_attribute()` for text support. Added `_attr_domains` tracking dict. |
| `kc/graph.py` | `_assert_element()` handles list/tuple attribute values (multiple triples) |
| `kc/__init__.py` | Export `text`, `TextDescriptor` |
| `models/mtg/schema.py` | Replaced `pattern` with `structure`; added all new vocab and text attributes |
| `demo/demo_instance.py` | All 25 elements carry full essay-derived attribute values |
| `tests/test_text_descriptor.py` | **New file.** 29 tests covering text() factory, OWL/SHACL generation, shared-domain handling, cross-type validation safety, list value assertion, dict-style specs, promote with text, and 4 regression tests |
| `tests/test_mtg_demo.py` | `pattern`→`structure`, `ooa/oaa`→`shard/wedge`, verified 5+5 counts |
| `tests/test_hypothesis_criteria.py` | H6 test provides required Color attributes |
| `tests/test_abstraction_boundary.py` | `__all__` expected set includes `text`, `TextDescriptor` |

## Design decisions

1. **`text()` vs extending `vocab()`**: Separate descriptor type because the semantics differ fundamentally — `vocab()` constrains values via `sh:in`, `text()` does not. Mixing them in one type would require sentinel values or mode flags.

2. **Shared property domain removal**: When `persona` appears on Color, ColorPair, and ColorTriple, setting `rdfs:domain` on all three causes RDFS inference to classify any individual with `persona` as a member of all three classes. The fix: track which properties have been seen via `_attr_domains` dict; if a property appears on a second type, remove `rdfs:domain` entirely. SHACL shapes already enforce per-type constraints. This is a concrete instance of the 2×2 design seam: OWL's `rdfs:domain` is an inference axiom (open-world — it *adds* knowledge), while SHACL's `sh:targetClass` + `sh:property` is a constraint (closed-world — it *validates*). Shared properties need the constraint semantics, not the inference semantics, confirming why both layers are necessary in the ontological column.

3. **`structure` replaces `pattern`**: The essay calls three-consecutive-color triples "shards" and two-adjacent-plus-one-opposite triples "wedges". Using the domain's own terminology (shard/wedge) instead of the topological encoding (oaa/ooa) is faithful to the source material. The mapping: shard = oaa (1 opposite, 2 adjacent), wedge = ooa (2 opposite, 1 adjacent).

4. **`add_vertex_type()` now accepts attributes**: Previously vertex types were bare (no attributes). The enriched MTG schema requires `goal`, `method`, `persona`, etc. on Color vertices. This is a backward-compatible change — `attributes=` defaults to `None`.

## Quality Criteria (human review)

- [ ] Are the persona descriptions faithful to the essay's characterizations?
- [ ] Are the at_best/at_worst pairs balanced and accurate?
- [ ] Is the shard/wedge terminology correct (shard = 3 consecutive colors, wedge = 2 adjacent + 1 opposite)?
- [ ] Are the guild names, clan names, themes, goals, and methods all correct per MTG lore?
- [ ] Does the `text()` API design feel right alongside `vocab()`?
- [x] Is the shared-domain removal the right trade-off (loses OWL domain info, gains SHACL correctness)? — **Accepted.** Validates the 2×2 architecture: OWL domain is inference (open-world), SHACL target is constraint (closed-world). Shared properties need constraint semantics.
- [ ] Are the example_behaviors representative and concise?

## Verification (machine — Claude runs these)

```bash
pytest tests/ -v
```

Expected: 177 passed, 5 skipped, 0 failed.

Test coverage:

- `tests/test_text_descriptor.py`: 29 tests — text() descriptor, OWL/SHACL generation, shared-domain handling, cross-type validation, list values, regressions
- `tests/test_mtg_demo.py`: structure discovery (shard/wedge), 5+5 counts, no structure pre-asserted
- `tests/test_hypothesis_criteria.py`: H1–H6 with enriched schema
- All existing tests remain green

Requirements covered: REQ-DEMO-01 through REQ-DEMO-05, H1–H6.

## Bugs found and fixed (with regression tests)

| Bug | Root cause | Fix | Regression test |
|-----|-----------|-----|-----------------|
| Shared property `persona` caused SHACL cross-type violations | Multiple `rdfs:domain` values on same property → RDFS inference classifies vertex as face | `_set_owl_domain()` removes domain when property appears on multiple types | `test_regression_shared_property_cross_type_shacl_three_types` |
| Domain re-added on 3rd type after removal on 2nd | `_set_owl_domain` v1 checked `already_declared` via graph triple (always True after add), not via tracking dict | `_attr_domains` dict tracks first domain; None means shared | `test_regression_shared_domain_not_reasserted_after_removal` |
| Same bug with vocab properties | Same root cause — `_set_owl_domain` is shared by both attr handlers | Same fix | `test_regression_shared_vocab_domain_not_reasserted` |
| Full MTG instance failed validation | Compound of above: White had `persona` → inferred as ColorTriple → missing `clan`, `boundedBy` | Same fix | `test_regression_mtg_full_instance_validates` |

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
| 2026-03-10 | Add `text()` framework extension for free-text string attributes | Added `TextDescriptor`, `text()`, `_add_text_attr_to_graphs()`, `_dispatch_attr()`. Updated `add_vertex_type()` to accept attributes. Updated `promote_to_attribute()` for text support. Exported from `kc/__init__.py`. |
| 2026-03-10 | Replace `pattern ∈ {ooa, oaa}` with `structure ∈ {shard, wedge}` | Updated `models/mtg/schema.py`, `demo/demo_instance.py`, `tests/test_mtg_demo.py`. Uses MTG domain terminology. |
| 2026-03-10 | Add vocab attributes: goal, method, guild, theme, clan | Added to `models/mtg/schema.py` with controlled vocabularies from the essay. |
| 2026-03-10 | Add text attributes: persona, at_best, at_worst, example_behaviors | Added to all three element types in schema and demo instance. All 25 elements carry essay-derived values. |
| 2026-03-10 | Add optional playstyle, example_decks | Added as `text(required=False)` / `text(multiple=True, required=False)` on all types. Not asserted in demo. |
| 2026-03-10 | Fix shared property domain inference bug | Added `_set_owl_domain()` with `_attr_domains` tracking dict. Removes `rdfs:domain` when property appears on multiple types. 4 regression tests added. |
| 2026-03-10 | Write regression tests for all bugs found | 4 regression tests in `tests/test_text_descriptor.py`: shared domain removal, 3-type domain, cross-type SHACL, full MTG instance validation. |
| 2026-03-10 | Accepted: shared-domain removal trade-off | User confirmed this validates the 2×2 architecture — OWL domain is inference (open-world), SHACL target is constraint (closed-world). Quality criterion checked. |
