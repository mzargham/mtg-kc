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
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD, BNode
from rdflib.collection import Collection

_RESOURCES = Path(__file__).parent / "resources"
_CORE_OWL = _RESOURCES / "kc_core.ttl"
_CORE_SHAPES = _RESOURCES / "kc_core_shapes.ttl"

# Internal namespace constants
_KC = Namespace("https://example.org/kc#")
_KCS = Namespace("https://example.org/kc/shape#")
_SH = Namespace("http://www.w3.org/ns/shacl#")


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
    >>> sb.add_edge_type("ColorPair",
    ...     attributes={"disposition": vocab("adjacent", "opposite")})
    >>> sb.add_face_type("ColorTriple",
    ...     attributes={"pattern": {"vocab": vocab("ooa", "oaa"), "required": False}})
    >>> owl_ttl = sb.dump_owl()
    >>> shacl_ttl = sb.dump_shacl()
    """

    def __init__(self, namespace: str) -> None:
        self._namespace = namespace
        self._base_iri = f"https://example.org/{namespace}#"
        # Internal namespace objects
        self._ns = Namespace(self._base_iri)
        self._nss = Namespace(f"https://example.org/{namespace}/shape#")
        # Internal graphs — never exposed publicly
        self._owl_graph: Any = None   # rdflib.Graph, populated in _init_graphs()
        self._shacl_graph: Any = None # rdflib.Graph, populated in _init_graphs()
        self._types: dict[str, dict] = {}  # registry: name -> {kind, attributes}
        self._init_graphs()

    def _init_graphs(self) -> None:
        """Load core OWL and SHACL static resources into internal graphs."""
        self._owl_graph = Graph()
        self._owl_graph.parse(str(_CORE_OWL), format="turtle")

        self._shacl_graph = Graph()
        self._shacl_graph.parse(str(_CORE_SHAPES), format="turtle")

        # Bind prefixes on both graphs
        for g in (self._owl_graph, self._shacl_graph):
            g.bind("kc", _KC)
            g.bind("kcs", _KCS)
            g.bind("sh", _SH)
            g.bind("owl", OWL)
            g.bind("rdfs", RDFS)
            g.bind("rdf", RDF)
            g.bind("xsd", XSD)
            g.bind(self._namespace, self._ns)
            g.bind(f"{self._namespace}s", self._nss)

    def _add_attr_to_graphs(
        self,
        type_iri: URIRef,
        shape_iri: URIRef,
        attr_name: str,
        vocab_desc: VocabDescriptor,
        required: bool,
    ) -> None:
        """Add an attribute's OWL property and SHACL property shape."""
        attr_iri = self._ns[attr_name]

        # OWL: declare data property
        self._owl_graph.add((attr_iri, RDF.type, OWL.DatatypeProperty))
        self._owl_graph.add((attr_iri, RDFS.domain, type_iri))
        self._owl_graph.add((attr_iri, RDFS.range, XSD.string))
        self._owl_graph.add((attr_iri, RDFS.comment,
                             Literal(f"Allowed values: {', '.join(vocab_desc.values)}")))

        # SHACL: create property shape
        prop_shape = BNode()
        self._shacl_graph.add((shape_iri, _SH.property, prop_shape))
        self._shacl_graph.add((prop_shape, _SH.path, attr_iri))
        self._shacl_graph.add((prop_shape, _SH.datatype, XSD.string))
        self._shacl_graph.add((prop_shape, _SH.minCount, Literal(1 if required else 0)))
        self._shacl_graph.add((prop_shape, _SH.maxCount, Literal(1)))

        # sh:in list
        list_node = BNode()
        self._shacl_graph.add((prop_shape, _SH["in"], list_node))
        Collection(self._shacl_graph, list_node,
                   [Literal(v) for v in vocab_desc.values])

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
        self._types[name] = {"kind": "vertex"}
        type_iri = self._ns[name]
        shape_iri = self._nss[f"{name}Shape"]

        # OWL
        self._owl_graph.add((type_iri, RDF.type, OWL.Class))
        self._owl_graph.add((type_iri, RDFS.subClassOf, _KC.Vertex))

        # SHACL
        self._shacl_graph.add((shape_iri, RDF.type, _SH.NodeShape))
        self._shacl_graph.add((shape_iri, _SH.targetClass, type_iri))

        return self

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
        attributes = attributes or {}
        self._types[name] = {"kind": "edge", "attributes": dict(attributes)}
        type_iri = self._ns[name]
        shape_iri = self._nss[f"{name}Shape"]

        # OWL
        self._owl_graph.add((type_iri, RDF.type, OWL.Class))
        self._owl_graph.add((type_iri, RDFS.subClassOf, _KC.Edge))

        # SHACL
        self._shacl_graph.add((shape_iri, RDF.type, _SH.NodeShape))
        self._shacl_graph.add((shape_iri, _SH.targetClass, type_iri))

        for attr_name, attr_spec in attributes.items():
            if isinstance(attr_spec, VocabDescriptor):
                self._add_attr_to_graphs(type_iri, shape_iri, attr_name, attr_spec, required=True)
            else:
                vd = attr_spec["vocab"]
                req = attr_spec.get("required", True)
                self._add_attr_to_graphs(type_iri, shape_iri, attr_name, vd, required=req)

        return self

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
        attributes = attributes or {}
        self._types[name] = {"kind": "face", "attributes": dict(attributes)}
        type_iri = self._ns[name]
        shape_iri = self._nss[f"{name}Shape"]

        # OWL
        self._owl_graph.add((type_iri, RDF.type, OWL.Class))
        self._owl_graph.add((type_iri, RDFS.subClassOf, _KC.Face))

        # SHACL
        self._shacl_graph.add((shape_iri, RDF.type, _SH.NodeShape))
        self._shacl_graph.add((shape_iri, _SH.targetClass, type_iri))

        for attr_name, attr_spec in attributes.items():
            if isinstance(attr_spec, VocabDescriptor):
                self._add_attr_to_graphs(type_iri, shape_iri, attr_name, attr_spec, required=True)
            else:
                vd = attr_spec["vocab"]
                req = attr_spec.get("required", True)
                self._add_attr_to_graphs(type_iri, shape_iri, attr_name, vd, required=req)

        return self

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
        from kc.exceptions import SchemaError
        if type not in self._types:
            raise SchemaError(f"Type '{type}' is not registered")

        type_iri = self._ns[type]
        shape_iri = self._nss[f"{type}Shape"]
        attr_iri = self._ns[attribute]

        # Remove existing OWL triples for this attribute (if upgrading)
        for p in (RDFS.domain, RDFS.range, RDFS.comment):
            self._owl_graph.remove((attr_iri, p, None))
        self._owl_graph.remove((attr_iri, RDF.type, OWL.DatatypeProperty))

        # Remove existing SHACL property shape for this attribute (if upgrading)
        for prop_node in list(self._shacl_graph.objects(shape_iri, _SH.property)):
            if (prop_node, _SH.path, attr_iri) in self._shacl_graph:
                # Remove the sh:in list
                list_head = self._shacl_graph.value(prop_node, _SH["in"])
                if list_head is not None:
                    Collection(self._shacl_graph, list_head).clear()
                    self._shacl_graph.remove((prop_node, _SH["in"], list_head))
                # Remove all triples about this property shape
                for p, o in list(self._shacl_graph.predicate_objects(prop_node)):
                    self._shacl_graph.remove((prop_node, p, o))
                self._shacl_graph.remove((shape_iri, _SH.property, prop_node))

        # Re-add with new settings
        self._add_attr_to_graphs(type_iri, shape_iri, attribute, vocab, required)

        # Update type registry
        if "attributes" not in self._types[type]:
            self._types[type]["attributes"] = {}
        self._types[type]["attributes"][attribute] = {
            "vocab": vocab, "required": required
        }

        return self

    def dump_owl(self) -> str:
        """
        Return merged OWL graph (core + user schema) as a Turtle string.

        REQ-SCHEMA-06
        """
        return self._owl_graph.serialize(format="turtle")

    def dump_shacl(self) -> str:
        """
        Return merged SHACL graph (core shapes + user shapes) as a Turtle string.

        REQ-SCHEMA-07
        """
        return self._shacl_graph.serialize(format="turtle")
