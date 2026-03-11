"""
tests/test_model_io.py — Model import/export roundtrip tests.

Tests that SchemaBuilder and KnowledgeComplex can export to a directory
of standard semantic web files (OWL Turtle, SHACL Turtle, SPARQL) and
load back from that directory with full functionality preserved.

Updated for WP4.5 enriched schema (structure/shard/wedge, text attributes).
"""

import pytest
from pathlib import Path

from kc.schema import SchemaBuilder, vocab, text
from kc.graph import KnowledgeComplex
from kc.exceptions import ValidationError


@pytest.fixture
def mtg_schema():
    """Enriched MTG schema matching models/mtg/schema.py."""
    sb = SchemaBuilder(namespace="mtg")
    sb.add_vertex_type("Color", attributes={
        "goal": vocab("peace", "perfection", "satisfaction", "freedom", "harmony"),
        "method": vocab("order", "knowledge", "ruthlessness", "action", "acceptance"),
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })
    sb.add_edge_type("ColorPair", attributes={
        "disposition": vocab("adjacent", "opposite"),
        "guild": vocab(
            "azorius", "dimir", "rakdos", "gruul", "selesnya",
            "orzhov", "boros", "simic", "izzet", "golgari",
        ),
        "theme": vocab(
            "design", "growth_mindset", "independence", "authenticity", "community",
            "tribalism", "heroism", "truth_seeking", "creativity", "profanity",
        ),
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })
    sb.add_face_type("ColorTriple", attributes={
        "clan": vocab(
            "esper", "grixis", "jund", "naya", "bant",
            "mardu", "temur", "abzan", "jeskai", "sultai",
        ),
        "structure": {"vocab": vocab("shard", "wedge"), "required": False},
        "persona": text(),
        "at_best": text(),
        "at_worst": text(),
        "example_behaviors": text(multiple=True),
        "playstyle": text(required=False),
        "example_decks": text(multiple=True, required=False),
    })
    return sb


@pytest.fixture
def mtg_queries_dir():
    return Path(__file__).parent.parent / "models" / "mtg" / "queries"


@pytest.fixture
def mtg_instance(mtg_schema, mtg_queries_dir):
    kc = KnowledgeComplex(schema=mtg_schema, query_dirs=[mtg_queries_dir])
    kc.add_vertex("White", type="Color",
        goal="peace", method="order",
        persona="Test persona W.", at_best="Best W.", at_worst="Worst W.",
        example_behaviors=["Behavior W1", "Behavior W2"])
    kc.add_vertex("Blue", type="Color",
        goal="perfection", method="knowledge",
        persona="Test persona U.", at_best="Best U.", at_worst="Worst U.",
        example_behaviors=["Behavior U1"])
    kc.add_vertex("Black", type="Color",
        goal="satisfaction", method="ruthlessness",
        persona="Test persona B.", at_best="Best B.", at_worst="Worst B.",
        example_behaviors=["Behavior B1"])
    kc.add_edge("WU", type="ColorPair",
        vertices={"White", "Blue"}, disposition="adjacent",
        guild="azorius", theme="design",
        persona="Test persona WU.", at_best="Best WU.", at_worst="Worst WU.",
        example_behaviors=["Behavior WU1"])
    kc.add_edge("UB", type="ColorPair",
        vertices={"Blue", "Black"}, disposition="adjacent",
        guild="dimir", theme="growth_mindset",
        persona="Test persona UB.", at_best="Best UB.", at_worst="Worst UB.",
        example_behaviors=["Behavior UB1"])
    kc.add_edge("WB", type="ColorPair",
        vertices={"White", "Black"}, disposition="opposite",
        guild="orzhov", theme="tribalism",
        persona="Test persona WB.", at_best="Best WB.", at_worst="Worst WB.",
        example_behaviors=["Behavior WB1"])
    kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"],
        clan="esper",
        persona="Test persona WUB.", at_best="Best WUB.", at_worst="Worst WUB.",
        example_behaviors=["Behavior WUB1"])
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
        from rdflib import Graph
        from rdflib.compare import isomorphic
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        # Compare graphs semantically (BNode ordering is non-deterministic)
        owl_orig = Graph().parse(data=mtg_schema.dump_owl(), format="turtle")
        owl_loaded = Graph().parse(data=loaded.dump_owl(), format="turtle")
        assert isomorphic(owl_orig, owl_loaded), "OWL graphs not isomorphic after roundtrip"
        shacl_orig = Graph().parse(data=mtg_schema.dump_shacl(), format="turtle")
        shacl_loaded = Graph().parse(data=loaded.dump_shacl(), format="turtle")
        assert isomorphic(shacl_orig, shacl_loaded), "SHACL graphs not isomorphic after roundtrip"

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
        kc.add_vertex("White", type="Color",
            goal="peace", method="order",
            persona="Test.", at_best="Best.", at_worst="Worst.",
            example_behaviors=["B1"])
        kc.add_vertex("Blue", type="Color",
            goal="perfection", method="knowledge",
            persona="Test.", at_best="Best.", at_worst="Worst.",
            example_behaviors=["B1"])
        kc.add_edge("WU", type="ColorPair",
            vertices={"White", "Blue"}, disposition="adjacent",
            guild="azorius", theme="design",
            persona="Test.", at_best="Best.", at_worst="Worst.",
            example_behaviors=["B1"])

    def test_load_namespace(self, mtg_schema, tmp_path):
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        assert loaded._namespace == "mtg"

    def test_loaded_schema_enforces_validation(self, mtg_schema, tmp_path):
        """SHACL constraints survive export/load roundtrip."""
        out = mtg_schema.export(tmp_path / "mtg")
        loaded = SchemaBuilder.load(out)
        kc = KnowledgeComplex(schema=loaded)
        with pytest.raises(ValidationError):
            kc.add_vertex("White", type="Color")  # missing required attrs


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
        loaded.add_vertex("Red", type="Color",
            goal="freedom", method="action",
            persona="Test.", at_best="Best.", at_worst="Worst.",
            example_behaviors=["B1"])

    def test_roundtrip_preserves_text_attrs(self, mtg_instance, tmp_path):
        """Free-text and list attributes survive roundtrip."""
        out = mtg_instance.export(tmp_path / "mtg")
        loaded = KnowledgeComplex.load(out)
        ttl = loaded.dump_graph()
        assert "Test persona W." in ttl
        assert "Behavior W1" in ttl
        assert "Behavior W2" in ttl
