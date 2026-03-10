# Architecture: Knowledge Complex Semantic Web Toolchain

## The 2×2 Responsibility Map

This is the central architectural constraint. Every rule in the system belongs to exactly one cell.
The Python package exists to hide this table from the user.

|  | **OWL** | **SHACL** |
|---|---|---|
| **Topological** | `KC:Edge` has exactly 1 `hasSource` and 1 `hasTarget`; `KC:Face` has exactly 3 `hasEdge` (class + cardinality axioms on abstract classes) | Endpoints are distinct vertices; edges of a face form a closed triangle (instance-level; requires `sh:sparql`) |
| **Ontological** | Concrete subclasses and their allowed attributes (`Relationship` with `disposition`; `ColorTriple` with `pattern`); property domain/range declarations | Controlled vocabulary enforcement (`disposition ∈ {adjacent, opposite}`); attribute presence rules; co-occurrence constraints |

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
│                  User / Notebook                    │
│  SchemaBuilder DSL   |   KnowledgeComplex I/O       │
├─────────────────────────────────────────────────────┤
│              kc Python Package                      │
│  schema.py           |   graph.py                  │
│  (OWL + SHACL emit)  |   (rdflib graph + SPARQL)   │
├──────────────────────┬──────────────────────────────┤
│  kc_core.ttl         │  kc_core_shapes.ttl          │
│  (abstract OWL)      │  (abstract SHACL)            │
├──────────────────────┴──────────────────────────────┤
│         rdflib  |  pyshacl  |  owlrl                │
└─────────────────────────────────────────────────────┘
```

The static resources (`kc_core.ttl`, `kc_core_shapes.ttl`) are loaded once at package import.
User schema and shapes are merged into the same rdflib `Graph` objects at runtime.

---

## Key Design Decisions

### DD1: Attributes over Subclasses for the MTG Demo

The MTG demo uses a single concrete edge type (`Relationship`) with a controlled-vocabulary
attribute (`disposition`) rather than two subclasses (`AllyEdge`, `EnemyEdge`). Similarly,
`ColorTriple` uses an attribute (`pattern`) rather than two face subclasses.

**Rationale:** The model is simple enough that attributes suffice. The framework still supports
multiple concrete subclasses with different attribute schemas — the demo simply does not require
that power. Keeping the demo flat makes the discovery step more legible: the `ooa`/`oaa` split
is visible in the data *before* it is promoted to a schema-level concern.

**Implication:** The `Person` horizon example (WP5 step 6) motivates the subclass path — a
`Person` vertex type needs `PersonColorAffinity` edges that carry different attributes than
`Relationship` edges, requiring a new concrete subclass.

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

---

## Known OWL Expressivity Limits (Design Seams)

| Constraint | OWL can express? | Resolution |
|---|---|---|
| Edge has exactly 2 endpoints | Yes (cardinality on `hasSource`, `hasTarget`) | OWL cardinality axiom |
| Face has exactly 3 edges | Yes (cardinality on `hasEdge`) | OWL cardinality axiom |
| Endpoints are distinct individuals | No (OWL open-world; same-as/different-from is individual-level) | SHACL `sh:not sh:equals` |
| Edges of a face form a closed triangle | No (requires co-reference across 3 property values) | SHACL `sh:sparql` constraint |
| Controlled vocabulary on data property | No (without `owl:oneOf` on individuals, impractical for strings) | SHACL `sh:in` |

These seams are documented as comments in the relevant `.ttl` files.

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
| `kc/queries/*.sparql` | SPARQL templates | Implemented (WP3) |
| `demo/demo_instance.py` | MTG instance | Implemented (WP4) |
| `demo/demo.py` | Marimo notebook | Implemented (WP5) |
