# Feature Request: Boundary-Derived Attribute Constraints

## Status: Feature request for [`knowledgecomplex`](https://github.com/BlockScience/knowledgecomplex)

The proposed `add_boundary_attribute_constraint()` API does not exist in
`knowledgecomplex` v0.1.0. Model authors must still write raw `sh:sparql`
constraints via `add_sparql_constraint()` for cross-element attribute checks.

---

## Original Issue (preserved for reference)

### Status: Deferred

## Summary

A recurring model-level constraint pattern: **an attribute on a simplex must
equal the collection of values of a specific attribute from its boundary
elements.** The `thematic_triad` property on `ColorTriple` is the canonical
example — it must contain exactly the three `theme` values from its three
bounding `ColorPair` edges, no more and no less.

Currently this requires two raw `sh:sparql` constraints registered via
`add_sparql_constraint()`:

```python
# models/mtg/schema.py — current form

sb.add_sparql_constraint(
    "ColorTriple",
    f"""
    PREFIX kc: <{_KC}>
    PREFIX mtg: <{_MTG}>
    SELECT $this WHERE {{
        $this kc:boundedBy ?edge .
        ?edge mtg:theme ?edgeTheme .
        FILTER NOT EXISTS {{
            $this mtg:thematic_triad ?edgeTheme .
        }}
    }}
""",
    "thematic_triad is missing at least one theme from a bounding edge.",
)
sb.add_sparql_constraint(
    "ColorTriple",
    f"""
    PREFIX kc: <{_KC}>
    PREFIX mtg: <{_MTG}>
    SELECT $this WHERE {{
        $this mtg:thematic_triad ?triadTheme .
        FILTER NOT EXISTS {{
            $this kc:boundedBy ?edge .
            ?edge mtg:theme ?triadTheme .
        }}
    }}
""",
    "thematic_triad contains a value that is not a theme of any bounding edge.",
)
```

This is 30 lines of SPARQL boilerplate encoding a single, clean idea: **set
equality between a face attribute and the boundary-derived values of an edge
attribute.** The pattern is general enough to appear in any model that stores
derived relational data explicitly alongside the structure that implies it.

The goal of this issue is a `SchemaBuilder` API that generates this SPARQL
automatically from a declarative Python description.

## The Pattern

Set-equality between a simplex attribute and a boundary-attribute projection
decomposes into two SPARQL `FILTER NOT EXISTS` constraints:

1. **Coverage** — every boundary attribute value appears in the face attribute:
   `∀e ∈ ∂(face): e.attr ∈ face.derived_attr`

2. **Exactness** — every face attribute value comes from some boundary element:
   `∀v ∈ face.derived_attr: ∃e ∈ ∂(face): e.attr = v`

Both directions are needed. Coverage alone allows extra values; exactness alone
allows missing values.

## Proposed API

```python
sb.add_boundary_attribute_constraint(
    type_name="ColorTriple",
    attribute="thematic_triad",
    boundary_attribute="theme",
    boundary_type="ColorPair",   # optional: filter boundary by subclass
)
```

This would generate the two SPARQL constraints automatically, with appropriate
`PREFIX` declarations derived from the builder's namespace and the KC base IRI.

### Signature

```python
def add_boundary_attribute_constraint(
    self,
    type_name: str,
    attribute: str,
    boundary_attribute: str,
    boundary_type: str | None = None,
) -> "SchemaBuilder":
    """
    Assert that `attribute` on elements of `type_name` equals exactly the
    set of `boundary_attribute` values collected from all boundary elements
    (optionally filtered to `boundary_type`).

    Generates two sh:sparql constraints on the type's SHACL shape:
      1. Coverage: every boundary element's attribute value appears in attribute.
      2. Exactness: every attribute value comes from some boundary element.

    Both constraints use FILTER NOT EXISTS, following the same pattern as the
    KC core topological constraints in kc_core_shapes.ttl.
    """
```

### Generated SPARQL

The method generates parameterized forms of the two patterns. With
`boundary_type` specified, the `kc:boundedBy ?edge` pattern gains a type
filter `?edge a <BoundaryType>`. Without it, all boundary elements are
considered.

```sparql
# Generated — coverage constraint
SELECT $this WHERE {
    $this kc:boundedBy ?boundary .
    ?boundary a <BoundaryType> .          # only if boundary_type specified
    ?boundary <ns:boundary_attribute> ?bval .
    FILTER NOT EXISTS {
        $this <ns:attribute> ?bval .
    }
}

# Generated — exactness constraint
SELECT $this WHERE {
    $this <ns:attribute> ?aval .
    FILTER NOT EXISTS {
        $this kc:boundedBy ?boundary .
        ?boundary a <BoundaryType> .      # only if boundary_type specified
        ?boundary <ns:boundary_attribute> ?aval .
    }
}
```

