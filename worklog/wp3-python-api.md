# WP3 — Python Package API

## Status: Not Started

## Scope

Implement all `NotImplementedError` stubs in the two core modules:

**`kc/schema.py` — SchemaBuilder:**

- `_init_graphs()` — initialize internal OWL and SHACL graphs from core resources
- `add_vertex_type(name)` — write subclass + shape to both OWL and SHACL
- `add_edge_type(name, attributes)` — write subclass + shape + vocab constraints
- `add_face_type(name, attributes)` — write subclass + shape + optional attribute handling
- `promote_to_attribute(type, attribute, vocab, required)` — atomic OWL + SHACL update
- `dump_owl()` — serialize merged OWL graph as Turtle
- `dump_shacl()` — serialize merged SHACL graph as Turtle

**`kc/graph.py` — KnowledgeComplex:**

- `_init_graph()` — initialize instance graph with schema
- `_validate()` — run pyshacl validation, raise `ValidationError` on failure
- `add_vertex(id, type)` — assert vertex, validate
- `add_edge(id, type, source, target, **attributes)` — assert edge, validate
- `add_face(id, type, edges, **attributes)` — assert face, validate (including closed-triangle)
- `query(template_name, **kwargs)` — execute named SPARQL template, return DataFrame
- `dump_graph()` — serialize instance graph as Turtle

Tests are already written (TDD): `tests/test_schema_builder.py`, `tests/test_knowledge_complex.py`.

## Quality Criteria

- [ ] REQ-SCHEMA-01: SchemaBuilder accepts namespace parameter
- [ ] REQ-SCHEMA-02: `add_vertex_type` writes to both OWL and SHACL (H3)
- [ ] REQ-SCHEMA-03: `add_edge_type` writes to both OWL and SHACL (H3)
- [ ] REQ-SCHEMA-04: `add_face_type` with `required=False` generates `sh:minCount 0`
- [ ] REQ-SCHEMA-05: `vocab()` generates OWL annotation + SHACL `sh:in`
- [ ] REQ-SCHEMA-06: `dump_owl()` returns valid merged Turtle
- [ ] REQ-SCHEMA-07: `dump_shacl()` returns valid merged Turtle
- [ ] REQ-SCHEMA-08: `promote_to_attribute` atomically updates both OWL and SHACL (H3)
- [ ] REQ-SCHEMA-09: No rdflib/pyshacl/owlrl in public API (H6)
- [ ] REQ-GRAPH-01: KnowledgeComplex initializes with merged schema
- [ ] REQ-GRAPH-02: `add_vertex` validates on write
- [ ] REQ-GRAPH-03: `add_edge` links vertices and validates
- [ ] REQ-GRAPH-04: `add_face` validates including closed-triangle (H4)
- [ ] REQ-GRAPH-05: `ValidationError` includes SHACL report text
- [ ] REQ-GRAPH-06: `query()` returns DataFrame
- [ ] REQ-GRAPH-07: `query()` rejects unknown templates
- [ ] REQ-GRAPH-08: `dump_graph()` returns valid Turtle
- [ ] REQ-GRAPH-09: No rdflib/pyshacl/owlrl in public API (H6)
- [ ] REQ-QUERY-01 through REQ-QUERY-04: Named SPARQL templates work correctly

## Verification

```bash
pytest tests/test_schema_builder.py tests/test_knowledge_complex.py -v
```

Expected: all tests pass.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
