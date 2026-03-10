# Deferred Issue: Model Composition

## Status: Deferred

## Summary

The KC framework is designed so that multiple model families can coexist over the
shared `kc:` core. Two models with non-colliding namespaces (e.g. `mtg:` and `peop:`)
can in principle be loaded into the same graph. However, composition is not the same
as useful integration — combining models requires explicit "connective tissue" in the
form of bridge types that relate elements across model boundaries.

This is analogous to software packages: importing two non-conflicting packages does
not automatically produce something useful. You often need to build the glue code
that connects them. The composability is real but not unlimited.

## The Bridge Model Pattern

Composing model A (`mtg:`) and model B (`peop:`) requires a model C that:

1. Imports both A and B (their OWL types are available via schema merge)
2. Defines **bridge types** — new edge and face types whose boundaries span
   elements from both models. For example:
   - `bridge:PersonColorAffinity` (edge): links a `peop:Person` vertex to an
     `mtg:Color` vertex, with attributes like `affinity_strength`
   - `bridge:PersonColorTriple` (face): a triangle involving one person and
     two colors, representing a person's relationship to a color pair

3. Provides **bridge queries** — SPARQL templates that reference both model
   namespaces (e.g., "which people have affinity for adjacent color pairs?")

The bridge model has its own namespace (`bridge:` or `mtg_peop:`) and its own
query directory. It is a first-class model family, not a special construct.

## Namespace Isolation Guarantees

The current architecture provides these guarantees:

- **Class names** are namespace-scoped: `mtg:Color` and `peop:Person` cannot
  collide because they have different IRI prefixes
- **Attribute properties** are namespace-scoped: `mtg:disposition` and
  `peop:disposition` are distinct OWL properties with distinct IRIs. They can
  coexist in the same graph without interference
- **SHACL shapes** target specific classes: `mtgs:ColorPairShape` targets
  `mtg:ColorPair` and ignores `peop:` individuals entirely. Shapes from
  different models do not interfere

These guarantees hold as long as each model uses its own namespace prefix. The
`kc:` namespace is reserved for core topological properties (`boundedBy`,
`hasElement`, `Element`, etc.) and must not be used for model-level terms.

## Design Concerns

### 1. SchemaBuilder Is Single-Namespace

Currently, one `SchemaBuilder` instance maps to one model namespace. To compose
models, you would need to:

- **Option A (merge outputs):** Create separate `SchemaBuilder` instances for
  each model, then merge their `dump_owl()` and `dump_shacl()` outputs into a
  combined graph before passing to `KnowledgeComplex`. This is modular and
  requires no API changes — just a merge utility.

- **Option B (composed wrapper):** Create a `ComposedSchema` class that wraps
  multiple `SchemaBuilder` instances and presents a unified interface. More
  ergonomic but adds API surface.

Option A is recommended for its simplicity. The merge utility is straightforward:
parse multiple Turtle strings into the same `rdflib.Graph`.

### 2. Type Registry Scope

`KnowledgeComplex` validates types against `schema._types`, which is a flat dict
from one `SchemaBuilder`. In a composed model, the type registry must span all
constituent models. With Option A (merge outputs), this means either:

- Merging the `_types` dicts from multiple builders
- Or having `KnowledgeComplex` accept multiple schemas

This needs design work. The Python-side type guard (`add_vertex` checks that
the type is registered) must see all registered types, not just one model's.

### 3. SPARQL Query Portability

Model-specific queries use model-specific prefixes (`PREFIX mtg:`, `PREFIX peop:`).
Cross-model queries need all relevant namespaces declared. These cross-model
queries are inherently composition-specific — they belong to the bridge model,
not to either constituent model.

The `query_dirs` parameter on `KnowledgeComplex` already supports multiple
directories, so bridge queries can be loaded alongside model queries.

### 4. Property Unification

If two models independently define properties with the same local name but
different namespaces (e.g., `mtg:disposition` and `peop:disposition`), they are
distinct and can coexist. But if a bridge model wants to declare them semantically
equivalent, it must use an explicit OWL axiom (`owl:equivalentProperty`). This
is a deliberate, auditable action — not an implicit merge.

### 5. Complex Membership

A composed `kc:Complex` can contain elements from multiple models. The
boundary-closure constraint (`ComplexShape`) applies uniformly: if a bridge edge
links a `mtg:Color` vertex and a `peop:Person` vertex, both must be `hasElement`
members of the complex before the edge is added. The slice rule works unchanged.

## Affected Components (When Implemented)

- `kc/schema.py` — merge utility or `ComposedSchema` wrapper
- `kc/graph.py` — multi-schema type registry support
- New `models/{bridge}/` directory for each composition
- New SPARQL queries spanning multiple model namespaces

## See Also

- `docs/ARCHITECTURE.md` — Abstraction Boundary, Vocabulary Tiers
- `docs/issues/skos-vocabularies.md` — vocabulary formalization (related: SKOS
  `skos:broader`/`skos:narrower` could formalize cross-model vocabulary extension)
