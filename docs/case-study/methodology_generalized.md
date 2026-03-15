# Generalized Methodology: KC Personality Analysis with Three Codings

*This document specifies a general-purpose analytical methodology for KC personality analysis. It assumes the extended ontology proposed in `learnings_framework.md` — specifically the Expression vertex type, Color-Expression attitude edges, (Color, Color, Expression) faces, and persistence/visibility properties on Expression vertices. It does not assume a specific subject or domain; the MTG color frame is the analytical vocabulary but the methodology applies wherever that vocabulary is deployed.*

---

## 1. Purpose and Framing

The primary use case for KC personality analysis is understanding how a person tends to behave in collaborative contexts — in joint action with others, in shared expressions, in the give-and-take of working together. This is a more specific target than "what kind of person is this" and a more tractable one: behavioral tendencies in collaboration leave observable traces in ways that inner motivational states often do not.

The central problem is that the evidence used to analyze a person — what they publish, how they describe themselves, what others report about them — does not uniformly reflect the phenomenon of interest. A person's publicly documented output may reflect their aspirational self-concept, or their institutional role, or a deliberate persona construction, or their actual collaborative tendencies — and there is no guarantee these are the same.

The three-coding framework addresses this directly. Rather than collapsing all available evidence into a single color signature, it asks: what is this person like in each of three distinct modes? And critically: how do those modes differ? The gaps between codings are often more informative than any single coding.

---

## 2. Prerequisites: The Extended Ontology

This methodology requires the extended KC ontology described in `learnings_framework.md` Section 4. The essential additions:

**Expression vertex type.** Expressions are modes of manifestation — activities, outputs, or channels through which color orientations become observable. Each Expression has:
- `persistence`: `ephemeral` | `persistent`
- `visibility`: `private` | `public-ish` | `overtly-public`

**Color-Expression attitude edges.** Each color vertex has a characteristic attitude toward each expression mode: `positive`, `neutral`, or `negative`. These encode which expression modes a given color tends to produce or seek.

**(Color, Color, Expression) faces.** Three-way simplices capturing the joint dynamic of two colors in a shared expression mode. The face's attributes describe what happens when those two colors co-participate in that kind of expression — whether they reinforce, complement, or tension each other.

**Self-identification claim.** A structured record of the subject's self-reported color signature, separate from the analyst's assessed scores.

Without these extensions, the methodology below degrades to the v1 approach (all evidence collapsed to a single scored ranking), which `case_study_mzargham_v2.md` showed to be systematically biased.

---

## 3. The Three Codings

The methodology produces three distinct color signature assessments of the same subject, each targeting a different phenomenon. They are not redundant; they are measurements of three genuinely different things.

### 3.1 Aspirational Coding

**What it captures:** The color signature the subject privately identifies with or is working toward — who they want to be, what orientations they value, what version of themselves they hold as an internal ideal.

**Why it matters:** Aspirational self-concept shapes motivation and direction. It is the compass, not the location. It often aligns with what a person believes are their best qualities, which may or may not be borne out in actual behavior with others. Understanding aspiration is useful context for the relational coding — it tells you what direction the person is trying to move.

**Evidence basis:** Tier 1 dominant. Self-identification claims are the clearest signal. Explicit statements about values, ideals, and role models are supporting evidence. Tier 2 evidence that reflects deliberate self-cultivation (what a person does privately, what they study, what they practice for its own sake) is also relevant.

**Expression filter:** Focus on expressions with `visibility: private` and the subject's own self-reported orientation. `SelfReport`, `InternalMotivation`, private creative or intellectual practice.

**Key limitation:** The subject controls the evidence. Aspirational self-report may reflect the ideal self more than the actual self. Self-identification is evidence of orientation, not proof of it. This coding requires Tier 1 access and is therefore unavailable in purely external analyses.

**Relationship to self-ID gap:** The aspirational coding is where the self-ID claim anchors. If the self-ID diverges from the public persona coding, the aspiration coding helps adjudicate: is the self-ID pointing at something real in the private/internal evidence, or does it appear genuinely aspirational even there?

### 3.2 Persona Coding

**What it captures:** The color signature the world perceives — what is legible to external observers from the most visible, persistent evidence. This is the public record: publications, institutional affiliations, professional reputation, stated positions, documented organizational behavior.

**Why it matters:** The persona is how a person is pre-understood before any direct interaction. It shapes expectations, reputation, and how collaborators approach them. It is also the starting point for any analyst who lacks direct access to the subject. Understanding where the persona is accurate and where it diverges from actual collaborative tendencies is directly useful for collaboration.

**Evidence basis:** Tier 3 dominant. The persona coding is what a diligent web researcher would construct. High-discoverability, high-legibility sources: academic papers, professional profiles, LinkedIn, GitHub, organizational roles, public statements.

