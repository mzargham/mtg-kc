"""
models.mtg.schema — MTG color wheel schema definition.

Defines the domain-specific types for the MTG knowledge complex:
- Color (vertex type)
- ColorPair (edge type) with disposition ∈ {adjacent, opposite}
- ColorTriple (face type) with optional pattern ∈ {ooa, oaa}

Design note — face enumeration policy:
    MTG explicitly enumerates all C(5,3)=10 ColorTriple faces in K5.
    This is an MTG model-level assertion, NOT a framework invariant.
    Other model families may leave faces absent (holes are meaningful).

Deferred issue — simplex inference from closed boundaries:
    A future framework extension could let a model family declare that
    closed k-boundaries necessitate (k+1)-simplices. When declared, the
    framework would provide methods to infer higher-order simplices from
    lower-order ones (e.g., infer all faces from vertices + edges alone).
    Without this declaration, faces must be added explicitly as MTG does
    today. Analogous to the proposed orientation extension — both are
    model-family-level framework features, not core invariants.
"""

from kc.schema import SchemaBuilder, vocab


def build_mtg_schema() -> SchemaBuilder:
    """Build and return the MTG color wheel schema."""
    sb = SchemaBuilder(namespace="mtg")
    sb.add_vertex_type("Color")
    sb.add_edge_type(
        "ColorPair",
        attributes={"disposition": vocab("adjacent", "opposite")},
    )
    sb.add_face_type(
        "ColorTriple",
        # pattern is optional here — to be discovered, not pre-asserted (REQ-DEMO-05)
        attributes={"pattern": {"vocab": vocab("ooa", "oaa"), "required": False}},
    )
    return sb
