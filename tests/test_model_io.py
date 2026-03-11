"""
tests/test_model_io.py — WP3.5: Model import/export roundtrip tests.

Tests that SchemaBuilder and KnowledgeComplex can export to a directory
of standard semantic web files (OWL Turtle, SHACL Turtle, SPARQL) and
load back from that directory with full functionality preserved.
"""

import pytest
from pathlib import Path

from kc.schema import SchemaBuilder, vocab, text
from kc.graph import KnowledgeComplex


@pytest.fixture
def mtg_schema():
    sb = SchemaBuilder(namespace="mtg")
    sb.add_vertex_type("Color", attributes={
        "goal": text(),
    })
    sb.add_edge_type("ColorPair", attributes={
        "disposition": vocab("adjacent", "opposite"),
    })
    sb.add_face_type("ColorTriple", attributes={
        "pattern": {"vocab": vocab("ooa", "oaa"), "required": False},
    })
    return sb


@pytest.fixture
def mtg_queries_dir():
    return Path(__file__).parent.parent / "models" / "mtg" / "queries"


@pytest.fixture
def mtg_instance(mtg_schema, mtg_queries_dir):
    kc = KnowledgeComplex(schema=mtg_schema, query_dirs=[mtg_queries_dir])
    kc.add_vertex("White", type="Color", goal="peace")
    kc.add_vertex("Blue", type="Color", goal="perfection")
    kc.add_vertex("Black", type="Color", goal="power")
    kc.add_edge("WU", type="ColorPair", vertices={"White", "Blue"}, disposition="adjacent")
    kc.add_edge("UB", type="ColorPair", vertices={"Blue", "Black"}, disposition="adjacent")
    kc.add_edge("WB", type="ColorPair", vertices={"White", "Black"}, disposition="opposite")
    kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"])
    return kc


class TestSchemaExport:

    def test_export_creates_files(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        assert (out / "ontology.ttl").exists()
        assert (out / "shapes.ttl").exists()

    def test_export_includes_queries(self, mtg_schema, mtg_queries_dir, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg", query_dirs=[mtg_queries_dir])
        query_dir = out / "queries"
        assert query_dir.exists()
        sparql_files = list(query_dir.glob("*.sparql"))
        assert len(sparql_files) >= 2
        names = {f.stem for f in sparql_files}
        assert "edges_by_disposition" in names
        assert "faces_by_edge_pattern" in names

    def test_export_without_queries(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        assert not (out / "queries").exists()

    def test_export_owl_is_valid_turtle(self, mtg_schema, tmp_path):
        from rdflib import Graph
        out = mtg_schema.export(tmp_path / "mtg")
        g = Graph()
        g.parse(str(out / "ontology.ttl"), format="turtle")
        assert len(g) > 0


class TestSchemaLoad:

    def test_roundtrip_schema(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        assert loaded.dump_owl() == mtg_schema.dump_owl()
        assert loaded.dump_shacl() == mtg_schema.dump_shacl()

    def test_load_type_registry(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        assert "Color" in loaded._types
        assert loaded._types["Color"]["kind"] == "vertex"
        assert "ColorPair" in loaded._types
        assert loaded._types["ColorPair"]["kind"] == "edge"
        assert "ColorTriple" in loaded._types
        assert loaded._types["ColorTriple"]["kind"] == "face"

    def test_loaded_schema_supports_new_instances(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        kc = KnowledgeComplex(schema=loaded)
        kc.add_vertex("White", type="Color", goal="peace")
        kc.add_vertex("Blue", type="Color", goal="perfection")
        kc.add_edge("WU", type="ColorPair",
                     vertices={"White", "Blue"}, disposition="adjacent")

    def test_load_namespace(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        assert loaded._namespace == "mtg"


class TestKnowledgeComplexExport:

    def test_export_creates_instance_file(self, mtg_instance, tmp_path):
        out = mtg_instance.export(tmp_path / "mtg")
        assert (out / "instance.ttl").exists()
        assert (out / "ontology.ttl").exists()
        assert (out / "shapes.ttl").exists()

    def test_export_includes_queries(self, mtg_instance, tmp_path):
        out = mtg_instance.export(tmp_path / "mtg")
        assert (out / "queries").exists()
        sparql_files = list((out / "queries").glob("*.sparql"))
        assert len(sparql_files) >= 2


class TestKnowledgeComplexLoad:

    def test_roundtrip_instance(self, mtg_instance, tmp_path):
        out = mtg_instance.export(tmp_path / "mtg")
        loaded = KnowledgeComplex.load(out)
        # Verify vertices are present via query
        df = loaded.query("vertices")
        assert len(df) >= 3

    def test_load_without_instance(self, mtg_schema, mtg_queries_dir, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg", query_dirs=[mtg_queries_dir])
        loaded = KnowledgeComplex.load(out)
        df = loaded.query("vertices")
        assert len(df) == 0

    def test_loaded_queries_work(self, mtg_instance, tmp_path):
        out = mtg_instance.export(tmp_path / "mtg")
        loaded = KnowledgeComplex.load(out)
        df = loaded.query("edges_by_disposition")
        assert len(df) >= 1

    def test_loaded_instance_supports_new_elements(self, mtg_instance, tmp_path):
        out = mtg_instance.export(tmp_path / "mtg")
        loaded = KnowledgeComplex.load(out)
        # Should be able to add more elements to a loaded complex
        loaded.add_vertex("Red", type="Color", goal="freedom")
