# Knowledge Complex — Semantic Web Toolchain Proof of Concept

## Hypothesis

The semantic web toolchain (OWL + SHACL + SPARQL via `rdflib`/`pyshacl`) is sufficient to implement the three-layer knowledge complex framework. A Python package abstraction can hide the internal 2×2 complexity — {topological, ontological} × {OWL, SHACL} — behind a DSL that feels like dataclass-style modeling.

## What This Is

A demonstrator, not production code. End-to-end, fully working, but scoped to validate the toolchain hypothesis. The concrete instance is a knowledge complex over the five Magic: The Gathering colors, used because it is simple enough to understand immediately but non-trivial enough to exercise all framework layers.

## Repository Layout

```
kc/
  resources/
    kc_core.ttl            # abstract OWL ontology (topological backbone)
    kc_core_shapes.ttl     # abstract SHACL shapes (topological constraints)
  queries/
    *.sparql               # named query templates (not user-facing)
  schema.py                # SchemaBuilder — type and rule authoring API
  graph.py                 # KnowledgeComplex — instance I/O API
  exceptions.py            # ValidationError and friends
  __init__.py

tests/
  requirements.md          # explicit requirements driving all tests
  test_core_owl.py
  test_core_shacl.py
  test_schema_builder.py
  test_knowledge_complex.py

docs/
  PLAN.md                  # project plan with work packages and gates
  ARCHITECTURE.md          # 2x2 responsibility map and design decisions
  REQUIREMENTS.md          # full requirements document

demo/
  demo_instance.py         # MTG color pentagon instantiation script
  demo.py                  # marimo notebook

pyproject.toml
```

## Dependencies

```toml
rdflib = ">=7.0"
pyshacl = ">=0.25"
owlrl = ">=6.0"
marimo = ">=0.6"
networkx = ">=3.0"
matplotlib = ">=3.8"
pandas = ">=2.0"
```

## Usage Sketch

```python
from kc.schema import SchemaBuilder, vocab

sb = SchemaBuilder(namespace="mtg")
sb.add_vertex_type("Color")
sb.add_edge_type("Relationship", attributes={"disposition": vocab("adjacent", "opposite")})
sb.add_face_type("ColorTriple", attributes={"pattern": vocab("ooa", "oaa"), "required": False})

from kc.graph import KnowledgeComplex

kc = KnowledgeComplex(schema=sb)
kc.add_vertex("White", type="Color")
kc.add_vertex("Blue",  type="Color")
kc.add_edge("WU", type="Relationship", source="White", target="Blue", disposition="adjacent")
# ... add remaining vertices, edges, faces
# add_face triggers SHACL validation on write

results = kc.query("faces_by_edge_pattern")
```

## Running Tests

```bash
pytest tests/ -v
```

## Notebook

```bash
marimo run demo/demo.py
```

## See Also

- `docs/PLAN.md` — work packages, sequence, review gates
- `docs/ARCHITECTURE.md` — the 2×2 responsibility map, design decisions, known OWL limits
- `docs/REQUIREMENTS.md` — numbered requirements; all tests trace back to these
