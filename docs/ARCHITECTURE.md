# Architecture: Knowledge Complex Semantic Web Toolchain

## The 2×2 Responsibility Map

This is the central architectural constraint. Every rule in the system belongs to exactly one cell.
The Python package exists to hide this table from the user.

|  | **OWL** | **SHACL** |
|---|---|---|
| **Topological** | `KC:Element` base class; `KC:Vertex`, `KC:Edge`, `KC:Face` as subclasses. `KC:Edge` has exactly 2 `boundedBy` (Vertex); `KC:Face` has exactly 3 `boundedBy` (Edge). `KC:Complex` as collection of elements via `KC:hasElement`. | Boundary vertices are distinct; boundary edges of a face form a closed triangle; boundary-closure of a complex (all instance-level; requires `sh:sparql`) |
| **Ontological** | Concrete subclasses and their allowed attributes (`ColorPair` with `disposition`; `ColorTriple` with `structure`); property domain/range declarations | Controlled vocabulary enforcement (e.g. `disposition ∈ {adjacent, opposite}`); attribute presence rules; co-occurrence constraints |

### Why Both OWL and SHACL at Each Layer

**Topological layer:** OWL cardinality axioms enforce structural counts at the class level (reasoning
over schema). SHACL is required for the closed-triangle constraint because OWL cannot express
a constraint that references the *co-values* of three different property assertions on the same
individual — this is a known expressivity boundary of OWL-DL. The `sh:sparql` constraint in
`kc_core_shapes.ttl` is the explicit test of this boundary.

**Ontological layer:** OWL defines what attributes a concrete type *has* (property declarations,
domain, range, subclass hierarchy). SHACL defines what values those attributes *must have*
at the instance level (vocabulary constraints, cardinality on the concrete shape, required/optional).
OWL cannot enforce controlled vocabulary on data properties at the instance level without
enumerating individuals, which is inappropriate for string-valued attributes.

---

## Component Layers

```
┌─────────────────────────────────────────────────────┐
│              Demo / Notebook  (demo/)                │
│  build_mtg_instance()  |  Marimo cells              │
│  Concrete elements: vertices, edges, faces          │
├─────────────────────────────────────────────────────┤
│          Model Family  (models/mtg/)                │
│  build_mtg_schema()    |  SPARQL templates          │
│  Color, ColorPair, ColorTriple definitions           │
├─────────────────────────────────────────────────────┤
│              kc Python Package  (kc/)               │
│  SchemaBuilder DSL     |  KnowledgeComplex I/O      │
│  (OWL + SHACL emit)   |  (rdflib graph + SPARQL)   │
├──────────────────────┬──────────────────────────────┤
│  kc_core.ttl         │  kc_core_shapes.ttl          │
│  (abstract OWL)      │  (abstract SHACL)            │
├──────────────────────┴──────────────────────────────┤
│         rdflib  |  pyshacl  |  owlrl                │
└─────────────────────────────────────────────────────┘
```

The **model family** layer (`models/mtg/`) sits between the core framework and the demo.
It defines domain-specific types and queries using the core's `SchemaBuilder` DSL — analogous
to defining a dataclass or ML model class. The demo layer then instantiates that model with
concrete data.

The static resources (`kc_core.ttl`, `kc_core_shapes.ttl`) are loaded once at package import.
Model schema and shapes are merged into the same rdflib `Graph` objects at runtime.

---

## Abstraction Boundary: Core vs. Model Families

The four implementation layers in the diagram above are separated by a key abstraction
boundary: the **core framework** (kc/) vs. **model families** (models/{name}/). Everything
below the boundary (core package, static resources, libraries) is framework-owned and
invariant. Everything above (model definitions, demo instances) is user-authored. The
Python package exists so users interact only with the model layer's Pythonic interface,
never with OWL/SHACL/SPARQL directly.

### Core Framework (`kc/`, prefixes `kc:` and `kcs:`)

- **Topological rule enforcement.** The Element/Vertex/Edge/Face hierarchy, cardinality
  axioms, distinctness, closed-triangle, and boundary-closure constraints. These are
  static OWL and SHACL shipped with the package (DD4). Users cannot modify them.
- **Ontological rule authoring.** `SchemaBuilder` provides the DSL for declaring types,
  attributes, and vocabularies. It *generates* OWL classes and SHACL shapes on behalf
  of the model but does not itself define any domain types.
