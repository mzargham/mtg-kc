# Issue: Support Temporal Complex Ordering

## Status: Deferred (documented simplification)

## Motivation

The current implementation enforces the **slice rule**: at every point during construction,
the elements added so far must form a valid complex (closed under the boundary operator).
This is a partial ordering — an element's boundary elements must be added before the element
itself, but elements of the same simplex order can be interleaved freely.

The demo satisfies this rule trivially by adding elements in type order: all vertices (k=0),
then all edges (k=1), then all faces (k=2). This is correct but discards potentially
meaningful information about construction order.

## Temporal Complex Interpretation

If the insertion sequence is treated as temporally ordered, the slice rule gains additional
semantic content: each prefix `elements[0:n]` represents the state of the complex at time
step n. The complex "grows" over time, and the growth sequence is itself a meaningful object.

This interpretation enables:
- **Filtration**: a nested sequence of subcomplexes C₀ ⊆ C₁ ⊆ ... ⊆ Cₙ, each valid
- **Persistent homology**: tracking which topological features (connected components, cycles,
  voids) appear and disappear as the complex grows
- **Provenance**: knowing when each element was introduced and what motivated it
- **Incremental validation**: each step's validity is guaranteed by the slice rule

## Current Implementation

The slice rule is enforced by `ComplexShape` boundary-closure SHACL validation on every write.
The insertion order is not recorded — only the final complex state is stored in the RDF graph.

## What Would Change for Temporal Support

### RDF Representation

Option A — Ordered element list:
- Replace `kc:hasElement` (unordered) with an `rdf:List` or positional blank nodes
- Each element gets a timestamp or sequence number

Option B — Snapshot sequence:
- Each time step creates a named graph (or a new Complex individual)
- The filtration is the sequence of graphs

Option C — Annotation:
- Keep `kc:hasElement` but add `kc:addedAt` annotation (integer or timestamp) to each element
- Reconstruct the filtration by sorting on `addedAt`

### Python API

- `add_vertex()` / `add_edge()` / `add_face()` would record insertion order
- New method: `filtration() -> list[set[str]]` returning the sequence of element sets
- New method: `complex_at(step: int) -> KnowledgeComplex` returning a snapshot

### SPARQL Queries

- Filtration queries: "what elements existed at step n?"
- Birth/death queries: "when did this topological feature first appear?"

## Affected Files (from impact analysis)

1. `kc/resources/kc_core.ttl` — add ordering annotation or list property
2. `kc/resources/kc_core_shapes.ttl` — temporal slice-rule constraint
3. `kc/graph.py` — record insertion order, filtration/snapshot methods
4. `tests/test_knowledge_complex.py` — temporal ordering tests
5. `docs/ARCHITECTURE.md` — describe temporal complex interpretation

## Scope

This is a **framework-level** (Layer 1) change. The current demo does not require temporal
ordering — it constructs the complete complex in one batch. Temporal ordering becomes relevant
for dynamic or evolving knowledge complexes where the construction process itself is data.
