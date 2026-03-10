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

**`kc/graph.py` — KnowledgeComplex (maps to kc:Complex):**

- `_init_graph()` — initialize instance graph with schema; create kc:Complex individual
- `_validate()` — run pyshacl validation (element shapes + ComplexShape boundary-closure)
- `add_vertex(id, type)` — assert vertex + hasElement, validate
- `add_edge(id, type, vertices, **attributes)` — assert edge + boundedBy + hasElement, validate
- `add_face(id, type, boundary, **attributes)` — assert face + boundedBy + hasElement, validate (closed-triangle + boundary-closure)
- `query(template_name, **kwargs)` — execute named SPARQL template, return DataFrame
- `dump_graph()` — serialize instance graph as Turtle

Tests are already written (TDD): `tests/test_schema_builder.py`, `tests/test_knowledge_complex.py`.

## Quality Criteria (human review)

- [ ] Does the `SchemaBuilder` API surface feel right? (`add_vertex_type`, `add_edge_type`, `add_face_type`, `promote_to_attribute`)
- [ ] Does the `KnowledgeComplex` API surface feel right? (`add_vertex`, `add_edge`, `add_face`, `query`, `dump_graph`)
- [ ] Is validation-on-write the behavior you want, or should validation be explicit/deferred?
- [ ] Are the error messages in `ValidationError` reports useful and readable to a human?
- [ ] Does `promote_to_attribute` capture the workflow you envision for evolving a schema?
- [ ] Is the named-template-only query restriction (no ad-hoc SPARQL) the right call for this project?

## Verification (machine — Claude runs these)

```bash
pytest tests/test_schema_builder.py tests/test_knowledge_complex.py -v
```

Expected: all tests pass.

Requirements covered by tests: REQ-SCHEMA-01 through REQ-SCHEMA-09, REQ-GRAPH-01 through REQ-GRAPH-09, REQ-QUERY-01 through REQ-QUERY-04, H3, H4, H6.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