- **Instance management.** `KnowledgeComplex` loads the merged schema, manages the RDF
  graph, validates on every write (DD3), and executes named SPARQL queries (DD2).
- **Framework queries.** Generic SPARQL templates (`vertices`, `coboundary`) that work
  for any model family.

### Model Families (`models/{name}/`, prefixes `{name}:` and `{name}s:`)

- **Ontological rule enforcement.** The concrete OWL types and SHACL shapes generated
  by calling `SchemaBuilder.add_*_type()`. These are the model's rules, authored via
  the core's tools.
- **Concrete complex authoring.** Instance data constructed via `KnowledgeComplex.add_*()`
  calls. Each element must comply with both core topological rules and model ontological
  rules.
- **Domain queries.** Model-specific SPARQL templates (e.g. `faces_by_edge_pattern`,
  `edges_by_disposition`).

### The Type Inheritance Chain Crosses the Boundary

```
kc:Element → kc:Vertex → mtg:Color → (instance "Green")
   core          core        model        demo/instance
```

The core owns `Element → Vertex`; the model owns `Vertex → Color`; the demo owns the
instance `Green`. The boundary is at the subclass declaration — `add_vertex_type("Color")`
is the model calling the core's authoring API to extend the core's type hierarchy.

### Layer Ownership of the 2×2 Map

|  | **OWL** | **SHACL** |
|---|---|---|
| **Topological** | Core owns (static `kc_core.ttl`) | Core owns (static `kc_core_shapes.ttl`) |
| **Ontological** | Model authors via `SchemaBuilder` → core generates | Model authors via `vocab()`/attributes → core generates |

Both ontological cells are *authored* by the model but *generated and managed* by the core.
The model never touches OWL or SHACL directly.

### Vocabulary Tiers

The system has three tiers of controlled terms. Each tier extends but never replaces the
tier above it.

| Tier | Scope | Examples | Owner | Mechanism |
|---|---|---|---|---|
| 1. Structural | Core topological classes and properties | `kc:Element`, `kc:Vertex`, `kc:boundedBy`, `kc:hasElement` | Core (static OWL) | Fixed in `kc_core.ttl`; never modified |
| 2. Type | Domain-specific classes extending core types | `mtg:Color`, `mtg:ColorPair`, `mtg:ColorTriple` | Model (authored via SchemaBuilder) | `add_*_type()` generates OWL subclasses |
| 3. Value (vocab) | Controlled attribute values within a type | `"adjacent"`, `"opposite"`, `"shard"`, `"wedge"`, `"azorius"`, `"design"` | Model (authored via `vocab()`) | `vocab()` generates SHACL `sh:in` |
| 3. Value (text) | Free-text string attributes | `"persona"`, `"at_best"`, `"example_behaviors"` | Model (authored via `text()`) | `text()` generates SHACL `sh:datatype xsd:string` |

A model family adds type terms (tier 2) that subclass structural terms (tier 1), and adds
value terms (tier 3) that constrain attributes on those types. The core owns tier 1 and
provides the authoring tools for tiers 2 and 3.

SKOS (`skos:ConceptScheme`, `skos:Concept`) is the natural W3C formalization for making
these vocabulary tiers machine-readable in RDF. See `docs/issues/skos-vocabularies.md`.

### Python-Side Guards (Design Seam)

Some constraints cannot be expressed in SHACL and are enforced by the Python API instead:

- **Type registration check.** `add_vertex()`, `add_edge()`, and `add_face()` verify that
  the `type` argument is registered in the schema's type registry *before* asserting RDF
  triples. SHACL shapes target specific classes and pass silently on unknown types, so
  this guard is a Python-side pre-validation step.

- **Multiple shapes on a single violation.** When SHACL validation fails, multiple shapes
  may report violations for the same structural issue. For example, adding an edge before
  its boundary vertices are in the complex triggers both EdgeShape (boundary must be
  `kc:Vertex` individuals) and ComplexShape (boundary elements must be complex members).
  The `ValidationError.report` includes all violations — this is intentional.

---

## Key Design Decisions

### DD1: Attributes over Subclasses for the MTG Demo

The MTG demo uses a single concrete edge type (`ColorPair`) with a controlled-vocabulary
attribute (`disposition`) rather than two subclasses (`AllyEdge`, `EnemyEdge`). Similarly,
`ColorTriple` uses an attribute (`structure`) rather than two face subclasses.

