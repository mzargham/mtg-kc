# Deferred Issue: Local Rule Authoring via Query Primitives

## Status: Deferred

## Summary

Model families need SHACL constraints that reference the **topological
neighborhood** of an element — not just its own properties or immediate boundary,
but the coboundary, star, link, or closure of related elements. The core query
API (see `docs/issues/query-api.md`) provides the traversal primitives; this
issue addresses how model authors use those primitives to write shape constraints.

The current SHACL shapes (`kc_core_shapes.ttl`) enforce framework-level topology:
edge has 2 distinct boundary vertices, face forms a closed triangle, complex is
closed under boundary. These are universal invariants. Model-level rules are
domain-specific constraints that extend this foundation — they express when a
particular configuration of typed elements is valid, using the topological
neighborhood as context.

## Motivating Example: V&V Assurance Model

Consider a Validation & Verification model with the following element types:

**Vertices:** Doc, Spec, Guidance, Actor

**Edges** (with typed boundary):

| Edge Type       | Boundary         | Meaning                                     |
|-----------------|------------------|---------------------------------------------|
| Coupling        | [Spec, Guidance] | Spec is governed by this guidance            |
| Verification    | [Spec, Doc]      | Doc verifies (implements) this spec          |
| Validation      | [Guidance, Doc]  | Doc is validated against this guidance       |
| Review          | [Actor, Doc]     | Actor reviewed this doc                      |
| Qualification   | [Actor, Guidance]| Actor is qualified to assess against this guidance |

**Faces** (with typed boundary):

| Face Type  | Boundary                                    | Meaning                                  |
|------------|---------------------------------------------|------------------------------------------|
| Assurance  | [Coupling, Verification, Validation]        | Full traceability triangle               |
| Approval   | [Validation, Review, Qualification]         | Actor-backed validation approval         |

The two triangles share the Validation edge and the Doc and Guidance vertices:

```
        Spec
       / |  \
 Coupling |  Verification
     /    |    \
Guidance--+-----Doc
     \    |    /
 Qualif.  |  Review
       \  |  /
        Actor

Assurance  = triangle(Spec, Guidance, Doc)   via Coupling, Verification, Validation
Approval   = triangle(Guidance, Doc, Actor)  via Validation, Review, Qualification
```

### The Assurance Prerequisite Rule

**Rule:** An Assurance face cannot be added unless the Validation edge in its
boundary is already part of an Approval face.

In plain language: you cannot claim full traceability (Assurance) until someone
(Actor) has actually approved the validation — i.e., reviewed the document
against the guidance, demonstrated they're qualified to do so, and signed off.

This rule requires **type-filtered coboundary**: "does the coboundary of the
Validation edge contain a face of type Approval?" This is a local topological
check — it examines the neighborhood of a boundary element, not global graph
state.

### Relationship to Temporal Ordering

The boundary partial order (slice rule) requires that the Validation edge exists
before the Assurance face. But the Assurance prerequisite rule adds a **lateral
prerequisite**: the Approval face must also exist, and it shares the Validation
edge but is not in the Assurance face's boundary.

This creates an ordering constraint that goes beyond the boundary partial order:

```
Vertices → Edges → Approval face → Assurance face
                         ↑                ↑
                   (lateral prerequisite)  │
                         └─────────────────┘
```

The insertion sequence `[...vertices, ...edges, Assurance, Approval]` would
fail validation even though it respects the boundary partial order. The valid
sequence is `[...vertices, ...edges, Approval, Assurance]`. When lateral
prerequisites exist, insertion order becomes semantically meaningful — this
connects directly to the temporal ordering deferred issue.

## Sub-Issues

### 1. Type-Filtered Coboundary in SHACL

The most immediately needed primitive. A model shape needs to assert: "for this
element, there exists a face of type T in the coboundary of boundary element E."

This is an `sh:sparql` constraint using `^kc:boundedBy` (inverse boundary path)
with a type filter:

```sparql
PREFIX kc: <https://example.org/kc#>
PREFIX vv: <https://example.org/vv#>

# AssuranceShape: the Validation edge must already be in an Approval face
# Reports a violation if no Approval face exists in the Validation edge's coboundary
SELECT $this WHERE {
    $this a vv:Assurance .
    $this kc:boundedBy ?validation_edge .
    ?validation_edge a vv:Validation .
    FILTER NOT EXISTS {
        ?approval_face a vv:Approval .
        ?approval_face kc:boundedBy ?validation_edge .
    }
}
```

This pattern — "boundary element's coboundary must contain a face of type X" —
is likely the most common form of model-level topological constraint. It checks
one hop beyond the element's own boundary.

### 2. Star/Link Predicates in SHACL

More complex rules that reference the full star or link of an element:

- **Degree constraints:** "every vertex in this face must have degree ≥ 3"
  (i.e., each boundary vertex must participate in at least 3 edges). Requires
  counting the coboundary of each boundary vertex.

- **Link membership:** "the link of this vertex must contain at least one face
  of type T." The link is Cl(St(σ)) \ St(σ) — elements in the closed star that
  don't contain σ. This is harder to express in a single SPARQL pattern.

- **Star completeness:** "every edge in the star of this vertex must be in at
  least one face." This checks that no edge is "dangling" in the neighborhood.

These compose the traversal primitives with cardinality checks and type filters.
They are more expressive than sub-issue 1 but also more complex to author.