**Expression filter:** Focus on expressions with `visibility: overtly-public` and `persistence: persistent`. `AcademicPublication`, `InstitutionalCharter`, `DocumentedFramework`, `ProfessionalProfile`.

**Key limitation:** High-legibility colors (Blue, White) are systematically over-represented; low-legibility colors (Red, Black) are systematically under-represented. The persona coding should always carry an explicit note about which colors are likely undercounted given their Tier 3 legibility profiles. Do not treat the persona coding as the primary finding.

**Structural bias in the persona coding:** The Color-Expression attitude edges in the extended ontology can be used to compute, for any proposed persona signature, the expected Tier 3 evidence density. If a proposed persona includes strong Red, the analyst should ask: where is the Tier 3 evidence for Red-favored expressions? Its absence is informative — either Red is truly absent (persona is accurate), or Red's low-legibility expressions simply don't appear in Tier 3 (persona is biased).

### 3.3 Relational Coding

**What it captures:** The color signature that manifests in actual joint activity with others — how the subject tends to show up when co-participating in expressions. This is the primary phenomenon of interest for understanding collaboration.

**Why it matters:** Interpersonal dynamics are constituted in joint action. What someone aspires to be (privately) and what is broadly legible about them (publicly) may both diverge, in different ways, from how they actually behave when doing things together with other people. A collaborator's relational coding is what you need to know before working with them — not their persona, and not their private aspirations.

**Evidence basis:** Tier 2 most productive. The relational coding requires evidence of *joint* activity: how the subject participates in shared endeavors, what roles they take in collaborative settings, what others who have worked alongside them report. Community participation records, co-authored work, accounts from collaborators, participation in shared events. Tier 1 (subject self-report on collaborative tendencies) is valuable but subject to the aspirational conflation problem — people often describe how they *want* to collaborate rather than how they *do*.

**Expression filter:** Focus on expressions that are inherently joint — ones that require other people. `CommunityMembership`, `LiveExperiment`, `CompetitiveAthletics` (team sport), `ArtParticipation` (collaborative production), `ClientDeliverable` (in the context of team structure). The relational coding is blind to private solo expressions and is skeptical of purely public broadcast expressions (publications, talks) where no actual back-and-forth occurs.

**Key limitation:** The hardest coding to construct. Tier 2 participatory evidence is low-discoverability by definition. It requires domain knowledge to locate (knowing what communities to look in, knowing who the collaborators are). The relational coding therefore benefits most from the human curation that the 3-tier model identifies as essential.

**Why this is the primary phenomenon:** The aspiration and persona codings describe the subject in relation to themselves and to the world at large. The relational coding describes the subject in relation to *specific others* in *specific shared contexts*. For most practical applications — team formation, collaboration, mentorship, institutional design — the relational coding is the most predictively useful. It is also the coding that most directly reveals the Color-Color-Expression dynamic: what happens when this person's orientations meet other people's orientations in a shared expression.

---

## 4. The Expression Framework as Connective Tissue

The three codings are unified by the Expression framework. Each coding is not a different color assessment of the same undifferentiated evidence — it is an assessment over a *different subset of expressions*, filtered by visibility and participation type.

| Coding | Expression visibility filter | Expression participation filter | Evidence tier |
|--------|------------------------------|--------------------------------|---------------|
| Aspirational | private | solo (self-directed) | Tier 1 dominant |
| Persona | overtly-public | broadcast (solo → world) | Tier 3 dominant |
| Relational | public-ish + private | joint (with others) | Tier 2 dominant |

This table makes visible why the three codings can legitimately differ: they are not measuring the same thing with different instruments. They are measuring three genuinely different behavioral modes, each of which activates a different subset of expressions.

The Color-Expression attitude edges predict which colors should be prominent in each coding. A highly Blue subject should show up strongly in the persona coding (Blue generates high-legibility, persistent expressions) but may or may not show up equally in the relational coding (Blue may become less dominant when the task is joint and embodied rather than analytical and documented). A highly Red subject should show up weakly in the persona coding but may show up strongly in the relational coding if they are animated and present in shared activity.

The (Color, Color, Expression) faces are particularly valuable for the relational coding. When two people with different color signatures co-participate in a shared expression, the face that describes their color combination and that expression type predicts the quality and character of the interaction. A (Blue, Red, LiveExperiment) face predicts a specific kind of productive tension in collaborative hacker events. A (Green, White, CommunityMembership) face predicts a different kind of cooperative, norm-respecting communal participation.

---

## 5. Methodology Steps

### Step 1: Establish the Expression vocabulary

