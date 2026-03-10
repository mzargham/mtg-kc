# Worklog Conventions

This directory tracks the phased execution of the mtg-kc project. Each work package (WP) has its own file.

## Rules for Claude

1. **One WP at a time.** Never begin work on the next WP until the current one has Status: Accepted.
2. **Update the worklog after every change.** When you complete a piece of work or the user requests a change, add an entry to that WP's Changelog table.
3. **Reference requirements and hypotheses.** Use REQ-* identifiers (from docs/REQUIREMENTS.md) and H1-H6 hypothesis criteria (from docs/PLAN.md) when describing quality criteria and changelog entries.
4. **Keep entries factual and concise.** State what changed and why. No filler.
5. **Status values:** Not Started | In Progress | In Review | Accepted
6. **Changelog format:** Each row records the date, what the user requested (or what was found during verification), and how it was resolved.

## Execution Sequence

```text
WP0 (repo reorg)
  → [REVIEW]
WP1+WP2 (OWL + SHACL core review)
  → [REVIEW]
WP3 (Python API)
  → [REVIEW]
WP4 (demo instance)
  → [REVIEW]
WP5 (Marimo notebook)
  → [REVIEW]
WP6 (CI/CD + GitHub Pages)
  → [REVIEW]
```

## File Template

Every WP file follows this structure:

- **Status** — current phase
- **Scope** — what this WP delivers, which files, which requirements
- **Quality Criteria** — what the user validates before acceptance
- **Verification** — commands to run, expected results
- **Changelog** — iteration history table