**Rationale:** The model is simple enough that attributes suffice. The framework still supports
multiple concrete subclasses with different attribute schemas — the demo simply does not require
that power. Keeping the demo flat makes the discovery step more legible: the `shard`/`wedge` split
is visible in the data *before* it is promoted to a schema-level concern.

**Implication:** The `Person` horizon example (WP5 step 6) motivates the subclass path — a
`Person` vertex type needs `PersonColorAffinity` edges that carry different attributes than
`ColorPair` edges, requiring a new concrete subclass.

### DD2: SPARQL Templates, Not Free Queries

All SPARQL is encapsulated as named template files in `kc/queries/`. The `KnowledgeComplex.query()`
method accepts only registered template names.

**Rationale:** This maintains API opacity (H6), prevents arbitrary SPARQL from bypassing
validation invariants, and makes the query surface explicit and testable. The templates are
inspectable for transparency but not user-writable in normal usage.

**Known limitation:** This restricts ad-hoc exploration. In a production package, a separate
`expert_query(sparql_string)` escape hatch would be appropriate. Out of scope for this demonstrator.

### DD3: Validation on Write

`KnowledgeComplex.add_face()` triggers SHACL validation immediately and raises `ValidationError`
on failure. `add_vertex()` and `add_edge()` do the same against their respective shapes.

**Rationale:** Fail fast; keep the graph in a valid state at all times. This matches the V&V
framing: verification is not a batch post-processing step, it is enforced at assertion time.

**Implication:** `promote_to_attribute(..., required=True)` followed by re-validation against
an already-loaded graph will produce failures. This is intentional — it is the demonstration
that the schema and the data are in tension, motivating the annotation step.

### DD4: Static Core Resources

`kc_core.ttl` and `kc_core_shapes.ttl` are static files shipped with the package, not generated
at runtime. The user cannot modify them through the Python API.

**Rationale:** The topological rules are framework invariants, not user-configurable. Separating
them from user schema also makes the 2×2 boundary visible in the file system.

### DD5: `dump_owl()` and `dump_shacl()` Merge Core and User Schema

Both dump methods return the full merged graph (core + user-defined), serialized as Turtle.
They do not return just the user-defined fragment.

**Rationale:** The merged graph is what `pyshacl` and `owlrl` operate on. Showing the full
graph makes the system inspectable and demonstrates that user types genuinely extend (not
replace) the core ontology.

### DD6: Shared-Domain Removal (`_set_owl_domain`)

When the same property name (e.g., `persona`) appears on multiple types (Color, ColorPair,
ColorTriple), the OWL `rdfs:domain` assertion must be handled carefully. Naively adding
`rdfs:domain` for each type causes RDFS inference to classify any individual with that
property as a member of *all* types — a vertex with `persona` would be inferred to be a
face, violating the type hierarchy.

