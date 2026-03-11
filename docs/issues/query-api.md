# Deferred Issue: Simplicial Complex Query API

## Status: Deferred

## Summary

The `KnowledgeComplex` needs a read-only query API that leverages the native
structure of simplicial complexes. The standard operations — boundary, coboundary,
star, link, closure, skeleton — are mathematically well-defined traversal
primitives that compose with element type filtering via the OWL class hierarchy.

These operations belong in the `kc:` framework layer. They work for any model
family because they operate on the topological structure (`kc:boundedBy`,
`kc:hasElement`) rather than model-specific attributes.

Currently the query surface is minimal: `KnowledgeComplex.query(template_name)`
dispatches to named SPARQL templates, with only 4 templates defined (2 framework:
`vertices`, `coboundary`; 2 model-specific: `edges_by_disposition`,
`faces_by_edge_pattern`). The `coboundary` template is still a stub.

## Sub-Issues

### 1. Primitive Traversals: Boundary & Coboundary

The two atomic operations from which all other traversals are composed.

**Boundary** `∂(σ)` — the faces of a simplex:

- Vertex → ∅ (empty boundary, dimension 0)
- Edge → {v1, v2} (two boundary vertices)
- Face → {e1, e2, e3} (three boundary edges)
- Already stored as `kc:boundedBy` triples
- SPARQL: `?σ kc:boundedBy ?face`

**Coboundary** `δ(σ)` — the cofaces of a simplex (inverse boundary):

- Vertex → edges whose boundary includes that vertex
- Edge → faces whose boundary includes that edge
- Not a stored property — derived by inverse traversal of `kc:boundedBy`
- SPARQL: `?coface kc:boundedBy ?σ` (equivalently, `?σ ^kc:boundedBy ?coface`)
- Already stubbed in `kc/queries/coboundary.sparql`

Boundary and coboundary are duals. Boundary lowers dimension; coboundary raises it.
Together they define the full local neighborhood of any simplex.

### 2. Star & Closed Star

**Star** `St(σ)` = {τ ∈ K : σ is a face of τ} — all simplices that contain σ
as a face, including σ itself. This is the transitive coboundary.

- For vertex v: {v} ∪ {edges containing v} ∪ {faces containing those edges}
- For edge e: {e} ∪ {faces containing e}
- SPARQL mechanism: `?τ ^kc:boundedBy* ?σ` (transitive inverse boundary path)

The star is *not* a subcomplex — it is not closed under boundary. For example,
St(v) contains a face f but may not contain all of f's boundary edges (only those
that pass through v).

**Closed Star** `St̄(σ)` = Cl(St(σ)) — the closure of the star. The star plus
all boundary elements of star members. The closed star *is* always a subcomplex
(closed under boundary by construction).

### 3. Link

**Link** `Lk(σ)` = Cl(St(σ)) \ St(σ) — the "horizon" around σ. Elements in the
closed star that do not themselves contain σ.

Equivalently: Lk(σ) = {τ ∈ K : τ ∩ σ = ∅ and τ ∪ σ ∈ K}.

- For vertex v: the other vertices connected to v by an edge, plus the edges
  of incident faces that don't contain v
- Intuitively: the link is the boundary of the neighborhood, the "ring" around σ

**Structural invariant:** In a triangulated surface (closed 2-manifold), the link
of every vertex is a cycle. This is a checkable structural property that can
validate mesh quality and detect boundary vertices vs. interior vertices.

### 4. Closure

**Closure** `Cl(S)` for a set of simplices S = the smallest subcomplex containing
S. S plus all faces of elements in S, applied transitively.

- SPARQL mechanism: `?σ kc:boundedBy* ?face` for each σ ∈ S (transitive boundary)
- Always produces a valid subcomplex (closed under boundary by definition)

**Use case:** "Give me these three edges and everything they depend on." The closure
is the minimal valid subcomplex containing a given selection. This is the
topological analogue of dependency resolution — the closure of a set of simplices
includes all their prerequisites.

### 5. Skeleton & Element Enumeration

**k-Skeleton** `sk_k(K)` = all simplices of dimension ≤ k.

- `skeleton(0)` = all vertices
- `skeleton(1)` = all vertices + edges
- `skeleton(2)` = everything (in the current 2-complex)
- Mechanism: filter by `rdfs:subClassOf*` from `kc:Vertex`, `kc:Edge`, `kc:Face`

**Element enumeration** `elements(type=None)` — all elements in the complex,
optionally filtered by type at any level of the OWL hierarchy.

**Degree** `deg(v)` = |δ(v)| — number of edges incident to a vertex. A derived
scalar from coboundary. In the MTG model, degree is the number of ColorPair
edges meeting at a Color vertex (always 4 in the complete MTG color graph: 2
adjacent + 2 opposite).

### 6. Type Filtering (Cross-Cutting)

All traversal operations should accept an optional `type` parameter that filters
results using the OWL class hierarchy (`rdfs:subClassOf*`):

