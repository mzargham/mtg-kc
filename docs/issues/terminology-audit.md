# Terminology Audit

## Status: Active — local to this repo (MTG domain terminology)

## Canonical Terms

| Canonical | Deprecated | Context |
|-----------|-----------|---------|
| color wheel | color pentagon | Compound noun for the MTG 5-color structure. Matches blog title "The MTG Color Wheel (& Humanity)". |
| structure | pattern | The attribute classifying ColorTriple faces. |
| shard | ooa | A face with 2 adjacent + 1 opposite edge (3 consecutive colors). |
| wedge | oaa | A face with 1 adjacent + 2 opposite edges (non-consecutive center color). |
| Magic: The Gathering | Magic the Gathering | Full game title with colon and capitalized "The". |

## Acceptable Exceptions

- **Test fixtures** (`tests/test_knowledge_complex.py`, `tests/test_schema_builder.py`, etc.) may use `pattern`/`ooa`/`oaa` as arbitrary vocab values for framework API testing. These are not MTG domain references.
- **Quoted reference material** (`references/the-mtg-color-wheel.md`) preserves the original author's exact text.
- **Geometric descriptions** may say "pentagon" when referring to the literal geometric shape (e.g., "the five colors form a pentagon graph"), as long as it is not used as a compound noun ("color pentagon").

## Regression Check

```bash
# Should return zero results (excluding this file):
grep -ri "color pentagon" --include="*.py" --include="*.md" --include="*.sparql" | grep -v terminology-audit.md

# Should only match test fixtures and this file:
grep -rn "ooa\|oaa" --include="*.py" --include="*.md" --include="*.sparql" | grep -v terminology-audit.md | grep -v test_knowledge_complex | grep -v test_schema_builder | grep -v test_knowledge_complex_contract
```
