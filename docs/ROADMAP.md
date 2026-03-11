# Roadmap

## What Was Built

The `kc` package demonstrates that the semantic web toolchain (OWL + SHACL + SPARQL via `rdflib`/`pyshacl`) is sufficient to implement the three-layer knowledge complex framework, with the 2×2 complexity {topological, ontological} × {OWL, SHACL} hidden behind a Python DSL.

**Core framework:** Abstract OWL ontology and SHACL shapes defining simplicial structure (vertices, edges, faces) with boundary operators and cardinality constraints. The closed-triangle rule — the topological expressivity limit of OWL — is enforced via `sh:sparql`.

**Python API:** `SchemaBuilder` (schema definition with `vocab()` and `text()` descriptors, single-call OWL+SHACL invariant) and `KnowledgeComplex` (instance graph with validate-on-write, named SPARQL templates, DataFrame query results).

**MTG demonstrator:** 5 colors, 10 edges (adjacent/opposite), 10 faces. The `shard`/`wedge` classification is discovered via SPARQL query, then promoted to a required attribute — demonstrating the verification→discovery→schema-evolution loop.

**All six hypothesis criteria passed** (208 tests, 0 skipped). See [worklog/README.md](../worklog/README.md) for the plan-vs-actuals comparison.

---

## Dependency Stack

| Layer | Tool | Role |
|---|---|---|
| RDF graph + SPARQL | `rdflib` | In-memory triple store and query engine |
| OWL-RL inference | `owlrl` | Subclass/property inheritance |
| SHACL validation | `pyshacl` | Constraint checking on write |
| Notebook | `marimo` | Reactive exploration |
| Serialization | `rdflib` Turtle | Dump OWL/SHACL for inspection |

---

## Open Issues

Each issue has a dedicated file in [`docs/issues/`](issues/).

| Issue | Summary | Priority |
|-------|---------|----------|
| [Persistent data layer](issues/persistent-data-layer.md) | In-memory rdflib graphs don't scale; Apache Jena Fuseki as candidate backend | High |
| [Model composition](issues/model-composition.md) | Combining independently authored model families into a single complex | High |
| [SKOS vocabularies](issues/skos-vocabularies.md) | Replace `sh:in` string lists with SKOS concept schemes for richer vocabulary semantics | Medium |
| [Query API](issues/query-api.md) | Richer query composition, parameterized templates, result typing | Medium |
| [Orientation support](issues/orientation-support.md) | Oriented simplices (directed edges, oriented faces) for asymmetric relations | Medium |
| [Temporal ordering](issues/temporal-ordering.md) | Time-indexed snapshots of the complex for schema evolution tracking | Low |
| [Local rule authoring](issues/local-rule-authoring.md) | User-defined SHACL/SPARQL rules without touching core resources | Low |

---

## Hypothesis Test Criteria

These criteria drove the demonstrator design and are preserved here as the validation contract for future development.

| ID | Criterion | Pass condition |
|---|---|---|
| H1 | 2×2 coverage | All four cells of the responsibility map have at least one concrete rule |
| H2 | Topological limit documented | Closed-triangle constraint is in SHACL `sh:sparql`; comment explains why OWL cannot express it |
| H3 | Single-call invariant | `add_edge_type` and `promote_to_attribute` each produce changes in both OWL and SHACL dumps |
| H4 | Verification works | SHACL catches a malformed face and produces a readable report |
| H5 | Discovery works | SPARQL reveals `shard`/`wedge` split without it being pre-asserted |
| H6 | API opacity | The notebook never imports `rdflib`, `pyshacl`, or `owlrl` directly |

---

## Design Decisions

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full decision log (DD1–DD7). Key decisions that shape future work:

- **DD6 — Shared-domain removal:** When a property name appears on multiple types, `rdfs:domain` is removed to prevent RDFS inference from cross-classifying individuals. Future model composition must respect this invariant.
- **DD7 — vocab() vs text():** Two descriptor types with different OWL/SHACL generation. Future descriptors (e.g., numeric ranges, URI references) should follow this pattern.

---

## Terminology

| Canonical | Deprecated | Notes |
|-----------|------------|-------|
| color wheel | color pentagon | Matches the source essay title |
| structure | pattern | Face classification attribute name |
| shard | ooa | Face with 2 opposite + 1 adjacent edges |
| wedge | oaa | Face with 1 opposite + 2 adjacent edges |

See [docs/issues/terminology-audit.md](issues/terminology-audit.md) for regression checking.
