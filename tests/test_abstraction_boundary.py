"""
tests/test_abstraction_boundary.py

Tests enforcing the abstraction boundary between core framework and model/demo layers.
Source-inspection tests — verify import hygiene and API surface.
All tests should pass today.

Traceability: see tests/requirements.md, ARCHITECTURE.md §Abstraction Boundary
"""

import re
from pathlib import Path

_ROOT = Path(__file__).parent.parent


def _read_source(relative_path: str) -> str:
    """Read a source file as text."""
    return (_ROOT / relative_path).read_text()


def _has_import(source: str, module: str) -> bool:
    """Check if source contains an actual import of module (not just in comments)."""
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if re.search(rf'\bimport\s+{module}\b', stripped):
            return True
        if re.search(rf'\bfrom\s+{module}\b', stripped):
            return True
    return False


# ---------------------------------------------------------------------------
# Model layer import hygiene
# ---------------------------------------------------------------------------

def test_model_schema_does_not_import_rdflib():
    """models/mtg/schema.py must not import rdflib directly."""
    src = _read_source("models/mtg/schema.py")
    assert not _has_import(src, "rdflib")


def test_model_schema_does_not_import_pyshacl():
    """models/mtg/schema.py must not import pyshacl directly."""
    src = _read_source("models/mtg/schema.py")
    assert not _has_import(src, "pyshacl")


def test_model_schema_does_not_import_owlrl():
    """models/mtg/schema.py must not import owlrl directly."""
    src = _read_source("models/mtg/schema.py")
    assert not _has_import(src, "owlrl")


def test_model_init_does_not_import_rdflib():
    """models/mtg/__init__.py must not import rdflib."""
    src = _read_source("models/mtg/__init__.py")
    assert not _has_import(src, "rdflib")


def test_demo_instance_does_not_import_rdflib():
    """demo/demo_instance.py must not import rdflib (H6)."""
    src = _read_source("demo/demo_instance.py")
    assert not _has_import(src, "rdflib")


def test_demo_notebook_does_not_import_rdflib():
    """demo/demo.py must not import rdflib, pyshacl, or owlrl (H6)."""
    src = _read_source("demo/demo.py")
    for lib in ["rdflib", "pyshacl", "owlrl"]:
        assert not _has_import(src, lib), f"demo.py imports {lib}"


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

def test_kc_all_exports():
    """kc.__all__ should be exactly the 7 public names."""
    import kc
    expected = {"SchemaBuilder", "vocab", "text", "TextDescriptor", "KnowledgeComplex", "ValidationError", "UnknownQueryError"}
    assert set(kc.__all__) == expected


def test_kc_exports_are_not_rdflib_types():
    """None of the names in kc.__all__ should be rdflib types."""
    import kc
    import rdflib
    rdflib_types = {getattr(rdflib, name) for name in dir(rdflib) if not name.startswith("_")}
    for name in kc.__all__:
        obj = getattr(kc, name)
        assert obj not in rdflib_types, f"kc exports rdflib type: {name}"


# ---------------------------------------------------------------------------
# Layer isolation
# ---------------------------------------------------------------------------

def test_model_schema_only_imports_from_kc_schema():
    """models/mtg/schema.py should only import from kc.schema, not kc.graph or kc.exceptions."""
    src = _read_source("models/mtg/schema.py")
    assert not _has_import(src, "kc.graph"), "Model schema should not import from kc.graph"
    assert not _has_import(src, "kc.exceptions"), "Model schema should not import from kc.exceptions"


def test_model_does_not_reference_core_resources():
    """Model layer should never directly reference kc_core.ttl or kc_core_shapes.ttl."""
    for f in ["models/mtg/schema.py", "models/mtg/__init__.py"]:
        src = _read_source(f)
        assert "kc_core.ttl" not in src, f"{f} references kc_core.ttl"
        assert "kc_core_shapes.ttl" not in src, f"{f} references kc_core_shapes.ttl"
