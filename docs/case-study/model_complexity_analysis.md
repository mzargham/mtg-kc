# Model Complexity and Fitness for Purpose: A KC Composability Analysis

*This document examines whether the three analytical codings introduced in `methodology_generalized.md` — aspirational, persona, and relational — should be formalized as a vertex type in the KC ontology, enabling (Color, Expression, Phenomena) triples. The answer is: not yet, and possibly not ever — but the reasoning matters more than the verdict. The MTG psychometric stack serves as a concrete case study in how KC supports principled choices about model complexity within a single modeling domain.*

---

## 1. The Composability Thesis

The KC framework is explicitly layered: a generic topological core (`kc_core.ttl`) sits beneath domain-specific models, which sit beneath concrete instances. This separation is a design feature, not an incidental consequence of how the code is organized. It means each layer can be independently authored, validated, extended, or replaced. It also means there is no single "right" level of complexity — the appropriate layer to inhabit depends on what you are trying to do.

Within a single modeling domain, this layering supports incremental extension. You do not have to commit to the full model upfront; you can add structure as the need is demonstrated. The MTG psychometric application illustrates this with a three-step stack:

| Model | New elements | Core capability unlocked |
|-------|-------------|--------------------------|
| **MTG** | 5 Color vertices, 10 edges, 10 faces | Color signature analysis from Tier 3 evidence |
| **MTGExp** | Expression vertex type; Color-Expression edges; (Color, Color, Expression) faces | Formal observability reasoning; Tier 2 evidence targeting |
| **MTGExpPhen** | Phenomena vertex type; (Color, Expression, Phenomena) triples | Analytical codings as first-class model objects |

Each row is a valid stopping point. The question this document addresses is: which stopping point is appropriate, and why?

---

## 2. The Extension Criterion

A model extension is justified when all four of the following hold:

1. **Domain concept test:** The new element describes something in the *world being modeled*, not something in the *analysis process*. Mixing object-level and methodology-level concepts in the ontology produces models that are harder to use and easier to misread.

2. **Query test:** The extension enables queries or validations that are impossible or materially awkward without it — and those queries are ones we actually want to ask.

3. **Complexity test:** The cost of the extension (new types, new constraints, new toolchain surface) is proportionate to the new capability.

4. **Evidence test:** There is sufficient evidence that this is the right design — ideally from multiple cases, not just one.

Applying this criterion to each proposed layer:

---

## 3. MTG — The Base Layer

**What it represents.** Five Color vertices, each with a philosophical orientation defined by `goal`, `method`, `persona`, `at_best`, `at_worst`, and `example_behaviors`. Ten edges capturing pairwise tensions and synergies, each with a `theme`. Ten faces capturing three-way dynamics, each classified as `shard` or `wedge`. The full 25-element simplicial complex over the color set.

**Domain concept test: pass.** The colors, their tensions, and their emergent three-way dynamics are concepts from the MTG domain, applied to personality as an interpretive frame. They describe something about the phenomena of interest — human orientations and how they interact — not about how the analyst does their job.

**Fitness for purpose.** MTG is the right model for a first-pass analysis grounded in Tier 3 evidence, or for conversations where the goal is interpretive vocabulary rather than formal inference. The Zargham v1 analysis (`case_study_mzargham.md`) used MTG and produced a coherent, discriminating result. The model was fit for that purpose.

**Where it falls short.** MTG has no formal way to reason about evidence quality, expression modes, or which colors are likely to be over- or under-represented in any evidence base. The v1 analysis discovered this empirically: Red was systematically undercounted because the model gave no guidance about which colors leave Tier 3 traces and which do not. That gap is real and addressable — but it does not require adding Phenomena. It requires adding Expressions.

---

## 4. MTGExp — The First Extension

**What it adds.** Expression as a vertex type, with `persistence` (`ephemeral` | `persistent`) and `visibility` (`private` | `public-ish` | `overtly-public`) properties. Color-Expression attitude edges (`positive`, `neutral`, `negative`). (Color, Color, Expression) faces capturing the joint dynamic of two colors in a shared expression mode.

**Domain concept test: pass.** Expressions exist in the world independently of the analysis. The distinction between a published paper and a live hacker event is a fact about those activities — their persistence and visibility are measurable properties, not analytical constructs. The attitude a color has toward an expression mode is a claim about the domain (Blue produces documentation; Red lives in the moment and does not) that is grounded in the MTG source material and confirmed by the case study evidence. These are not N=1 findings.

**Query test: pass.** MTGExp enables formally querying: given a proposed color signature, which expression modes are expected? Which of those are high-legibility? Where should an analyst look for Tier 2 evidence? This transforms the color observability fingerprints — which in v2 of the case study had to be carried as analyst knowledge — into model-level properties that can be queried and validated. Observability becomes a first-class concern of the model, not a footnote in the methodology.

**Complexity test: pass.** MTGExp adds one new vertex type and new edges and faces of the same structural kinds already present in MTG. The SHACL shape machinery extends naturally. The KC framework's DSL (`SchemaBuilder`) accommodates the new type within the existing `vocab()` and `text()` attribute system. No new topological concepts are required — the simplicial complex structure already handles mixed-type vertices.

**Evidence test: adequate.** The color observability fingerprints are stable properties of the color philosophies, not artifacts of a single case. That Blue generates documentation and Red does not is a claim that can be evaluated against the MTG source material directly, and that evaluation does not depend on Zargham. The MTGExp extension would be the same regardless of which subject is being analyzed.

**Verdict: justified.** MTGExp adds domain concepts that increase the model's expressiveness about the phenomena of interest — how color orientations manifest in the world and what evidence they leave — at a proportionate complexity cost, with adequate evidence.

---

## 5. MTGExpPhen — The Second Extension (Not Yet)

