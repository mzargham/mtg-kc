# WP6 — CI/CD + GitHub Pages + Repo Finalization

## Status: In Progress

## Scope

### A. CI/CD & Deployment

Set up GitHub Actions for continuous deployment of the Marimo notebook to GitHub Pages. Pattern mirrors `mzargham/hc-marimo`.

**Create `.github/workflows/deploy.yml`:**

- Trigger: push to `main` + `workflow_dispatch`
- Test job: `pytest tests/ -v` as gate before build
- Build job: checkout, install uv, export notebook as HTML-WASM, upload artifact
- Deploy job: deploy artifact to GitHub Pages
- Concurrency: group `pages`, cancel-in-progress false

**User manual step on GitHub:**

1. Go to repository Settings > Pages
2. Under "Build and deployment", set Source to **"GitHub Actions"**
3. Save — the workflow handles everything else

### B. Documentation Reconciliation

Reconcile primary docs with the actual codebase. The implementation is ahead of documentation in several areas.

**PLAN.md → ROADMAP.md:**
- Replace the original WP0–WP6 plan with a forward-looking roadmap
- Make a worklog directory README.md that preserves the plan data and compares it to what actually happened
- Completed work: summarized from worklogs
- Open work: links to `docs/issues/`
- Hypothesis test results: which criteria were validated

**ARCHITECTURE.md updates:**
- Add DD6: shared-domain removal (`_set_owl_domain()` — OWL inference vs. SHACL constraint semantics)
- Update Vocabulary Tiers examples to include `structure`/`shard`/`wedge`, `goal`, `method`, `guild`, `theme`, `clan`
- Document `text()` vs. `vocab()` distinction in the ontological layer
- Fix `pattern`/`ooa`/`oaa` references → `structure`/`shard`/`wedge`

**REQUIREMENTS.md updates:**
- Add REQ-SCHEMA-10: `text()` descriptor for free-text attributes
- Add REQ-SCHEMA-11: `export()` / `load()` model serialization (WP3.5)
- Update REQ-DEMO-05/06 terminology: `pattern` → `structure`, `ooa`/`oaa` → `shard`/`wedge`
- Add requirements for enriched schema attributes (WP4.5)

**README.md:**
- Update usage sketch to show enriched schema (text attributes, vocab attributes)
- Add WotC trademark disclosure (already done on main)

**demo/demo.py:**
- Fix stale `pattern`/`ooa`/`oaa` references → `structure`/`shard`/`wedge`

### C. Stale Reference Cleanup

Grep and fix all remaining `pattern`/`ooa`/`oaa` references across docs and demo:
- `docs/PLAN.md` (or its replacement)
- `docs/ARCHITECTURE.md`
- `demo/demo.py`

## Quality Criteria (human review)

### CI/CD
- [ ] Is deploy-on-push-to-main the workflow you want? (vs. manual-only, or tag-based releases)
- [ ] Should pytest run as a gate before deploy, or is that overkill for this project?
- [ ] Is the notebook the right thing to publish to Pages, or should it be something else?
- [ ] Is `--mode run` (read-only interactive) the right mode, or do you want `--mode edit`?

### Documentation
- [ ] Does the roadmap accurately reflect where the project is and where it's headed?
- [ ] Does ARCHITECTURE.md now reflect the actual system, including DD6 and text()?
- [ ] Does REQUIREMENTS.md cover all implemented features?
- [ ] Is any stale terminology (pattern/ooa/oaa) still present?

## Verification (machine — Claude runs these)

```bash
# Local smoke test of the export command
uv run marimo export html-wasm demo/demo.py -o _site/index.html --mode run

# After push: check workflow status
gh run list --workflow=deploy.yml --limit=1

# After deploy: check pages
gh api repos/mzargham/mtg-kc/pages

# Stale terminology check
grep -r "ooa\|oaa" docs/ demo/demo.py --include="*.md" --include="*.py"
# Expected: no matches (only in references/ and models/mtg/queries/)

# All tests pass
uv run pytest tests/ -v
```

Expected: workflow green, pages live at `https://mzargham.github.io/mtg-kc/`, no stale terminology.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
| 2026-03-10 | CI/CD workflow | Created `.github/workflows/deploy.yml` with pytest gate + HTML-WASM export + Pages deploy. Branch `wp6-ci-deploy`. |
| 2026-03-10 | GitHub Pages source | User set Pages source to "GitHub Actions" in repo settings. Confirmed via `gh api`. |
| 2026-03-10 | Expand WP6 scope to include repo finalization | Added Section B (doc reconciliation) and Section C (stale reference cleanup). PLAN.md → ROADMAP.md. ARCHITECTURE.md, REQUIREMENTS.md, README.md updates queued. |
| 2026-03-10 | Human review gate for deployment | Added `_review/approved.sha` check to `deploy.yml`. Created top-level `CLAUDE.md`. Updated `README.md` with deployment section. |
| 2026-03-10 | Terminology: color pentagon → color wheel | 11 occurrences across README, demo, tests, docs, worklog. Created `docs/issues/terminology-audit.md`. |
| 2026-03-10 | Terminology: ooa/oaa → shard/wedge in docs | PLAN.md, REQUIREMENTS.md, ARCHITECTURE.md, SPARQL query, test comments, graph.py docstring. Test fixtures unchanged. |
| 2026-03-10 | Doc freshness: ARCHITECTURE.md | Added DD6 (shared-domain), DD7 (text vs vocab), updated Vocabulary Tiers, fixed DD1 and 2×2 table. |
| 2026-03-10 | Doc freshness: REQUIREMENTS.md | Added REQ-SCHEMA-10/11/12, REQ-GRAPH-10/11. Updated REQ-DEMO-05/06. |
| 2026-03-10 | Doc freshness: README.md | Updated usage sketch with enriched schema (text/vocab attributes). |
| 2026-03-10 | PLAN.md → ROADMAP.md | Created `docs/ROADMAP.md` (completed work summary, open issues, hypothesis criteria, terminology). Added historical note to PLAN.md header. Created `worklog/README.md` (plan vs. actuals). |
