# Project Plan: Knowledge Complex via Semantic Web Toolchain

## Hypothesis

The semantic web toolchain (OWL + SHACL + SPARQL via `rdflib`/`pyshacl`) is sufficient to implement the three-layer knowledge complex framework. The Python package abstraction is itself a hypothesis: that the 2×2 complexity {topological, ontological} × {OWL, SHACL} can be hidden behind a DSL that feels like dataclass-style modeling.

---

## Scope Constraints

- End-to-end demonstrator only; not production code
- One fixed demo model: MTG color pentagon
- OWL and SHACL are internal representations; never user-facing
- SPARQL encapsulated as named templates; not user-facing
- Face pattern discovery (`ooa`/`oaa`) is demonstrated via query, not pre-asserted
- Promoting a discovered pattern to a first-class attribute is the closing demonstration

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

## Concrete Data Model (MTG Demo)

**Vertex type:** `Color` (subclass of `KC:Vertex`)
- No additional attributes at this stage

**Edge type:** `Relationship` (subclass of `KC:Edge`)
- Attribute: `kc:disposition` ∈ `{"adjacent", "opposite"}`
- 5 adjacent edges (pentagon neighbors), 5 opposite edges (pentagon diagonals)
- Pentagon adjacency: W-U, U-B, B-R, R-G, G-W
- Pentagon opposites: W-B, W-R, U-G, U-R, B-G

**Face type:** `ColorTriple` (subclass of `KC:Face`)
- Attribute: `kc:pattern` ∈ `{"ooa", "oaa"}` — **not pre-asserted in demo instance**
- 10 valid triangles exist in the 10-edge complete graph
- Pattern is discovered via SPARQL; promotion to explicit attribute is the closing exercise

---

## Work Packages

### WP1 — Abstract OWL Core (`kc/resources/kc_core.ttl`)

Raw Turtle, hand-authored, static resource loaded by the package.

- Base class: `KC:Element` — abstract k-simplex; all topological types subclass this
- Simplex classes: `KC:Vertex` (k=0), `KC:Edge` (k=1), `KC:Face` (k=2) — subclasses of `KC:Element`
- Collection: `KC:Complex` with `KC:hasElement` membership property
- Object property: `KC:boundedBy` — dimension-polymorphic boundary operator (`domain: Element`, `range: Element`)
- OWL cardinality axioms:
  - `KC:Edge` `owl:qualifiedCardinality 2` on `boundedBy` (exactly 2 boundary vertices)
  - `KC:Face` `owl:qualifiedCardinality 3` on `boundedBy` (exactly 3 boundary edges)
  - Vertex has empty boundary (k=0); higher-order simplices (k>=3) extensible via subclass + restriction
- Code comment explicitly documents what OWL cannot enforce (closed-triangle rule, boundary-closure) and why — these are the design seams

Deliverable: `kc/resources/kc_core.ttl`

### WP2 — Abstract SHACL Core (`kc/resources/kc_core_shapes.ttl`)

Raw Turtle, hand-authored, static resource.

- `KC:EdgeShape`: `boundedBy` count = 2, each is `KC:Vertex`; boundary vertices are distinct (via `sh:sparql` COUNT DISTINCT)
- `KC:FaceShape`: `boundedBy` count = 3, each is `KC:Edge`; closed-triangle constraint via `sh:sparql`
  - The SPARQL constraint is the explicit test of the topological expressivity hypothesis
  - The constraint checks that the three edges share vertices forming a cycle
- `KC:ComplexShape`: boundary-closure constraint via `sh:sparql` — if a simplex is in the complex, all its boundary elements must also be in the complex

Deliverable: `kc/resources/kc_core_shapes.ttl`

### WP3 — Python Package (`kc/`)

Two coherent sub-APIs. Internal structure mirrors the 2×2 but is not exposed.

#### `kc.schema.SchemaBuilder`

```python
sb = SchemaBuilder(namespace="mtg")

sb.add_vertex_type("Color")

sb.add_edge_type(
    "Relationship",
    attributes={"disposition": vocab("adjacent", "opposite")}
)

sb.add_face_type(
    "ColorTriple",
    attributes={"pattern": vocab("ooa", "oaa"), "required": False}
)

sb.dump_owl()    # → Turtle string (kc_core + user schema, merged)
sb.dump_shacl()  # → Turtle string (kc_core_shapes + user shapes, merged)
```

