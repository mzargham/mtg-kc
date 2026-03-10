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

## Quality Criteria

- [ ] All files are in the locations described in README.md
- [ ] `pytest tests/test_core_owl.py tests/test_core_shacl.py -v` passes (the two currently-passing test suites)
- [ ] `python -c "from kc import SchemaBuilder, KnowledgeComplex"` imports without error
- [ ] No stale files left at the root (only README.md, pyproject.toml, .gitignore, and directories)

## Verification

```bash
# Structure check
ls kc/ kc/resources/ kc/queries/ tests/ demo/ docs/

# Import check
python -c "from kc import SchemaBuilder, KnowledgeComplex, ValidationError"

# Test check
pytest tests/test_core_owl.py tests/test_core_shacl.py -v
```

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
