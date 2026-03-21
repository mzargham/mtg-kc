# Partially Resolved: Persistent Data Layer

## Status: Partially resolved — file I/O in [`knowledgecomplex`](https://github.com/BlockScience/knowledgecomplex) v0.1.0; triple store backend remains open

The published `knowledgecomplex` package provides file-based persistence:

- `save_graph(kc, path, format="turtle")` — serialize to file (Turtle, JSON-LD, N-Triples, RDF/XML)
- `load_graph(kc, path, format=None, validate=False)` — parse file into instance graph (additive)
- `dump_graph(kc, format="turtle")` — return serialized graph as string

**Still open (feature request for knowledgecomplex):** The triple store backend
(Apache Jena Fuseki or similar) described below has not been implemented. The
in-memory architecture with per-mutation SHACL validation remains the only option.

---

## Original Issue (preserved for reference)

### Status: Deferred

## Summary

The `KnowledgeComplex` currently holds its entire state in memory as three
separate `rdflib.Graph` objects (OWL ontology, SHACL shapes, instance data).
Every mutation triggers a full `pyshacl.validate()` pass over these in-memory
graphs. This architecture works for small demonstrators but does not scale to
models with hundreds or thousands of elements.

Because the framework already uses OWL, SHACL, and SPARQL internally, a
persistent triple store backend is a natural evolution. The abstraction
boundary (H6) hides all RDF machinery from the public API — swapping the
storage backend would require no changes to user-facing code.

## Motivation

### Evidence from WP4.8

The import/export QC work made the in-memory costs visible:

- **Three graphs per instance.** Each `KnowledgeComplex` holds a copy of the
  OWL ontology (~5KB), SHACL shapes (~8KB), and instance data (~22KB for the
  25-element MTG model). These are fully materialized rdflib graphs with
  in-memory triple indices.

- **Full validation per mutation.** `pyshacl.validate()` runs against the
  entire instance graph on every `add_vertex()`, `add_edge()`, and
  `add_face()` call. For the MTG model this takes milliseconds, but
  validation cost grows with graph size — it is O(shapes × triples) in the
  general case.

- **Reconstruct-from-scratch on load.** `KnowledgeComplex.load()` parses all
  Turtle files into fresh in-memory graphs. There is no incremental loading
  or lazy materialization.

- **No concurrent access.** rdflib's in-memory store has no locking or
  transaction support. Two processes cannot safely share a graph.

### Scaling concerns

A model with 1,000 elements (vertices + edges + faces) with 10 attributes
each would produce ~10,000+ triples in the instance graph alone. With
per-mutation SHACL validation, adding the 1,000th element validates against
all previous 999 elements' triples — a quadratic cost profile.

## Candidate: Apache Jena Fuseki

Apache Jena Fuseki is a natural fit because it speaks the same standards the
framework already uses:

- **Native SPARQL 1.1 endpoint.** Existing `.sparql` query templates would
  work unchanged — the only difference is whether SPARQL executes against an
  in-memory rdflib graph or a remote Fuseki endpoint.

- **Named graph support.** Ontology, shapes, and instance data can live in
  separate named graphs within a single dataset, matching the current
  three-graph architecture.

- **Built-in SHACL validation.** Fuseki can be configured with a SHACL
  validation service, potentially offloading validation from the Python
  client entirely.

- **OWL reasoning.** Jena provides configurable reasoners (RDFS, OWL micro,
  OWL mini, OWL full) that can be attached to a dataset.

- **Persistent storage (TDB2).** Eliminates in-memory overhead. Data
  survives process restarts. Supports concurrent read access.

Other candidates (Oxigraph, GraphDB, Stardog) would also work — the key
requirement is a SPARQL 1.1 endpoint with named graph and SHACL support.

## Architecture Sketch

### What would change

- **`KnowledgeComplex` gets a `backend` parameter.** Default: `"memory"` for
  the current rdflib-based behavior. A `"fuseki"` backend would accept a
  connection URL and dataset name.

- **Mutations become SPARQL UPDATE.** `add_vertex()` etc. would issue
  `INSERT DATA` operations rather than `graph.add()` calls. The Python
  methods remain the same — only the internal dispatch changes.

- **Queries become remote SPARQL SELECT.** `query()` would POST the SPARQL
  template to the Fuseki endpoint instead of calling `graph.query()`.

- **Validation options.** Either:
  - Server-side: Fuseki's SHACL service validates on each update (simplest)
  - Client-side: fetch relevant triples, validate locally (current approach)
  - Hybrid: validate locally for fast feedback, server-side for consistency

- **Export/load become graph upload/download.** `export()` would dump named
  graphs to Turtle files (same format). `load()` would upload Turtle files
  into named graphs. The file format is unchanged.

### What doesn't change

- **Public API.** `SchemaBuilder`, `KnowledgeComplex`, `query()`,
  `add_vertex()`, `add_edge()`, `add_face()`, `export()`, `load()` — all
  signatures remain the same.

- **SPARQL templates.** Both framework (`kc/queries/`) and model-specific
  (`models/*/queries/`) templates work unchanged.

- **Export file format.** The `ontology.ttl` + `shapes.ttl` + `instance.ttl`
  + `queries/*.sparql` directory structure is backend-independent.

- **Abstraction boundary (H6).** Users still never import rdflib, pyshacl,
  or Jena. The backend is an implementation detail.

## Design Questions

### DQ1: Client-Side vs. Server-Side SHACL Validation

Server-side validation (Fuseki SHACL service) is simpler and ensures
consistency, but adds network latency per mutation. Client-side validation
(current approach) gives immediate feedback but requires fetching graph
state. A hybrid — validate locally, enforce server-side — may be optimal.

### DQ2: Named Graph Strategy

Options:
- One named graph per layer (ontology, shapes, instance) per model namespace
- One dataset per model with fixed graph names
- A single default graph with layer metadata as triples

The first option maps cleanly to the current three-graph architecture and
supports multi-model composition (see `docs/issues/model-composition.md`).

### DQ3: Transaction Semantics

`add_vertex()` should be atomic with validation: either the element is added
and valid, or the graph is unchanged. With a remote store, this requires
either:
- SPARQL UPDATE with conditional logic (complex)
- Optimistic insert + rollback on validation failure
- Client-side staging before commit

### DQ4: Connection Lifecycle

Who starts and stops the Fuseki server?
- External: user manages Fuseki independently (simplest, most flexible)
- Embedded: `KnowledgeComplex` starts a Fuseki process (convenient but
  adds a JVM dependency)
- Docker: provide a `docker-compose.yml` for development

## Affected Components (When Implemented)

- `kc/graph.py` — backend abstraction in `KnowledgeComplex`
- `kc/backends/` — new module for backend implementations (memory, fuseki)
- `kc/schema.py` — `SchemaBuilder.upload()` for pushing schema to a store
- `tests/` — backend-parametrized tests (run same tests against memory and
  fuseki backends)
- `docs/ARCHITECTURE.md` — new DD for backend abstraction

## See Also

- `docs/issues/query-api.md` — SPARQL execution would benefit most from a
  persistent backend (server-side query optimization, caching)
- `docs/issues/model-composition.md` — multi-model scenarios need shared
  persistent state more than single-model use cases
- `docs/ARCHITECTURE.md` — DD2 (SPARQL Templates), H6 (API Opacity)