**Invariant:** `add_vertex_type`, `add_edge_type`, `add_face_type` each write to both OWL
(subclass declaration, attribute property) and SHACL (shape with vocab/presence constraints).
One call, two internal locations. The package enforces this invariant.

#### `kc.graph.KnowledgeComplex`

```python
kc = KnowledgeComplex(schema=sb)

kc.add_vertex("White", type="Color")
kc.add_edge("WU", type="Relationship", vertices={"White", "Blue"},
            disposition="adjacent")
kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"])
# ↑ triggers SHACL validation on write; raises ValidationError with report on failure

df = kc.query("faces_by_edge_pattern")   # named template, returns DataFrame
kc.dump_graph()                           # → Turtle string
```

SPARQL lives as named `.sparql` template files in `kc/queries/`. Inspectable but not
user-editable. `query()` accepts only registered template names plus keyword arguments
for substitution.

#### `kc.schema.SchemaBuilder.promote_to_attribute` — closing demonstration

```python
sb.promote_to_attribute(
    type="ColorTriple",
    attribute="pattern",
    vocab=vocab("ooa", "oaa"),
    required=True    # upgrade: was optional, now required
)
```

Internally updates OWL property definition and SHACL shape constraint atomically.
After this call, re-validating the graph fails on faces lacking `pattern` — motivating
the annotation step and the next work item.

Deliverable: `kc/schema.py`, `kc/graph.py`, `kc/exceptions.py`, `kc/__init__.py`

### WP4 — MTG Demo Instance (`demo/demo_instance.py`)

- 5 `Color` vertices: White, Blue, Black, Red, Green
- 10 `Relationship` edges with correct `disposition` values
- 10 valid `ColorTriple` faces — no `pattern` attribute asserted
- All faces must pass SHACL structural validation before notebook proceeds

Deliverable: `demo/demo_instance.py`

### WP5 — Marimo Notebook (`demo/demo.py`)

Narrative structure:

1. **Schema authoring** — build `SchemaBuilder`; show `dump_owl()` / `dump_shacl()` cells
2. **Instance loading** — load MTG instance; graph visualization colored by `disposition`
3. **Verification** — run SHACL; all faces pass; show one deliberately broken face and its report
4. **Discovery** — run `faces_by_edge_pattern` query; show `ooa`/`oaa` split in table; observe the distinction is meaningful and not yet captured in the model
5. **Promotion** — call `promote_to_attribute`; show updated `dump_shacl()`; re-validate; show failures; motivate completing the annotation
6. **Horizon** — stub a `Person` vertex type; observe it motivates `PersonColorAffinity` edge type and new face types; leave as exercise

Deliverable: `demo/demo.py`

---

## Work Sequence and Review Gates

```
WP1 (kc_core.ttl)
  → [REVIEW] → WP2 (kc_core_shapes.ttl)
                 → [REVIEW] → WP3 (Python package)
                                → [REVIEW] → WP4 (demo instance)
                                               → [REVIEW] → WP5 (notebook)
                                                              → [REVIEW]
```

WP1 and WP2 are drafted as raw Turtle first. The package wraps them; it does not replace them.
All tests are written before implementation (TDD). Requirements in `docs/REQUIREMENTS.md`;
tests trace to requirement IDs.

---

## Hypothesis Test Criteria

| ID | Criterion | Pass condition |
|---|---|---|
| H1 | 2×2 coverage | All four cells of the responsibility map have at least one concrete rule |
| H2 | Topological limit documented | Closed-triangle constraint is in SHACL `sh:sparql`; comment explains why OWL cannot express it |
| H3 | Single-call invariant | `add_edge_type` and `promote_to_attribute` each produce changes in both OWL and SHACL dumps |
| H4 | Verification works | SHACL catches a malformed face and produces a readable report |
| H5 | Discovery works | SPARQL reveals `ooa`/`oaa` split without it being pre-asserted |
| H6 | API opacity | The notebook never imports `rdflib`, `pyshacl`, or `owlrl` directly |
