# Requirements

All tests trace to a requirement ID in this document. Requirements are organized by component.
The hypothesis test criteria (H1–H6, defined in PLAN.md and preserved in ROADMAP.md) are cross-referenced where applicable.

---

## REQ-CORE: Abstract Ontology and Shapes

### REQ-CORE-01
The package SHALL provide an abstract OWL ontology defining `KC:Element` as the base class
for all topological elements (k-simplices), with `KC:Vertex`, `KC:Edge`, and `KC:Face` as
subclasses. `KC:Complex` SHALL be defined as a collection of elements via `KC:hasElement`.
The `KC:boundedBy` property SHALL have `rdfs:domain` and `rdfs:range` of `KC:Element`.

### REQ-CORE-02
`KC:Edge` SHALL declare exactly 2 `KC:boundedBy` relations of type `KC:Vertex` via OWL
qualified cardinality restriction. The boundary is unordered (edges are unoriented).

### REQ-CORE-03
`KC:Face` SHALL declare exactly 3 `KC:boundedBy` relations of type `KC:Edge` via OWL
qualified cardinality restriction. The boundary is unordered (faces are unoriented).

### REQ-CORE-04
The abstract SHACL shapes SHALL enforce that `KC:Edge` instances have 2 distinct boundary
vertices (the two `boundedBy` values are different individuals). *[Design seam: OWL
open-world assumption prevents this being expressed as an OWL axiom.]*

### REQ-CORE-05
The abstract SHACL shapes SHALL enforce that the three boundary edges of a `KC:Face` instance
form a closed triangle over shared vertex endpoints. This constraint SHALL be implemented as a
`sh:sparql` constraint. *[Design seam: OWL cannot co-reference across three property values.]*
*[Cross-ref: H2]*

### REQ-CORE-06
The abstract ontology and shapes SHALL be loadable from static files shipped with the package
(`kc/resources/kc_core.ttl`, `kc/resources/kc_core_shapes.ttl`) without any runtime generation.

---

## REQ-SCHEMA: SchemaBuilder API

### REQ-SCHEMA-01
`SchemaBuilder` SHALL accept a `namespace` string parameter that determines the IRI prefix
for all user-defined classes and properties.

### REQ-SCHEMA-02
`SchemaBuilder.add_vertex_type(name)` SHALL declare a new OWL class that is a subclass of
`KC:Vertex` AND create a corresponding SHACL node shape targeting that class.
A single call SHALL produce changes in both OWL and SHACL internal representations.
*[Cross-ref: H3]*

### REQ-SCHEMA-03
`SchemaBuilder.add_edge_type(name, attributes)` SHALL declare a new OWL class that is a
subclass of `KC:Edge`, declare OWL data properties for each attribute, AND create a
corresponding SHACL property shape enforcing attribute presence and vocabulary constraints.
A single call SHALL produce changes in both OWL and SHACL internal representations.
*[Cross-ref: H3]*

### REQ-SCHEMA-04
`SchemaBuilder.add_face_type(name, attributes)` SHALL declare a new OWL class that is a
subclass of `KC:Face`, declare OWL data properties for each attribute, AND create a
corresponding SHACL property shape. Attributes flagged `required=False` SHALL generate
SHACL constraints with `sh:minCount 0`. *[Cross-ref: H3]*

### REQ-SCHEMA-05
`vocab(*values)` SHALL return a descriptor that generates both an OWL annotation on the
property (rdfs:comment listing valid values) and a SHACL `sh:in` constraint on the
corresponding shape.

### REQ-SCHEMA-06
`SchemaBuilder.dump_owl()` SHALL return a valid Turtle string representing the merged graph
of the abstract core OWL ontology and all user-defined type declarations.

### REQ-SCHEMA-07
`SchemaBuilder.dump_shacl()` SHALL return a valid Turtle string representing the merged graph
of the abstract core SHACL shapes and all user-defined shapes.

### REQ-SCHEMA-08
`SchemaBuilder.promote_to_attribute(type, attribute, vocab, required)` SHALL atomically update
both the OWL property definition and the SHACL shape for the named type. After calling this
method, `dump_owl()` and `dump_shacl()` SHALL both reflect the updated attribute.
*[Cross-ref: H3]*

### REQ-SCHEMA-09
`SchemaBuilder` SHALL NOT expose `rdflib`, `pyshacl`, or `owlrl` objects in its public API.
*[Cross-ref: H6]*

---

## REQ-GRAPH: KnowledgeComplex API

### REQ-GRAPH-01
`KnowledgeComplex(schema)` SHALL accept a `SchemaBuilder` instance and initialize an internal
RDF graph loaded with the merged OWL and SHACL from that schema.

### REQ-GRAPH-02
`KnowledgeComplex.add_vertex(id, type)` SHALL assert a new individual of the given type
(which must be a subclass of `KC:Vertex`) into the graph and SHALL run SHACL validation
against the node. It SHALL raise `ValidationError` with a human-readable report if validation
fails.