**What it would add.** Phenomena as a vertex type with values `{aspirational, persona, relational}`. (Color, Expression, Phenomena) triples — 3-simplices in which a Color vertex, an Expression vertex, and a Phenomena vertex jointly define a face. The attributes of such a face would describe the character of a given color, in a given expression mode, as observed through a given analytical coding.

**Domain concept test: fail.** This is the decisive objection. `{aspirational, persona, relational}` are not concepts about people, colors, or expressions. They are categories the analyst uses to organize their evidence-gathering process. "Aspirational" means: weight Tier 1 evidence, filter to private/solo expressions, emphasize self-identification. "Relational" means: weight Tier 2 evidence, filter to joint expressions, look for participatory records. These are instructions to the analyst, not facts about the world.

The test is this: does the concept describe something that would still be true if no analyst were involved? Expressions pass this test — a live hacker event is ephemeral and public-ish whether or not anyone is analyzing anyone. Colors pass it — Blue tends to document itself whether or not an analyst is watching. Phenomena do not pass it — "aspirational" only exists relative to an analytical act of coding evidence a certain way.

Adding Phenomena to the model conflates the object level (what is being modeled) with the methodology level (how the model is applied). This is a category error that produces models that are harder to interpret because they mix two different kinds of claims.

**Query test: inadequate return.** The queries MTGExpPhen would enable — "what is the aspirational expression of Blue in a LiveExperiment context?" — can already be answered by applying the methodology document to the model without Phenomena being formalized. The model does not need to represent the analysis process to support the analysis; the methodology document is the right place for that content.

**Complexity test: costly.** (Color, Expression, Phenomena) triples are 3-simplices — a new topological dimension that the current model does not use. The KC framework's core layer handles 2-simplices (faces over three vertices of the same type). Mixing vertex types across a 3-simplex requires either: extending the topological core, which changes the framework's guarantees; or treating the triple as a hyperedge outside the simplicial structure, which loses the structural machinery (SHACL validation, SPARQL templates). Either path has substantial cost.

**Evidence test: premature.** The three-coding framework (aspirational / persona / relational) was developed from a single self-assessment case study under ideal conditions. We do not know whether this tripartite structure is the right framework for subjects without Tier 1 access, or for domains other than psychometrics, or whether the boundary between the codings is stable. Encoding it as an ontological commitment now would lock in a design that has not been validated. If the framework turns out to need four codings, or two, or different names, the ontological version has to be redesigned; the methodology document can be revised without touching the model.

**Verdict: not yet.** The three-coding methodology is correctly located in `methodology_generalized.md`. It should remain there until: (a) it has been validated across multiple case studies, (b) there is a clear class of queries that requires formal model support rather than methodological application, and (c) the complexity cost of the 3-simplex extension is justified by that use case.

---

## 6. The Architectural Principle: KC Enables Principled Stopping

The KC framework's value is not only that it enables extensions. It is that it makes the choice to extend — or not extend — principled and articulable. The four-part criterion above (domain concept, query, complexity, evidence) is not specific to this case study; it is a general framework for evaluating any proposed extension to any KC-based model.

This is the composability/extensibility thesis applied *within* a single modeling domain at different levels of sophistication, not just across domains. MTG, MTGExp, and MTGExpPhen are three different answers to the question "how much structure do we need?" — and all three are legitimate answers depending on the purpose.

| Purpose | Right stopping point | Why |
|---------|---------------------|-----|
| Interpretive conversation, rapid first pass | MTG | Vocabulary is sufficient; formal inference is not the goal |
| Evidence-calibrated analysis with observability awareness | MTGExp | Domain concepts justify the extension; observability queries add real value |
| Formally queryable three-coding analysis | MTGExpPhen | *Not yet* — methodology-level concepts don't belong in the object model at N=1 |

The KC framework supports this table by providing: (1) clear layer separation so each level is independently usable; (2) a compositional design so MTGExp is a proper extension of MTG, not a replacement; and (3) enough formal machinery (OWL + SHACL + SPARQL) that "I want to query X" is a testable claim, not just an intuition.

---

## 7. What Belongs Where

The case study work to date has produced content at three distinct levels. Getting the placement right matters for maintainability and reuse:

| Concept | Correct location | Rationale |
|---------|-----------------|-----------|
| Color orientations, tensions, emergent dynamics | `models/mtg/` (MTG layer) | Domain concepts, stable across all applications |
| Expression modes; persistence; visibility | `models/mtgexp/` (MTGExp layer, future) | Domain concepts, stable |
| Color-Expression attitudes | `models/mtgexp/` (MTGExp layer, future) | Stable domain facts grounded in color philosophy |
| Aspirational / persona / relational codings | `docs/case-study/methodology_generalized.md` | Methodology-level categories; belong in the analyst's guide |
| Evidence tier classification (T1/T2/T3) | `docs/case-study/methodology_generalized.md` | Describes the analysis process, not the domain |
| Self-ID gap | Instance-level structured claim | Per-subject fact; not a model-level type |
| Observability fingerprint reasoning | MTGExp model (when built) | Once formalized, replaces the analyst-guidance version |

The three-coding framework is not a dead end — it is the right thing in the right place. A methodology document that an analyst applies to a model is not a lesser artifact than the model itself. It is a different kind of artifact that operates at a different layer, and the KC architecture makes that layer distinction explicit.

---

*This document addresses the design question raised at the end of `methodology_generalized.md`. It cites the full case study chain: `case_study_mzargham.md`, `case_study_mzargham_v2.md`, `feedback_observability.md`, `learnings_framework.md`, `methodology_generalized.md`. KC framework architecture: `docs/ARCHITECTURE.md`, `kc/resources/kc_core.ttl`.*
