# Worklog: Plan vs. Actuals

This directory tracks the phased execution of the mtg-kc project. Each work package (WP) has its own file.

## Work Package Summary

| WP | Status | Planned? | Delivered |
|----|--------|----------|-----------|
| WP0 | Accepted | Yes | Repository reorganization into three-layer structure |
| WP1+WP2 | Accepted | Yes | Abstract OWL + SHACL core; Element base class, Complex container, boundedBy operator |
| WP2.5 | Accepted | Emerged | Downstream stub alignment; KnowledgeComplex ↔ kc:Complex mapping, slice rule |
| WP2.8 | In Review | Emerged | Abstraction boundary definition; core vs. model family responsibilities |
| WP3 | In Review | Yes | Python API; SchemaBuilder (7 methods) + KnowledgeComplex (7 methods) |
| WP4 | In Review | Yes | MTG demo instance; 5 vertices, 10 edges, 10 faces |
| WP4.5 | In Review | Emerged | Essay-derived attributes; text() descriptor, structure/shard/wedge, enriched personas |
| WP5 | In Review | Yes | Marimo notebook; 9-cell narrative arc |
| WP6 | In Progress | Yes | CI/CD + Pages deploy + documentation reconciliation |

## Emerged Work Packages

Three work packages were not in the original plan but emerged during development:

**WP2.5 — Downstream Alignment.** After reviewing the OWL/SHACL core (WP1+WP2), the Python API stubs needed synchronization with design decisions (Element hierarchy, Complex container, slice rule). This was the first sign of the iterative refinement pattern.

**WP2.8 — Abstraction Boundary.** Clarifying the core ↔ model family boundary required resolving three design issues and documenting vocabulary tiers. This produced the SKOS deferred issue.

**WP4.5 — Essay-Derived Attributes.** Extracting semantic content from the reference essay ("The MTG Color Wheel") motivated the `text()` descriptor framework and the terminology update from `pattern/ooa/oaa` to `structure/shard/wedge`. This was the richest emerged work package — it validated the 2×2 architecture by exposing the shared-domain problem (DD6).

## Hypothesis Test Results

All six criteria from `docs/ROADMAP.md` are covered by tests (203 passed, 5 skipped):

| ID | Criterion | Result | Key Evidence |
|----|-----------|--------|-------------|
| H1 | 2×2 coverage | Pass | `test_two_by_two_coverage.py` — all four cells populated |
| H2 | Topological limit documented | Pass | `test_hypothesis_criteria.py` — FaceShape sh:sparql constraint rejects open triangle |
| H3 | Single-call invariant | Pass | `test_hypothesis_criteria.py` — add_edge_type and promote both change OWL+SHACL |
| H4 | Verification works | Pass | `test_hypothesis_criteria.py` — SHACL catches malformed face |
| H5 | Discovery works | Pass | `test_hypothesis_criteria.py` + `test_mtg_demo.py` — SPARQL classifies 5 shards + 5 wedges |
| H6 | API opacity | Pass | `test_hypothesis_criteria.py` + `test_abstraction_boundary.py` — no rdflib in demo/notebook |

## Conventions

- **Status values:** Not Started | In Progress | In Review | Accepted
- **Changelog format:** Each WP file has a table recording date, request, and resolution
- **Requirement tracing:** Tests reference REQ-* identifiers from `docs/REQUIREMENTS.md`
- **Hypothesis tracing:** Tests reference H1-H6 criteria from `docs/ROADMAP.md`

## Observation

The project followed the planned sequence (WP0 → WP1+WP2 → WP3 → WP4 → WP5 → WP6) but accumulated three interstitial work packages that deepened the design. Each emerged at a review gate where downstream consequences of design decisions became visible. This iterative refinement pattern — complete a gate, align stubs, clarify boundaries, enrich content — was not planned but proved productive.
