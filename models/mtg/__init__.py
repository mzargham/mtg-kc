"""
models.mtg — MTG color wheel domain model.

Layer 2: domain-specific schema types and queries built on the kc framework.
Defines Color, ColorPair, and ColorTriple types with MTG-specific
controlled vocabularies and SPARQL queries.

Usage:
    from models.mtg import build_mtg_schema, QUERIES_DIR
    sb = build_mtg_schema()
    kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])
"""

from models.mtg.schema import build_mtg_schema
from pathlib import Path

QUERIES_DIR = Path(__file__).parent / "queries"

__all__ = ["build_mtg_schema", "QUERIES_DIR"]