### 3. Authoring Ergonomics

Writing raw `sh:sparql` SPARQL inside SHACL shapes is verbose, error-prone,
and requires the model author to understand both SPARQL and the KC topological
vocabulary. Options for reducing this burden:

**Option A: SPARQL Template Macros**

The framework provides parameterized SPARQL fragments that model authors embed
in their `sh:sparql` constraints:

```sparql
# Framework-provided macro (conceptual)
kc:typed_coboundary_exists(?element, ?boundary_edge_type, ?required_face_type)
```

In practice, these would be SPARQL subquery patterns or property path expressions
that the framework documents and the model author copy-pastes with type
substitutions.

**Option B: Python Rule Builder**

`SchemaBuilder` gains a rule-authoring API:

```python
sb.add_rule(
    target_type="Assurance",
    constraint="coboundary_contains",
    boundary_type="Validation",
    required_type="Approval",
    message="Assurance requires Approval on the Validation edge",
)
```

This generates the `sh:sparql` constraint automatically. More accessible to
model authors who aren't SPARQL experts, but less flexible.

**Option C: Constraint Vocabulary**

A small set of SHACL property shapes that encode common topological constraint
patterns:

```turtle
vvs:AssuranceShape
    kcs:requiresCoboundaryFace [
        kcs:onBoundaryType vv:Validation ;
        kcs:requiredFaceType vv:Approval ;
        sh:message "..." ;
    ] .
```

This extends the SHACL vocabulary with KC-specific constraint types. Most
declarative, but requires framework support for interpreting the custom
constraint properties.

### 4. Rule Interaction with Validation-on-Write

DD3 mandates SHACL validation on every write (the slice rule). Model-level rules
that reference the topological neighborhood create complications:

**Lateral prerequisites:** The Assurance rule requires an Approval face that
shares a boundary edge but is not itself in the Assurance face's boundary. This
creates an ordering dependency outside the boundary partial order. The model
author must know (or discover) that Approval must be added before Assurance.

**Deferred validation:** Some rules may reference elements that haven't been
added yet. Strict validation-on-write would reject the intermediate state. Two
options:

1. **Strict (current):** Model author is responsible for valid insertion order.
   Rules that create ordering constraints are documented as part of the model's
   API contract. Simple, predictable, but can be frustrating.

2. **Deferred:** Some constraints are marked as "deferred" — checked only when
   explicitly requested (e.g., `kc.validate()`) or at a phase boundary. This
   is more flexible but introduces the possibility of invalid intermediate
   states, which contradicts the slice rule's guarantee.

**Mutual dependencies:** If rule A requires the existence of element B, and
rule B requires element A, no insertion order is valid under strict
validation-on-write. Deferred validation or batched insertion would be needed.

**Recommendation:** Start with strict validation-on-write. Document ordering
constraints as part of the model's API. If real models frequently hit ordering
conflicts, introduce a `deferred_rules` parameter on `add_face()` that
temporarily suppresses specific model-level constraints, with a `validate()`
call to check them later.

## Design Questions

### DQ1: Rule Scope

Should model rules be limited to the **local neighborhood** (star, link, closed
star — bounded topological distance from the element) or allow **arbitrary graph
patterns** (any SPARQL over the full complex)?

Local-only is simpler, more predictable, and aligns with the simplicial complex
philosophy of local structure determining global properties. But some rules
may genuinely require non-local context (e.g., "no two Assurance faces in the
complex may share all three boundary edges" — a global uniqueness constraint).

**Recommendation:** Encourage local rules, support global rules via raw
`sh:sparql`. The framework's ergonomic aids (sub-issue 3) focus on local
patterns; global patterns are the escape hatch for expert authors.

### DQ2: Framework vs. Model SPARQL

Should the framework provide **pre-built SPARQL fragments** for common patterns
(coboundary-existence, star-cardinality, link-membership), or leave all SPARQL
authoring to the model?

The V&V example suggests reusable fragments would dramatically reduce
boilerplate. The coboundary-existence pattern alone covers a large class of
useful rules.

**Recommendation:** Start with 3-5 well-documented SPARQL patterns covering
the most common constraint forms. Evolve based on real model needs.

### DQ3: Validation Timing

When lateral prerequisites exist, should the framework support deferred
validation, or should the model author manage insertion ordering?

This connects directly to the temporal ordering deferred issue. If insertion
order is recorded (temporal complex), the ordering constraints become part of
the model's documented contract. If not, they're implicit and discoverable only
by trial and error.

**Recommendation:** Strict-by-default with an opt-in deferred mode. Document
ordering constraints as first-class model metadata.

## Prerequisite Issues

- **`docs/issues/query-api.md`** — the traversal primitives (boundary,
  coboundary, star, link, closure) that this issue builds on. Without core
  query infrastructure, model authors have to reinvent traversal patterns in
  every `sh:sparql` constraint.

## See Also

- `docs/issues/temporal-ordering.md` — insertion ordering becomes meaningful
  when lateral prerequisites exist
- `kc/resources/kc_core_shapes.ttl` — current framework-level SHACL shapes
  that model rules extend (EdgeShape, FaceShape, ComplexShape)
- `docs/ARCHITECTURE.md` — DD3 (validation on write), 2×2 responsibility map
  (topological × ontological, OWL × SHACL)
- `docs/issues/model-composition.md` — cross-model rules may need to reference
  types from multiple model namespaces