**Resolution:** `SchemaBuilder._set_owl_domain()` tracks property-to-type mappings in
`_attr_domains`. When a property first appears, its domain is set to the declaring type.
When the same property appears on a second type, the `rdfs:domain` triple is *removed*
from the OWL graph, leaving the property without a domain restriction. SHACL property shapes
still enforce per-type constraints correctly (each type's NodeShape has its own property shape).

**Rationale:** This is a 2×2 architecture validation — OWL domain semantics (inference-based,
open-world) conflict with SHACL constraint semantics (validation-based, closed-world).
The shared-domain fix demonstrates that both layers must be managed together, even when they
express similar-looking rules.

### DD7: Two Attribute Descriptor Types — `vocab()` vs. `text()`

The ontological layer supports two kinds of attributes:

- **`vocab(*values)`** — controlled vocabulary. Generates an OWL `DatatypeProperty` with
  `rdfs:comment` listing allowed values, and a SHACL `sh:in` constraint. Values are
  validated at write time. Example: `disposition ∈ {"adjacent", "opposite"}`.

- **`text(required=True, multiple=False)`** — free-text string. Generates an OWL
  `DatatypeProperty` with `rdfs:range xsd:string`, and a SHACL property shape with
  `sh:datatype xsd:string` (no `sh:in`). Used for essay-derived prose attributes.
  Example: `persona`, `at_best`, `at_worst`.

Both descriptors support `required` and `multiple` flags. When `multiple=True`, the SHACL
shape has no `sh:maxCount`, and the Python API accepts list values (each item becomes a
separate triple).

The dict-style spec `{"vocab": vocab(...), "required": False}` or
`{"text": text(), "required": True}` is the legacy syntax; bare descriptors are preferred.

---

## Known OWL Expressivity Limits (Design Seams)

| Constraint | OWL can express? | Resolution |
|---|---|---|
| Edge has exactly 2 boundary vertices | Yes (cardinality on `boundedBy`) | OWL cardinality axiom |
| Face has exactly 3 boundary edges | Yes (cardinality on `boundedBy`) | OWL cardinality axiom |
| Boundary vertices are distinct individuals | No (OWL open-world; same-as/different-from is individual-level) | SHACL `sh:sparql` (COUNT DISTINCT) |
| Boundary edges of a face form a closed triangle | No (requires co-reference across 3 property values) | SHACL `sh:sparql` constraint |
| Boundary-closure of a complex | No (requires co-reference across `hasElement` and `boundedBy` on different individuals) | SHACL `sh:sparql` constraint |
| Controlled vocabulary on data property | No (without `owl:oneOf` on individuals, impractical for strings) | SHACL `sh:in` |

These seams are documented as comments in the relevant `.ttl` files.

---

## Known Simplifications

### Element Base Class and Complex

All topological objects are subclasses of `kc:Element` (the abstract k-simplex). The simplex
order k determines boundary cardinality: k=0 (Vertex) has empty boundary; k>=1 has (k+1)
boundary (k-1)-simplices. Higher-order simplices (k>=3) can be defined by subclassing Element
and adding a `boundedBy` cardinality restriction.

A `kc:Complex` is a collection of elements (`kc:hasElement`) with a SHACL boundary-closure
constraint: if a simplex is in the complex, all its boundary elements must also be in the complex.

The Python `KnowledgeComplex` class maps to a `kc:Complex` individual in the RDF graph.
Each `add_vertex` / `add_edge` / `add_face` call asserts both the element and its
`kc:hasElement` membership. Boundary-closure validation (via `ComplexShape`) is enforced on
every write via the **slice rule**: at every point during construction, the elements added
so far must form a valid complex. This is a partial ordering — an element's boundary elements
must precede it, but types can be interleaved (e.g., vertex, vertex, edge, vertex, edge, ...).
The demo uses the simpler strategy of adding all vertices, then all edges, then all faces.

For temporal complex interpretation (where insertion order carries meaning), see
`docs/issues/temporal-ordering.md`.

### Orientation

All simplices in this demo are **unoriented**. The boundary operator (`kc:boundedBy`) returns
an unordered set, not an ordered list. This means:

- **Edges** are undirected — `boundedBy` links to 2 vertices with no source/target distinction
- **Faces** are unoriented triangles — the boundary edge cycle has no winding direction
- **Coboundary** is computed via SPARQL inverse lookup, not stored triples

This is sufficient for the MTG color wheel where all relationships are symmetric.

For oriented simplex support (directed edges, oriented faces), see `docs/issues/orientation-support.md`.

---

## Namespace Conventions

```turtle
@prefix kc:   <https://example.org/kc#> .       # core framework
@prefix kcs:  <https://example.org/kc/shape#> . # core shapes
@prefix mtg:  <https://example.org/mtg#> .      # user namespace (demo)
@prefix mtgs: <https://example.org/mtg/shape#> .# user shapes (demo)
```

User namespaces are set via `SchemaBuilder(namespace="mtg")`. The URI base is currently
`https://example.org/` as a placeholder; a real deployment would use a dereferenceable IRI.

---

## File Inventory

| File | Layer | Authored by |
|---|---|---|
| `kc/resources/kc_core.ttl` | Abstract OWL | Hand-authored (WP1) |
| `kc/resources/kc_core_shapes.ttl` | Abstract SHACL | Hand-authored (WP2) |
| `kc/schema.py` | Python API — schema | Implemented (WP3) |
| `kc/graph.py` | Python API — instances | Implemented (WP3) |
| `kc/queries/*.sparql` | Framework SPARQL templates | Implemented (WP3) |
| `models/mtg/schema.py` | MTG model schema | Implemented (WP3) |
| `models/mtg/queries/*.sparql` | MTG SPARQL templates | Implemented (WP3) |
| `demo/demo_instance.py` | MTG instance | Implemented (WP4) |
| `demo/demo.py` | Marimo notebook | Implemented (WP5) |
