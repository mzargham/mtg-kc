# WP6 — CI/CD + GitHub Pages Deployment

## Status: Not Started

## Scope

Set up GitHub Actions for continuous deployment of the Marimo notebook to GitHub Pages. Pattern mirrors `mzargham/hc-marimo`.

**Create `.github/workflows/deploy.yml`:**

- Trigger: push to `main` + `workflow_dispatch`
- Build job: checkout, install uv, export notebook as HTML-WASM, upload artifact
- Deploy job: deploy artifact to GitHub Pages
- Concurrency: group `pages`, cancel-in-progress false

**Optional: CI test job** running `pytest` before the deploy step.

**User manual step on GitHub:**

1. Go to repository Settings > Pages
2. Under "Build and deployment", set Source to **"GitHub Actions"**
3. Save — the workflow handles everything else

## Quality Criteria

- [ ] `.github/workflows/deploy.yml` exists and follows the hc-marimo pattern
- [ ] Workflow triggers on push to main
- [ ] `marimo export html-wasm demo/demo.py` runs successfully in CI
- [ ] Notebook is accessible at `https://mzargham.github.io/mtg-kc/`
- [ ] (Optional) pytest runs as a prerequisite to deploy

## Verification

```bash
# Local smoke test of the export command
uv run marimo export html-wasm demo/demo.py -o _site/index.html --mode run

# After push: check workflow status
gh run list --workflow=deploy.yml --limit=1

# After deploy: check pages
gh api repos/mzargham/mtg-kc/pages
```

Expected: workflow green, pages live.

## Changelog

| Date | Change Requested | Resolution |
|------|-----------------|------------|
