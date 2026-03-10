# WP0 — Repository Organization

## Status: Not Started

## Scope

Reorganize the flat file layout into the package structure described in README.md:

| Current location | Target location |
|---|---|
| `schema.py`, `graph.py`, `exceptions.py`, `__init__.py` | `kc/` |
| `kc_core.ttl`, `kc_core_shapes.ttl` | `kc/resources/` |
| `*.sparql` | `kc/queries/` |
| `test_*.py` | `tests/` |
| `demo.py`, `demo_instance.py` | `demo/` |
| `PLAN.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md` | `docs/` |

Also:

- Update `pyproject.toml` (testpaths, package config)
- Fix all imports in test files and demo files to use `kc.*` package paths
- Ensure `kc/resources/` and `kc/queries/` are included as package data

## Quality Criteria (human review)

- [ ] Does the directory layout match your mental model of the project?
- [ ] Are there files that should live elsewhere (e.g., should `references/` be under `docs/`)?
- [ ] Is the package name `kc` still the right name for imports?
- [ ] Does the root directory feel clean — only config files and top-level directories?

## Verification (machine — Claude runs these)

```bash
# Structure check
ls kc/ kc/resources/ kc/queries/ tests/ demo/ docs/

# Import check
python -c "from kc import SchemaBuilder, KnowledgeComplex, ValidationError"

# Test check (currently-passing suites still pass)
pytest tests/test_core_owl.py tests/test_core_shacl.py -v

# No stale .py/.ttl/.sparql files at root
ls *.py *.ttl *.sparql 2>&1 | grep -c "No such file"
```

Requirements verified by tests: all currently-passing tests remain green after reorg.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