Before scoring, define which expressions are relevant to the subject and context of analysis. Not every possible expression is relevant to every subject. The vocabulary should:
- Cover the expression modes that are actually present in the evidence base
- Include at least one expression from each visibility tier (private, public-ish, overtly-public)
- Flag which expressions are joint (relevant for relational coding) vs. solo

This is a domain-specific curation step. For a public intellectual, the vocabulary might center on `DocumentedFramework`, `AcademicPublication`, `Seminar`, `OpenSourceProject`, `MentorshipRelation`. For an athlete-activist, it might center on `CompetitiveAthletics`, `CommunityGovernance`, `PublicAdvocacy`, `CoachingRelation`.

### Step 2: Gather evidence across all three tiers

For each tier:
- **Tier 1:** Subject self-report, self-identification claims, guided introspection, private testimony. Note: Tier 1 is only available with subject cooperation.
- **Tier 2:** Low-discoverability public records. Requires domain knowledge and active curation: community archives, participatory event records, collaborative outputs, accounts from close collaborators.
- **Tier 3:** Standard discoverable public evidence. Web search, academic databases, professional profiles, public repositories.

Tag each piece of evidence with its tier and with the expression(s) it bears on.

### Step 3: Produce three independent scored assessments

Score the 25-element simplicial complex three times, once per coding:

- **Aspirational scoring:** Weight Tier 1 evidence heavily; filter to private/solo expressions; include self-identification claims; discount Tier 3 evidence as unreliable for aspirational content.
- **Persona scoring:** Weight Tier 3 evidence heavily; filter to overtly-public/persistent expressions; apply upward corrections for colors with known low Tier 3 legibility (Red, Black) where Tier 1/2 evidence confirms their presence.
- **Relational scoring:** Weight Tier 2 evidence; filter to joint expressions; discount both private solo evidence (aspiration) and public broadcast evidence (persona); include collaborator accounts if available.

Each scoring produces a ranked table of all 25 simplices with scores and an evidence basis note.

### Step 4: Identify the primary signatures per coding

For each coding, identify the top 3 simplices as the primary signature. Note which layer they occupy (vertex, edge, face): a primary signature at the edge layer indicates a person defined by tension; at the face layer, by emergence; at the vertex layer, by purity.

Also note which simplices score significantly *differently* across the three codings — these are the analytically interesting cases.

### Step 5: Gap analysis

Compare the three primary signatures and produce a structured gap analysis:

**Aspiration-Persona gap.** Where does the aspirational coding diverge from the persona? Directions:
- *Aspiration exceeds persona:* The subject privately identifies with orientations that are not legible in their public output. May indicate: under-developed expression of those orientations, deliberate privacy, or genuinely aspirational (not yet realized).
- *Persona exceeds aspiration:* The public record over-represents certain orientations relative to the private self-concept. May indicate: role demands, institutional capture, or effective performance of an identity the subject doesn't fully endorse internally.

**Persona-Relational gap.** Where does the relational coding diverge from the persona? This is the gap most relevant to collaborators:
- *Relational exceeds persona in a color:* The subject is more of a given color in actual joint activity than their public record suggests. Positive surprise territory for collaborators.
- *Persona exceeds relational in a color:* The subject's public identity as a given color is not fully realized in actual collaboration. May indicate: public persona is a performance, or the expression modes favored by that color are solo rather than joint.

**Aspiration-Relational gap.** The gap between what the subject is trying to be and how they actually show up with others. This is the most personal and often most developmentally significant gap:
- *Aspiration exceeds relational in a color:* The subject values an orientation they have not yet integrated into their collaborative behavior. Possible growth edge.
- *Relational exceeds aspiration in a color:* The subject naturally expresses an orientation in collaboration that they don't fully own privately. May indicate unacknowledged strengths.

### Step 6: Primary report

The primary report foregrounds the **relational coding** as the main finding. Aspiration and persona codings are framed as interpretive context: they explain where the relational signature comes from and where it might go.

Structure:
1. Relational signature (primary): top 3 simplices, evidence basis, confidence level
2. Aspiration-Relational gap commentary: what does the subject aspire to that doesn't yet fully show up in joint activity?
3. Persona-Relational gap commentary: where does the collaborator's experience likely diverge from the public reputation?
4. Synthesis: a characterization of how this person tends to show up in joint work — what they bring, what tensions they create or hold, what expressions they tend to activate

---

## 6. Interpreting the Gaps

### When gaps are small

If all three codings are similar, the subject has high consistency across modes: they aspire to what they express publicly, and they enact it in collaboration. This is the "authentic public figure" profile. It is a meaningful finding — it means the persona coding is relatively trustworthy as a proxy for the relational coding.

Note: This is the condition that makes Tier 3 analysis viable for quick assessments. It should not be assumed; it should be confirmed via the three-coding comparison.

### When the aspiration-persona gap is large

