# Issue: Support Oriented Simplices

## Status: Deferred (documented simplification)

## Motivation

Mathematical simplicial complexes distinguish between oriented and unoriented elements.
Orientation is a single bit per simplex that determines whether the boundary operator
produces an ordered list (oriented) or an unordered set (unoriented).

- **Vertices**: Orientation is irrelevant (no boundary, only coboundary)
- **Edges**: Oriented = directed (source, target); Unoriented = undirected (two endpoints)
- **Faces**: Oriented = boundary edges have a winding direction; Unoriented = boundary is a set

The current demo assumes **all simplices are unoriented**. This is correct for the MTG
color wheel where relationships are symmetric (White-Blue is the same as Blue-White).

## Current Implementation

A single `kc:boundedBy` property serves as the dimension-polymorphic boundary operator:
- Edge `boundedBy` Vertex (cardinality 2, unordered)
- Face `boundedBy` Edge (cardinality 3, unordered)

Coboundary (inverse boundary) is computed via SPARQL query (`kc/queries/coboundary.sparql`),
not stored as triples.

## What Would Change for Oriented Support

### OWL Ontology

Option A — Split property by orientation:
- Oriented edges: `kc:hasSource` and `kc:hasTarget` (each cardinality 1)
- Unoriented edges: `kc:boundedBy` (cardinality 2, as currently)
- Orientation declared per-type in the schema

Option B — Add orientation flag:
- Keep `kc:boundedBy` but add `kc:oriented` boolean datatype property
- When oriented, impose an ordering convention (e.g., `rdf:List` or positional blank nodes)

### SHACL Shapes

- EdgeShape: orientation-aware distinctness constraint
- FaceShape: closed-triangle constraint needs to respect edge direction
  (cycle direction matters for oriented faces)

### Python API

- `add_edge()`: When oriented, accept `source`/`target` instead of `vertices`
- `add_face()`: When oriented, boundary list order matters
- Schema: `add_edge_type(..., oriented=True)` flag

### SPARQL Queries

- Edge queries need orientation-aware patterns
- Coboundary query is unaffected (always "find what contains me")

## Affected Files (from impact analysis)

1. `kc/resources/kc_core.ttl`
2. `kc/resources/kc_core_shapes.ttl`
3. `kc/graph.py`
4. `kc/schema.py`
5. `tests/test_core_owl.py`
6. `tests/test_core_shacl.py`
7. `models/mtg/queries/edges_by_disposition.sparql`
8. `docs/ARCHITECTURE.md`
9. `docs/REQUIREMENTS.md`

## Scope

This is a **framework-level** (Layer 1) change. Domain models (Layer 2) would declare
their orientation preference in the schema definition. The MTG demo model would remain
unoriented even after this feature is implemented.