## Relationship to Existing Issues

### `docs/issues/query-api.md`

This constraint pattern is the validation-side dual of the **boundary traversal
query**. The query API asks "what are the boundary elements and their
attributes?" The constraint here asks "does the stored attribute agree with
what the boundary traversal would return?"

Once `kc.boundary(element)` exists as a first-class Python operation, a natural
validation mode is:

```python
# Hypothetical: validate at Python level using query API
def check_boundary_attribute(kc, face_id, attribute, boundary_attribute):
    expected = {kc.get_attr(e, boundary_attribute)
                for e in kc.boundary(face_id)}
    stored = set(kc.get_attrs(face_id, attribute))
    return expected == stored
```

The SHACL `sh:sparql` form (this issue) and the Python-side check (query API)
are equivalent but serve different roles: SHACL fires automatically on write;
the Python form is available for interactive inspection and debugging.

### `docs/issues/local-rule-authoring.md`

This issue is a concrete, motivated instance of the **Python Rule Builder**
option (sub-issue 3, Option B in that document). The
`add_boundary_attribute_constraint()` method is the first entry in a
`SchemaBuilder` rule-authoring API that generates SPARQL constraints from
higher-level descriptions.

The boundary-attribute equality pattern is the simplest and most common case.
More complex patterns from `local-rule-authoring.md` (coboundary-existence,
degree constraints, link-membership) would follow the same design: a named
`add_*_constraint()` method on `SchemaBuilder` that generates the appropriate
`sh:sparql` constraint, hiding the SPARQL from the model author.

## Additional Pattern Variants

The basic pattern generalizes in two directions worth tracking:

### Partial projection (subset, not equality)

Instead of full set-equality, some rules need set-containment:

- `∀e ∈ ∂(face): e.attr ∈ face.derived_attr` — coverage only (face may have
  additional values from non-boundary sources)
- `∀v ∈ face.derived_attr: ∃e ∈ ∂(face): e.attr = v` — exactness only (every
  stored value must be justified, but not every boundary value need appear)

A `mode` parameter (`"equality"` | `"coverage"` | `"exactness"`) would cover
all three cases. The default should be `"equality"` — the most restrictive and
most commonly useful form.

### Aggregated projection (count, concat)

Rules where the face attribute is a derived aggregate rather than a direct
set projection:

- `face.edge_count = |∂(face)|` — count of boundary elements
- `face.vertex_labels = sorted labels of boundary vertices` — ordered
  concatenation

These require aggregation SPARQL and are more complex to generate. Defer to a
follow-on issue if needed.

## Concrete Starting Point

The MTG `thematic_triad` constraint is the reference implementation. When
this issue is worked:

1. Add `add_boundary_attribute_constraint()` to `SchemaBuilder`
2. Replace the two `add_sparql_constraint()` calls in `models/mtg/schema.py`
   with one `add_boundary_attribute_constraint()` call
3. Verify generated SPARQL is functionally equivalent by running tests and
   checking validation still catches invalid `thematic_triad` values

The generated SHACL should be indistinguishable from the hand-written form in
`shapes.ttl`. Tests should continue to pass without modification.

## Affected Components (When Implemented)

- `kc/schema.py` — new `add_boundary_attribute_constraint()` method on
  `SchemaBuilder`
- `models/mtg/schema.py` — replace two `add_sparql_constraint()` calls
- `tests/` — new tests for the method (correct SPARQL generation, correct
  validation behavior for both coverage and exactness violations)

## See Also

- `docs/issues/query-api.md` — boundary traversal as a query primitive; this
  issue is the constraint-authoring dual of that query capability
- `docs/issues/local-rule-authoring.md` — broader context for model-level
  rule authoring via the `SchemaBuilder` API (this issue implements Option B,
  sub-issue 3 of that document, for the boundary-attribute equality pattern)
- `kc/resources/kc_core_shapes.ttl` — canonical examples of `sh:sparql`
  constraints using `kc:boundedBy` that this method generalizes
- `models/mtg/schema.py` — `_THEMATIC_TRIAD_MISSING` and
  `_THEMATIC_TRIAD_EXTRA` — the motivating SPARQL that this API should replace