The subject presents publicly in ways that diverge from their private self-concept. This is common among people in institutional roles that require a specific persona (the "organizational representative" profile) or people who are strategically managing their public image. It can also indicate a subject in transition — moving from one self-concept to another.

Caution: This gap is hard to assess without Tier 1 access. Without the subject's cooperation, the aspirational coding cannot be reliably constructed, and this gap cannot be measured.

### When the persona-relational gap is large

This is the most directly useful finding for collaboration. The subject is significantly different to work with than their public record suggests. Two common patterns:

- **High Blue persona, lower Blue relational:** Common in practitioners whose documented output (papers, frameworks, formal systems) suggests deep analytical rigor, but whose collaborative mode is warmer, more improvisational, and more Green or Red than the documentation implies. The written output reflects a style that doesn't fully transfer to real-time joint work.
- **High Red/Green relational, lower in persona:** Common in people who are deeply present and alive in shared activity but whose public record is sparse (low-legibility expression modes). A community organizer, a coach, a great collaborator who leaves few written traces.

### When the aspiration-relational gap is large

The subject has a gap between intention and enactment in collaborative contexts. Two interpretations:

- *Developmental gap:* The aspirational orientation is real but not yet expressed in behavior with others. The subject is growing toward it. This is positive if the aspiration is healthy.
- *Conflict gap:* The aspiration is not being enacted because something in the collaborative context suppresses it (institutional norms, role demands, social pressures). The subject may be more themselves in solo or private contexts than in collaboration.

---

## 7. Confidence and Evidence Quality

Every coding should carry an explicit confidence assessment: high, medium, or low.

**Confidence is determined by:**

1. **Tier coverage:** How many tiers of evidence are present? A coding built on Tier 3 only is low confidence for Red and Black, regardless of what the scores say. A coding with Tier 1 evidence is higher confidence for the aspirational coding.

2. **Expression coverage:** Are the relevant expressions well-evidenced? A relational coding with only one joint expression in the evidence base is thin.

3. **Color legibility calibration:** Apply the Color-Expression attitude edges to identify which colors in the proposed signature have positive attitudes toward the expression modes in evidence. For those colors, evidence is more reliable. For colors whose favored expressions are absent from the evidence base, the score is soft.

4. **Internal consistency:** Does the signature make sense as a whole? Do the at_best and at_worst attributes land? Misfiring shadows are a signal of low fit, not just a nice-to-have.

A low-confidence coding should be reported as a hypothesis, not a finding.

---

## 8. Relationship to the Zargham Case Study

The Zargham case study (`case_study_mzargham_v2.md`) implicitly performed a version of this methodology but without the formal three-coding structure. Several of the case study's key findings map cleanly onto the three-coding framework:

- The Temur self-ID is the aspirational coding signal — and it turned out to be confirmed by Tier 2 evidence, not merely aspirational.
- The v1 Tier-3-only analysis produced a reasonably reliable persona coding (Bant/WUG).
- The revised conclusion — "Bant in institutional output, Temur in embodied/experimental life" — is a proto-relational coding: it identifies that the joint-expression modes (athletics, hacker labs, art collaboration) activate a different signature than the solo-publication modes.

What the Zargham case study did not do, and what this methodology would now enable, is produce a proper relational coding sourced from collaborator accounts and participatory Tier 2 records. That coding remains to be done. The existing evidence supports inference about the relational mode, but direct evidence of how Zargham behaves in actual joint work — from people who have worked alongside him — would substantially strengthen or revise the picture.

This is the natural next analytical step for that case study: gather relational-tier evidence (accounts from collaborators, joint project records, community participation observation) and compare it to the persona coding already established.

---

## 9. Summary: The Methodology in Brief

1. **Define the Expression vocabulary** for the subject and context.
2. **Gather evidence** across all three tiers, tagged by tier and expression.
3. **Score three times:** aspirational (Tier 1, private/solo), persona (Tier 3, public/persistent), relational (Tier 2, joint).
4. **Identify primary signatures** for each coding (top 3 simplices, layer, confidence).
5. **Gap analysis:** aspiration-persona, persona-relational, aspiration-relational.
6. **Primary report:** foreground the relational coding; contextualize with the other two.
7. **Confidence assessment:** per coding, per color, citing evidence tier and expression coverage.

The relational coding is the primary phenomenon. The persona coding is the starting point (most accessible). The aspirational coding is the interpretive context (least accessible, most private). The three together produce an account that is neither naive (treating the public record as the whole truth) nor solipsistic (treating self-report as the whole truth).

---

*This methodology extends the KC analytical framework documented in `kc/resources/kc_core.ttl` and `models/mtg/schema.py`. It assumes the Expression vertex type and associated edges and faces proposed in `learnings_framework.md`. Prior case study materials: `docs/case-study/`.*
