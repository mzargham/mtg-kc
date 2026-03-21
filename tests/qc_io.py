import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import tempfile
    from pathlib import Path

    from knowledgecomplex import SchemaBuilder, KnowledgeComplex, ValidationError
    from models.mtg import build_mtg_schema, QUERIES_DIR
    from demo.demo_instance import build_mtg_instance
    return (
        KnowledgeComplex, Path, SchemaBuilder, ValidationError,
        build_mtg_instance, build_mtg_schema, mo, tempfile, QUERIES_DIR,
    )


@app.cell
def cell_1_build_and_export(mo, tempfile, Path, build_mtg_schema, QUERIES_DIR):
    """Cell 1: Build a model at runtime and export it."""
    sb = build_mtg_schema()
    schema_export_dir = Path(tempfile.mkdtemp()) / "mtg_schema"
    schema_path = sb.export(schema_export_dir, query_dirs=[QUERIES_DIR])

    # Inventory what was written
    schema_files = []
    for entry in sorted(schema_path.rglob("*")):
        if entry.is_file():
            schema_files.append(
                f"{entry.relative_to(schema_path)}  ({entry.stat().st_size:,} bytes)"
            )
    schema_listing = "\n".join(schema_files)

    # Show OWL snippet (first 40 lines)
    owl_text = (schema_path / "ontology.ttl").read_text()
    owl_snippet = "\n".join(owl_text.splitlines()[:40])

    mo.output.replace(mo.md(f"""
## 1. Build a Model at Runtime and Export It

`build_mtg_schema()` constructs the full MTG color wheel schema with enriched
attributes (goal, method, persona, guild, theme, clan, structure, etc.).

`sb.export(path, query_dirs=[QUERIES_DIR])` writes standard semantic web files:

```
{schema_listing}
```

**OWL ontology snippet** (first 40 lines):

```turtle
{owl_snippet}
```

All 3 types (Color, ColorPair, ColorTriple) with their vocab and text attributes
are serialized as OWL DatatypeProperties + SHACL NodeShapes.
"""))
    return schema_path,


@app.cell
def cell_2_load_and_verify(
    mo, SchemaBuilder, KnowledgeComplex, ValidationError, schema_path
):
    """Cell 2: Load a model and build+verify a knowledge complex."""
    # Load schema from exported files
    loaded_sb = SchemaBuilder.load(schema_path)

    # Verify type registry reconstructed
    types_info = {name: info["kind"] for name, info in loaded_sb._types.items()}

    # Build a small instance against the loaded schema
    kc_loaded = KnowledgeComplex(schema=loaded_sb)

    # Demonstrate validation: missing required attributes should fail
    validation_msg = ""
    try:
        kc_loaded.add_vertex("White", type="Color")
        validation_msg = "ERROR: should have raised ValidationError"
    except ValidationError:
        validation_msg = "ValidationError raised (missing required attributes)"

    # Now add with all required attributes — should pass
    kc_loaded.add_vertex("White", type="Color",
        goal="peace", method="order",
        persona="Test persona.", at_best="Best.", at_worst="Worst.",
        example_behaviors=["Behavior 1"])
    kc_loaded.add_vertex("Blue", type="Color",
        goal="perfection", method="knowledge",
        persona="Test persona.", at_best="Best.", at_worst="Worst.",
        example_behaviors=["Behavior 1"])
    kc_loaded.add_edge("WU", type="ColorPair",
        vertices={"White", "Blue"}, disposition="adjacent",
        guild="azorius", theme="design",
        persona="Test persona.", at_best="Best.", at_worst="Worst.",
        example_behaviors=["Behavior 1"])

    loaded_vertices_df = kc_loaded.query("vertices")

    # Strip namespace URIs to short names for display
    def _short(uri):
        return str(uri).rsplit("#", 1)[-1] if "#" in str(uri) else str(uri).rsplit("/", 1)[-1]

    vtx_display = loaded_vertices_df.copy()
    vtx_display["name"] = vtx_display["vertex"].apply(_short)
    vtx_display = vtx_display.rename(columns={"vertex": "URI", "type": "type URI"})
    vtx_display["type"] = vtx_display["type URI"].apply(_short)
    vtx_display = vtx_display[["name", "type", "URI"]]

    mo.output.replace(mo.md(f"""
## 2. Load a Model and Build + Verify a Knowledge Complex

`SchemaBuilder.load(path)` reconstructs the schema from `ontology.ttl` + `shapes.ttl`.

**Reconstructed type registry:** `{types_info}`

**SHACL validation on loaded schema:**
- Attempt to add Color without required attributes: **{validation_msg}**
- Add Color with all required attributes: **accepted**
- Add 2 vertices + 1 edge: **all validated successfully**

**Vertices in the new instance:**

{vtx_display.to_markdown(index=False)}

The loaded schema enforces the same constraints as the original — SHACL shapes
survive the export/load roundtrip.
"""))
    return