- `star("White", type="Edge")` → only edges in the star (skip vertices and faces)
- `coboundary("White", type="ColorPair")` → only ColorPair edges (model-level
  subclass of `kc:Edge`)
- `elements(type="Vertex")` → framework-level filter
- `elements(type="Color")` → model-level filter (equivalent for MTG, but
  distinct in a multi-type model)

Type filtering composes with any traversal. SPARQL implementation uses
`?x a/rdfs:subClassOf* <type>` in a FILTER or join pattern.

## Design Questions

### DQ1: Return Type

Should these methods return `pd.DataFrame` (consistent with `query()`) or
`set[str]` (more natural for element ID collections)?

A DataFrame carries richer information (type, attributes) but may be awkward for
set operations (union, intersection, difference) that are natural when composing
traversals. One option: return element ID sets from traversal methods, with a
separate `describe(element_ids)` method to materialize full details as a DataFrame.

### DQ2: Python Methods vs. SPARQL Templates

DD2 mandates named SPARQL templates, not free queries. But star/link/closure are
so fundamental to the data model that they may warrant first-class Python methods:

```python
# Option A: template dispatch (DD2-compliant)
kc.query("star", simplex="White")

# Option B: first-class methods (more Pythonic)
kc.star("White")
kc.link("White", type="ColorPair")

# Option C: methods that internally dispatch to templates
# (Pythonic surface, templates underneath)
```

Option C is likely the right resolution: the methods are framework-provided
convenience wrappers, the templates remain the source of truth, and DD2 is
preserved in spirit (no ad-hoc SPARQL).

### DQ3: Composability

Can traversals compose? Examples:

- `closure(star("White") & type=="Edge")` — closure of the edge-filtered star
- `link(star("White"))` — link of the star (higher-order operation)
- `star("White") - star("Blue")` — set difference of two stars

This is a query algebra question. Options range from "named operations are
sufficient, compose manually in Python" to a full query builder pattern with
lazy evaluation. The former is simpler and likely sufficient for the demonstrator.

### DQ4: Performance

SPARQL property paths (`^kc:boundedBy*`, `kc:boundedBy*`) give us transitive
operations for free, but rdflib's SPARQL engine may not optimize these well for
large complexes. For the MTG demonstrator (5 vertices, 10 edges, 10 faces) this
is irrelevant. For larger complexes, materialized views or Python-side traversal
may be needed. Flag but do not solve now.

### DQ5: Dimension Awareness

Dimension is currently implicit in the class hierarchy: Vertex=0, Edge=1, Face=2.
Should `kc:dimension` be an explicit datatype property on `kc:Element` subclasses?

**Pro:** Simplifies skeleton queries (`?x kc:dimension ?d . FILTER(?d <= 1)`),
enables dimension-generic operations, and makes the mathematical structure
explicit in the ontology.

**Con:** Redundant with the class hierarchy. Adds a property that must be kept
in sync. The class hierarchy already encodes dimension via `rdfs:subClassOf`.

**Possible resolution:** Add `kc:dimension` as an OWL annotation property on the
classes themselves (not on individuals), so `kc:Vertex kc:dimension 0` etc. This
avoids per-individual redundancy while making the dimension queryable.

## Relationship to Existing Architecture

- **DD2 (SPARQL Templates, Not Free Queries):** The traversal operations would
  be implemented as framework SPARQL templates in `kc/queries/`, loaded
  automatically for any `KnowledgeComplex` instance. Model-specific queries
  remain in `models/{name}/queries/`.

- **`kc/queries/coboundary.sparql`:** Already stubbed. Sub-issue 1 would
  complete this implementation and add `boundary.sparql`.

- **`kc/queries/vertices.sparql`:** An existing element enumeration query.
  Sub-issue 5 would generalize this to all element types and add skeleton support.

- **Type hierarchy (`rdfs:subClassOf*`):** Already used in existing SPARQL
  queries (`vertices.sparql`, `faces_by_edge_pattern.sparql`). Sub-issue 6
  formalizes this as a composable filter across all traversals.

## Affected Components (When Implemented)

- `kc/graph.py` — new read-only methods on `KnowledgeComplex`
- `kc/queries/` — new framework SPARQL templates (boundary, star, link, closure,
  skeleton, elements, degree)
- `kc/resources/kc_core.ttl` — possibly `kc:dimension` annotation (DQ5)
- `tests/` — new tests for each traversal operation
- `docs/REQUIREMENTS.md` — new REQ-QUERY-* requirements
- `docs/ARCHITECTURE.md` — update DD2 discussion if Python methods are added

## See Also

- `docs/ARCHITECTURE.md` — DD2 (SPARQL Templates), type hierarchy
- `docs/issues/orientation-support.md` — oriented boundary (directed edges)
  would affect boundary/coboundary semantics
- `docs/issues/model-composition.md` — cross-model queries need traversals
  that span multiple model namespaces
