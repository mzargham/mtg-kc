"""
kc.graph — KnowledgeComplex instance I/O.

Public API. Never exposes rdflib, pyshacl, or owlrl objects.

SHACL validation is run on every write (add_vertex, add_edge, add_face).
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
    ...             source="White", target="Blue", disposition="adjacent")
    >>> kc.add_face("WUB", type="ColorTriple", edges=["WU", "UB", "WB"])
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
        self._init_graph()

    def _init_graph(self) -> None:
        """
        Initialize the instance graph by parsing the merged OWL + SHACL from schema.
        """
        # TODO (WP3): parse schema.dump_owl() into rdflib.Graph; store separately for
        # use as ontology graph in pyshacl calls
        raise NotImplementedError

    def _validate(self, focus_node_id: str | None = None) -> None:
        """
        Run pyshacl against the current instance graph.

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
        Assert a vertex individual and validate.

        REQ-GRAPH-02

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
        # TODO (WP3)
        raise NotImplementedError

    def add_edge(
        self,
        id: str,
        type: str,
        source: str,
        target: str,
        **attributes: Any,
    ) -> None:
        """
        Assert an edge individual, link to source/target vertices, and validate.

        REQ-GRAPH-03

        Parameters
        ----------
        id : str
            Local identifier for the edge.
        type : str
            Edge type name (must be a registered subclass of KC:Edge).
        source : str
            ID of the source vertex individual.
        target : str
            ID of the target vertex individual.
        **attributes : Any
            Attribute values (e.g. disposition="adjacent").

        Raises
        ------
        ValidationError
            If SHACL validation fails after assertion.
        """
        # TODO (WP3)
        raise NotImplementedError

    def add_face(
        self,
        id: str,
        type: str,
        edges: list[str],
        **attributes: Any,
    ) -> None:
        """
        Assert a face individual, link to exactly 3 edge individuals, and validate.

        Includes closed-triangle SHACL sh:sparql constraint check.

        REQ-GRAPH-04

        Parameters
        ----------
        id : str
            Local identifier for the face.
        type : str
            Face type name (must be a registered subclass of KC:Face).
        edges : list[str]
            Exactly 3 edge IDs.
        **attributes : Any
            Attribute values (e.g. pattern="ooa").

        Raises
        ------
        ValueError
            If len(edges) != 3.
        ValidationError
            If SHACL validation fails after assertion.
        """
        if len(edges) != 3:
            raise ValueError(f"add_face requires exactly 3 edges; got {len(edges)}")
        # TODO (WP3)
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