@app.cell
def cell_3_export_full_kc(mo, tempfile, Path, build_mtg_instance):
    """Cell 3: Export a concrete knowledge complex."""
    # Build the full MTG instance (5 vertices, 10 edges, 10 faces)
    kc_full = build_mtg_instance()
    kc_export_dir = Path(tempfile.mkdtemp()) / "mtg_full"
    kc_path = kc_full.export(kc_export_dir)

    # Inventory
    kc_files = []
    for kc_entry in sorted(kc_path.rglob("*")):
        if kc_entry.is_file():
            kc_files.append(
                f"{kc_entry.relative_to(kc_path)}  ({kc_entry.stat().st_size:,} bytes)"
            )
    kc_listing = "\n".join(kc_files)

    # Count elements
    n_vertices_full = len(kc_full.query("vertices"))
    n_edges_full = len(kc_full.query("edges_by_disposition"))
    n_faces_full = len(kc_full.query("faces_by_edge_pattern"))

    # Instance snippet (first 30 lines)
    instance_text = (kc_path / "instance.ttl").read_text()
    instance_snippet = "\n".join(instance_text.splitlines()[:30])

    mo.output.replace(mo.md(f"""
## 3. Export a Concrete Knowledge Complex

`build_mtg_instance()` constructs the full MTG color wheel:
**{n_vertices_full} vertices, {n_edges_full} edges, {n_faces_full} faces** — all with enriched
essay-derived attributes (persona, at_best, at_worst, example_behaviors, etc.).

`kc.export(path)` writes schema + queries + instance data:

```
{kc_listing}
```

**Instance graph snippet** (first 30 lines):

```turtle
{instance_snippet}
```

The instance.ttl contains all 25 elements with their full attribute values.
"""))
    return kc_path,


@app.cell
def cell_4_import_kc(mo, KnowledgeComplex, kc_path):
    """Cell 4: Import a concrete knowledge complex."""
    # Load the exported knowledge complex
    imported_kc = KnowledgeComplex.load(kc_path)

    # Run queries on the loaded instance
    imported_vertices = imported_kc.query("vertices")
    imported_edges = imported_kc.query("edges_by_disposition")
    imported_faces = imported_kc.query("faces_by_edge_pattern")

    n_v = len(imported_vertices)
    n_adj = len(imported_edges[imported_edges["disposition"] == "adjacent"])
    n_opp = len(imported_edges[imported_edges["disposition"] == "opposite"])
    n_f = len(imported_faces)

    # SPARQL discovery: classify faces as shard/wedge from edge dispositions
    def _classify_structure(row):
        dispositions = sorted([row["d1"], row["d2"], row["d3"]])
        if dispositions.count("opposite") == 1:
            return "shard"
        elif dispositions.count("opposite") == 2:
            return "wedge"
        return "unknown"

    imported_faces["structure"] = imported_faces.apply(_classify_structure, axis=1)
    n_shards = len(imported_faces[imported_faces["structure"] == "shard"])
    n_wedges = len(imported_faces[imported_faces["structure"] == "wedge"])

    # Strip namespace URIs to short names for display
    def _short_name(uri):
        return str(uri).rsplit("#", 1)[-1] if "#" in str(uri) else str(uri).rsplit("/", 1)[-1]

    imported_faces["name"] = imported_faces["face"].apply(_short_name)

    # Build a description from the edge dispositions
    def _describe(row):
        disps = sorted([row["d1"], row["d2"], row["d3"]])
        n_opp_d = disps.count("opposite")
        n_adj_d = disps.count("adjacent")
        return f"{n_adj_d} adjacent + {n_opp_d} opposite edges"

    imported_faces["description"] = imported_faces.apply(_describe, axis=1)

    # Verify counts
    checks = [
        f"Vertices: {n_v} {'(pass)' if n_v == 5 else '(FAIL)'}",
        f"Adjacent edges: {n_adj} {'(pass)' if n_adj == 5 else '(FAIL)'}",
        f"Opposite edges: {n_opp} {'(pass)' if n_opp == 5 else '(FAIL)'}",
        f"Faces: {n_f} {'(pass)' if n_f == 10 else '(FAIL)'}",
        f"Shards: {n_shards} {'(pass)' if n_shards == 5 else '(FAIL)'}",
        f"Wedges: {n_wedges} {'(pass)' if n_wedges == 5 else '(FAIL)'}",
    ]

    # Check text attributes survived
    imported_ttl = imported_kc.dump_graph()
    has_persona = "Believes the solution to suffering" in imported_ttl
    has_behaviors = "Creating fair rules" in imported_ttl
    checks.append(f"Text attributes preserved: {'(pass)' if has_persona else '(FAIL)'}")
    checks.append(f"List attributes preserved: {'(pass)' if has_behaviors else '(FAIL)'}")

    checks_text = "\n".join(f"- {c}" for c in checks)

    display_df = imported_faces[["name", "face", "structure", "description"]].sort_values("name")
    display_df = display_df.rename(columns={"face": "URI"})

    mo.output.replace(mo.md(f"""
## 4. Import a Concrete Knowledge Complex

`KnowledgeComplex.load(path)` reconstructs the full instance from exported files.

**Verification checks:**

{checks_text}

**SPARQL discovery on loaded instance** — classifying faces by edge dispositions:

{display_df.to_markdown(index=False)}

All queries, validation, and discovery work identically on the imported instance.
The full roundtrip (build -> export -> load -> query) preserves both structural
topology and enriched content attributes.
"""))
    return


if __name__ == "__main__":
    app.run()
