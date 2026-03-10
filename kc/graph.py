"""
kc.graph — KnowledgeComplex instance I/O.

Public API. Never exposes rdflib, pyshacl, or owlrl objects.

A KnowledgeComplex corresponds to a kc:Complex individual in the RDF graph.
Each add_vertex / add_edge / add_face call asserts the new element AND its
kc:hasElement membership in the complex. SHACL validation on every write
enforces both per-element constraints (EdgeShape, FaceShape) and
boundary-closure (ComplexShape): if a simplex is in the complex, all its
boundary elements must be too.

This enforces the "slice rule": at every point during construction, the
elements added so far must form a valid complex. Concretely, an element's
boundary elements must already be members before it can be added. This is
a partial ordering — types can be interleaved as long as each element's
boundary predecessors are present (e.g., add v1, v2, edge(v1,v2), v3,
edge(v2,v3), ...). The simplest strategy is to add all vertices, then all
edges, then all faces, but this is not required.

SPARQL queries are encapsulated as named templates. The framework provides
generic queries in kc/queries/; domain models can supply additional query
directories via the query_dirs parameter.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any

import pandas as pd

from kc.exceptions import ValidationError, UnknownQueryError
from kc.schema import SchemaBuilder

_FRAMEWORK_QUERIES_DIR = Path(__file__).parent / "queries"


def _load_query_templates(
    extra_dirs: list[Path] | None = None,
) -> dict[str, str]:
    """Load .sparql files from framework queries dir and any extra directories.

    Extra directories (e.g. from domain models) are loaded after the framework
    queries. If a model provides a query with the same name as a framework query,
    the model's version takes precedence.
    """
    templates: dict[str, str] = {}
    dirs = [_FRAMEWORK_QUERIES_DIR] + (extra_dirs or [])
    for d in dirs:
        for path in d.glob("*.sparql"):
            templates[path.stem] = path.read_text()
    return templates


class KnowledgeComplex:
    """
    Manage a knowledge complex instance: add elements, validate, query.

    Maps to a kc:Complex individual in the RDF graph. Each element added
    via add_vertex / add_edge / add_face becomes a kc:hasElement member of
    this complex. Boundary-closure is enforced by ComplexShape on every write
    (the "slice rule": every prefix of the insertion sequence is a valid complex).
    An element's boundary elements must be added before the element itself.

    Parameters
    ----------
    schema : SchemaBuilder
        A fully configured schema. The merged OWL + SHACL is loaded into
        the internal graph at construction time.
    query_dirs : list[Path], optional
        Additional directories containing .sparql query templates
        (e.g. from domain models). Merged with the framework's built-in queries.

    Example
    -------
    >>> from models.mtg import build_mtg_schema, QUERIES_DIR
    >>> kc = KnowledgeComplex(schema=sb, query_dirs=[QUERIES_DIR])
    >>> kc.add_vertex("White", type="Color")
    >>> kc.add_edge("WU", type="Relationship",
    ...             vertices={"White", "Blue"}, disposition="adjacent")
    >>> kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"])
    >>> df = kc.query("faces_by_edge_pattern")
    """

    def __init__(
        self,
        schema: SchemaBuilder,
        query_dirs: list[Path] | None = None,
    ) -> None:
        self._schema = schema
        self._query_templates = _load_query_templates(extra_dirs=query_dirs)
        self._instance_graph: Any = None  # rdflib.Graph, populated in _init_graph()
        self._complex_iri: Any = None     # URIRef for the kc:Complex individual
        self._init_graph()

    def _init_graph(self) -> None:
        """
        Initialize the instance graph and create the kc:Complex individual.

        Parses the merged OWL from schema into the instance graph.
        Creates a kc:Complex individual to serve as the container for all
        elements added via add_vertex / add_edge / add_face.
        Stores the ontology + shapes graphs separately for pyshacl calls.
        """
        # TODO (WP3):
        #   1. Parse schema.dump_owl() into rdflib.Graph (instance graph)
        #   2. Store schema OWL and SHACL graphs for pyshacl ont_graph/shacl_graph
        #   3. Create kc:Complex individual: _complex_iri = URIRef(f"{namespace}#_complex")
        #   4. Assert (_complex_iri, RDF.type, KC.Complex) in instance graph
        raise NotImplementedError

    def _validate(self, focus_node_id: str | None = None) -> None:
        """
        Run pyshacl against the current instance graph.

        Validates both element-level shapes (EdgeShape, FaceShape) and
        complex-level shapes (ComplexShape boundary-closure).

        Parameters
        ----------
        focus_node_id : str, optional
            If provided, validate only this node (for incremental write validation).
            If None, validate entire graph.

        Raises
        ------
        ValidationError
            If validation fails. report attribute contains human-readable text.
        """
        # TODO (WP3): call pyshacl.validate(); raise ValidationError on failure
        raise NotImplementedError

    def add_vertex(self, id: str, type: str, **attributes: Any) -> None:
        """
        Assert a vertex individual and add it to the complex.

        REQ-GRAPH-02

        Asserts the vertex as an individual of the given type (subclass of
        KC:Vertex, which is a KC:Element), then asserts kc:hasElement on the
        complex. Validates via SHACL. Vertices have empty boundary (k=0),
        so boundary-closure is trivially satisfied.

        Parameters
        ----------
        id : str
            Local identifier for the vertex.
        type : str
            Vertex type name (must be a registered subclass of KC:Vertex).
        **attributes : Any
            Additional attribute values for the vertex.

        Raises
        ------
        ValidationError
            If SHACL validation fails after assertion.
        """
        # TODO (WP3):
        #   1. Assert (id_iri, RDF.type, type_iri) in instance graph
        #   2. Assert any attributes as data properties
        #   3. Assert (_complex_iri, KC.hasElement, id_iri)
        #   4. Call _validate(id)
        raise NotImplementedError

    def add_edge(
        self,
        id: str,
        type: str,
        vertices: set[str] | list[str],
        **attributes: Any,
    ) -> None:
        """
        Assert an edge individual, link to boundary vertices, and add to complex.

        REQ-GRAPH-03

        Asserts the edge as an individual of the given type (subclass of
        KC:Edge, which is a KC:Element), links it to exactly 2 boundary
        vertices via kc:boundedBy, then asserts kc:hasElement on the complex.
        Validates via SHACL including:
        - EdgeShape: exactly 2 distinct boundary vertices
        - ComplexShape: boundary vertices must already be members of the complex

        Parameters
        ----------
        id : str
            Local identifier for the edge.
        type : str
            Edge type name (must be a registered subclass of KC:Edge).
        vertices : set[str] | list[str]
            Exactly 2 vertex IDs forming the boundary of this edge.
            Unordered (edges are unoriented in this demo).
        **attributes : Any
            Attribute values (e.g. disposition="adjacent").

        Raises
        ------
        ValueError
            If len(vertices) != 2.
        ValidationError
            If SHACL validation fails after assertion.
        """
        if len(vertices) != 2:
            raise ValueError(f"add_edge requires exactly 2 vertices; got {len(vertices)}")
        # TODO (WP3):
        #   1. Assert (id_iri, RDF.type, type_iri)
        #   2. Assert (id_iri, KC.boundedBy, v_iri) for each vertex
        #   3. Assert any attributes as data properties
        #   4. Assert (_complex_iri, KC.hasElement, id_iri)
        #   5. Call _validate(id)
        raise NotImplementedError

    def add_face(
        self,
        id: str,
        type: str,
        boundary: list[str],
        **attributes: Any,
    ) -> None:
        """
        Assert a face individual, link to boundary edges, and add to complex.

        REQ-GRAPH-04

        Asserts the face as an individual of the given type (subclass of
        KC:Face, which is a KC:Element), links it to exactly 3 boundary
        edges via kc:boundedBy, then asserts kc:hasElement on the complex.
        Validates via SHACL including:
        - FaceShape: exactly 3 boundary edges forming a closed triangle
        - ComplexShape: boundary edges must already be members of the complex

        Parameters
        ----------
        id : str
            Local identifier for the face.
        type : str
            Face type name (must be a registered subclass of KC:Face).
        boundary : list[str]
            Exactly 3 edge IDs forming the boundary of this face.
        **attributes : Any
            Attribute values (e.g. pattern="ooa").

        Raises
        ------
        ValueError
            If len(boundary) != 3.
        ValidationError
            If SHACL validation fails after assertion.
        """
        if len(boundary) != 3:
            raise ValueError(f"add_face requires exactly 3 boundary edges; got {len(boundary)}")
        # TODO (WP3):
        #   1. Assert (id_iri, RDF.type, type_iri)
        #   2. Assert (id_iri, KC.boundedBy, e_iri) for each edge
        #   3. Assert any attributes as data properties
        #   4. Assert (_complex_iri, KC.hasElement, id_iri)
        #   5. Call _validate(id)
        raise NotImplementedError

    def query(self, template_name: str, **kwargs: Any) -> pd.DataFrame:
        """
        Execute a named SPARQL template and return results as a DataFrame.

        REQ-GRAPH-06, REQ-GRAPH-07

        Parameters
        ----------
        template_name : str
            Name of a registered query template (filename stem from
            framework or model query directories).
        **kwargs : Any
            Substitution values for {placeholder} tokens in the template.

        Returns
        -------
        pd.DataFrame
            One row per SPARQL result binding.

        Raises
        ------
        UnknownQueryError
            If template_name is not registered.
        """
        if template_name not in self._query_templates:
            raise UnknownQueryError(
                f"No query template named '{template_name}'. "
                f"Available: {sorted(self._query_templates)}"
            )
        # TODO (WP3): substitute kwargs, execute via rdflib, return DataFrame
        raise NotImplementedError

    def dump_graph(self) -> str:
        """
        Return the instance graph as a Turtle string.

        REQ-GRAPH-08
        """
        # TODO (WP3)
        raise NotImplementedError
