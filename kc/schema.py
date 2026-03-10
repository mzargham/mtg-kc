"""
kc.schema — SchemaBuilder and vocab descriptor.

Public API. Never exposes rdflib, pyshacl, or owlrl objects.

Internal structure mirrors the 2x2 responsibility map:
  {topological, ontological} x {OWL, SHACL}

The core ontology defines KC:Element as the base class for all simplices,
with KC:Vertex (k=0), KC:Edge (k=1), KC:Face (k=2) as subclasses.
add_vertex_type / add_edge_type / add_face_type each declare a user type
as a subclass of the appropriate simplex class and write to both internal
OWL and SHACL graphs.

dump_owl() and dump_shacl() return merged (core + user) Turtle strings.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# rdflib is an internal implementation detail.
# Do not re-export any rdflib types through the public API.
import rdflib  # noqa: F401  (imported here; usage in _impl methods below)

_RESOURCES = Path(__file__).parent / "resources"
_CORE_OWL = _RESOURCES / "kc_core.ttl"
_CORE_SHAPES = _RESOURCES / "kc_core_shapes.ttl"


@dataclass(frozen=True)
class VocabDescriptor:
    """
    Returned by vocab(). Carries the allowed string values for an attribute.
    Generates both an OWL rdfs:comment annotation and a SHACL sh:in constraint
    when passed to add_*_type().
    """
    values: tuple[str, ...]

    def __repr__(self) -> str:
        return f"vocab({', '.join(repr(v) for v in self.values)})"


def vocab(*values: str) -> VocabDescriptor:
    """
    Declare a controlled vocabulary for an attribute.

    Parameters
    ----------
    *values : str
        The allowed string values.

    Returns
    -------
    VocabDescriptor

    Example
    -------
    >>> vocab("adjacent", "opposite")
    vocab('adjacent', 'opposite')
    """
    if not values:
        raise ValueError("vocab() requires at least one value")
    return VocabDescriptor(values=tuple(values))


class SchemaBuilder:
    """
    Author a knowledge complex schema: vertex types, edge types, face types.

    Each add_*_type call declares a new OWL subclass of the appropriate
    KC:Element subclass (Vertex, Edge, or Face) and creates a corresponding
    SHACL node shape. Both OWL and SHACL graphs are maintained internally.
    dump_owl() / dump_shacl() return the full merged Turtle strings.

    Parameters
    ----------
    namespace : str
        Short namespace token for user-defined classes and properties.
        Used to build IRI prefix: https://example.org/{namespace}#

    Example
    -------
    >>> sb = SchemaBuilder(namespace="mtg")
    >>> sb.add_vertex_type("Color")
    >>> sb.add_edge_type("Relationship",
    ...     attributes={"disposition": vocab("adjacent", "opposite")})
    >>> sb.add_face_type("ColorTriple",
    ...     attributes={"pattern": {"vocab": vocab("ooa", "oaa"), "required": False}})
    >>> owl_ttl = sb.dump_owl()
    >>> shacl_ttl = sb.dump_shacl()
    """

    def __init__(self, namespace: str) -> None:
        self._namespace = namespace
        self._base_iri = f"https://example.org/{namespace}#"
        # Internal graphs — never exposed publicly
        self._owl_graph: Any = None   # rdflib.Graph, populated in _init_graphs()
        self._shacl_graph: Any = None # rdflib.Graph, populated in _init_graphs()
        self._types: dict[str, dict] = {}  # registry: name -> {kind, attributes}
        self._init_graphs()

    def _init_graphs(self) -> None:
        """Load core OWL and SHACL static resources into internal graphs."""
        # TODO (WP3): implement using rdflib.Graph().parse()
        raise NotImplementedError

    def add_vertex_type(self, name: str) -> "SchemaBuilder":
        """
        Declare a new vertex type (OWL subclass of KC:Vertex, a KC:Element, + SHACL node shape).

        REQ-SCHEMA-02

        Parameters
        ----------
        name : str
            Class name within the user namespace.

        Returns
        -------
        SchemaBuilder (self, for chaining)
        """
        # TODO (WP3): write subclass triple to _owl_graph; write NodeShape to _shacl_graph
        raise NotImplementedError

    def add_edge_type(
        self,
        name: str,
        attributes: dict[str, VocabDescriptor | Any] | None = None,
    ) -> "SchemaBuilder":
        """
        Declare a new edge type (OWL subclass of KC:Edge, a KC:Element, + SHACL property shapes).

        REQ-SCHEMA-03

        Parameters
        ----------
        name : str
            Class name within the user namespace.
        attributes : dict, optional
            Mapping of attribute name to VocabDescriptor (or plain type annotation).
            Each attribute generates both an OWL data property and a SHACL sh:property.

        Returns
        -------
        SchemaBuilder (self, for chaining)
        """
        # TODO (WP3)
        raise NotImplementedError

    def add_face_type(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> "SchemaBuilder":
        """
        Declare a new face type (OWL subclass of KC:Face, a KC:Element, + SHACL property shapes).

        REQ-SCHEMA-04

        Attributes with ``required=False`` generate sh:minCount 0 constraints.

        Parameters
        ----------
        name : str
            Class name within the user namespace.
        attributes : dict, optional
            Mapping of attribute name to attribute specification. Each value is either:

            - A ``VocabDescriptor`` (from ``vocab()``) — required by default.
            - A ``dict`` with keys ``{"vocab": VocabDescriptor, "required": bool}``
              for optional attributes (``required=False`` generates sh:minCount 0).

        Returns
        -------
        SchemaBuilder (self, for chaining)
        """
        # TODO (WP3)
        raise NotImplementedError

    def promote_to_attribute(
        self,
        type: str,
        attribute: str,
        vocab: VocabDescriptor,
        required: bool = True,
    ) -> "SchemaBuilder":
        """
        Atomically promote a discovered pattern to a first-class typed attribute.

        Updates both OWL property definition and SHACL shape constraint for the named type.
        After calling this, dump_owl() and dump_shacl() both reflect the updated attribute.

        REQ-SCHEMA-08

        Parameters
        ----------
        type : str
            The type name (must have been registered via add_face_type or add_edge_type).
        attribute : str
            Attribute name to add or upgrade.
        vocab : VocabDescriptor
            Controlled vocabulary for the attribute.
        required : bool
            If True, generates sh:minCount 1 (was previously 0 or absent).

        Returns
        -------
        SchemaBuilder (self, for chaining)
        """
        # TODO (WP3)
        raise NotImplementedError

    def dump_owl(self) -> str:
        """
        Return merged OWL graph (core + user schema) as a Turtle string.

        REQ-SCHEMA-06
        """
        # TODO (WP3)
        raise NotImplementedError

    def dump_shacl(self) -> str:
        """
        Return merged SHACL graph (core shapes + user shapes) as a Turtle string.

        REQ-SCHEMA-07
        """
        # TODO (WP3)
        raise NotImplementedError