### REQ-GRAPH-03
`KnowledgeComplex.add_edge(id, type, vertices, **attributes)` SHALL assert a new edge
individual, link it to exactly 2 existing vertex individuals via `KC:boundedBy`,
assert all provided attributes, and SHALL run SHACL validation. It SHALL raise `ValidationError`
on failure. The `vertices` parameter is an unordered collection (edges are unoriented).

### REQ-GRAPH-04
`KnowledgeComplex.add_face(id, type, boundary, **attributes)` SHALL assert a new face individual,
link it to exactly 3 existing edge individuals via `KC:boundedBy`, assert all provided attributes,
and SHALL run SHACL validation including the closed-triangle `sh:sparql` constraint.
It SHALL raise `ValidationError` on failure. *[Cross-ref: H4]*

### REQ-GRAPH-05
`ValidationError` SHALL include the SHACL validation report text as a human-readable string
accessible as `error.report`.

### REQ-GRAPH-06
`KnowledgeComplex.query(template_name, **kwargs)` SHALL execute the named SPARQL template
with the provided keyword substitutions and return a `pandas.DataFrame`.

### REQ-GRAPH-07
`KnowledgeComplex.query()` SHALL raise `UnknownQueryError` if the template name is not
registered. It SHALL NOT accept arbitrary SPARQL strings.

### REQ-GRAPH-08
`KnowledgeComplex.dump_graph()` SHALL return a valid Turtle string of the full instance graph.

### REQ-GRAPH-09
`KnowledgeComplex` SHALL NOT expose `rdflib`, `pyshacl`, or `owlrl` objects in its public API.
*[Cross-ref: H6]*

---

## REQ-QUERY: Named SPARQL Templates

### REQ-QUERY-01
The package SHALL provide a `faces_by_edge_pattern` query template that returns, for each
face, the face ID and the multiset of `disposition` values of its three edges (enabling
`shard`/`wedge` classification). *[Cross-ref: H5]*

### REQ-QUERY-02
The package SHALL provide a `vertices` query template that returns all vertex individuals
and their types.

### REQ-QUERY-03
The package SHALL provide an `edges_by_disposition` query template that returns all edge
individuals grouped by `disposition` value.

### REQ-QUERY-04
All query templates SHALL be valid SPARQL 1.1 SELECT queries parameterizable via Python
string substitution with named `{placeholder}` tokens.

---

## REQ-DEMO: MTG Instance

### REQ-DEMO-01
The demo instance SHALL contain exactly 5 `Color` vertices: White, Blue, Black, Red, Green.

### REQ-DEMO-02
The demo instance SHALL contain exactly 5 `ColorPair` edges with `disposition = "adjacent"`,
corresponding to the pentagon adjacency: W-U, U-B, B-R, R-G, G-W.

### REQ-DEMO-03
The demo instance SHALL contain exactly 5 `ColorPair` edges with `disposition = "opposite"`,
corresponding to the pentagon diagonals: W-B, W-R, U-G, U-R, B-G.

### REQ-DEMO-04
The demo instance SHALL contain exactly 10 `ColorTriple` faces, one for each valid triangle
in the 10-edge graph. Each face SHALL pass SHACL structural validation.

### REQ-DEMO-05
No `ColorTriple` face in the initial demo instance SHALL have a `structure` attribute asserted.
The `shard`/`wedge` classification SHALL be discoverable only via query. *[Cross-ref: H5]*

### REQ-DEMO-06
After calling `promote_to_attribute("ColorTriple", "structure", vocab("shard","wedge"), required=True)`
and re-validating the demo instance, ALL 10 faces SHALL fail SHACL validation (missing required
attribute), demonstrating the schema/data tension. *[Cross-ref: H4, H3]*

---

## REQ-V&V: Verification and Validation

### REQ-VV-01 (maps to H1)
Tests SHALL cover all four cells of the 2×2 responsibility map: topological-OWL,
topological-SHACL, ontological-OWL, ontological-SHACL.

### REQ-VV-02 (maps to H2)
The `sh:sparql` closed-triangle constraint in `kc_core_shapes.ttl` SHALL be tested by
asserting a face whose three edges do NOT form a closed triangle and verifying that SHACL
validation fails with an appropriate report.

### REQ-VV-03 (maps to H3)
Tests SHALL verify that `add_edge_type` and `promote_to_attribute` each produce observable
changes in both `dump_owl()` and `dump_shacl()` output.

### REQ-VV-04 (maps to H4)
Tests SHALL cover at least: malformed face (wrong edge count), open-triangle face, edge with
invalid disposition value, face referencing non-existent edges.

### REQ-VV-05 (maps to H5)
Tests SHALL verify that `faces_by_edge_pattern` correctly classifies all 10 MTG triangles
into `shard` and `wedge` groups and that the ground-truth classification matches the expected
MTG color wheel topology.

### REQ-VV-06 (maps to H6)
Tests SHALL verify that no public method of `SchemaBuilder` or `KnowledgeComplex` returns
an object whose type is defined in `rdflib`, `pyshacl`, or `owlrl`.
