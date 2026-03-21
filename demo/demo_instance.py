"""
demo/demo_instance.py

MTG color wheel knowledge complex — full instance construction.
Layer 3: concrete data built using the models.mtg schema (layer 2)
and the kc framework (layer 1).

Authored in WP4, enriched in WP4.5 with essay-derived attributes.
Returns a ready-to-use KnowledgeComplex for the Marimo notebook.

REQ-DEMO-01 through REQ-DEMO-05.
"""

from knowledgecomplex import SchemaBuilder, KnowledgeComplex
from models.mtg import build_mtg_schema, QUERIES_DIR


def build_mtg_instance(schema: SchemaBuilder | None = None) -> KnowledgeComplex:
    """Build the MTG color wheel instance.

    If no schema is provided, builds one from models.mtg.
    """
    if schema is None:
        schema = build_mtg_schema()

    kc = KnowledgeComplex(schema=schema, query_dirs=[QUERIES_DIR])

    # REQ-DEMO-01: 5 Color vertices
    kc.add_vertex("White", type="Color",
        goal="peace", method="order",
        persona="Believes the solution to suffering is coordination, cooperation, and rules. Values fairness, duty, and the greater good.",
        at_best="Compassionate leadership, principled sacrifice, building systems that protect the vulnerable.",
        at_worst="Rigid authoritarianism that cannot tolerate ambiguity, empty ritual, suffocating conformity.",
        example_behaviors=[
            "Creating fair rules and enforcing them consistently",
            "Sacrificing personal gain for the greater good",
            "Building institutions that protect the vulnerable",
        ],
    )
    kc.add_vertex("Blue", type="Color",
        goal="perfection", method="knowledge",
        persona="Believes things could be arbitrarily good if we could figure out the truth and apply it fully. Values clarity, rigor, and optimization.",
        at_best="Visionary insight, elegant invention, patient mastery of complex systems.",
        at_worst="Dismissive of what it cannot quantify, paralyzed by analysis, emotionally disconnected.",
        example_behaviors=[
            "Pursuing deep understanding before acting",
            "Designing elegant solutions to complex problems",
            "Optimizing systems through careful analysis",
        ],
    )
    kc.add_vertex("Black", type="Color",
        goal="satisfaction", method="ruthlessness",
        persona="Wants power and agency to act on its preferences, reshaping the world as it sees fit. Amoral rather than immoral — recognizes no limits except self-interest.",
        at_best="Decisive self-reliance, relentless excellence, unflinching honesty about incentives.",
        at_worst="Short-sighted transactionalism that drives away allies, consuming everything without sustainability.",
        example_behaviors=[
            "Pursuing personal goals with relentless determination",
            "Making hard choices others shy away from",
            "Being honest about self-interest and incentives",
        ],
    )
    kc.add_vertex("Red", type="Color",
        goal="freedom", method="action",
        persona="Wants to live in the moment and follow the thread of aliveness and passion. Values authenticity, courage, and emotional truth.",
        at_best="Fierce loyalty, joyful creation, courage to act when others hesitate.",
        at_worst="Restless impulsivity that cannot commit or tolerate stillness, flailing emotional volatility.",
        example_behaviors=[
            "Acting on passionate conviction without hesitation",
            "Expressing emotions openly and authentically",
            "Taking bold risks in pursuit of what matters",
        ],
    )
    kc.add_vertex("Green", type="Color",
        goal="harmony", method="acceptance",
        persona="Believes most suffering comes from trying to cast off one's natural role. Seeks harmony as distinct from order — embracing what is.",
        at_best="Grounded wisdom, patient strength, deep respect for interconnection and balance.",
        at_worst="Pathological passivity that surrenders to fate and sabotages others' attempts to improve things.",
        example_behaviors=[
            "Accepting circumstances and working within natural limits",
            "Respecting tradition and the wisdom of experience",
            "Finding strength in patience and rootedness",
        ],
    )

    # REQ-DEMO-02: 5 adjacent edges (pentagon neighbors: W-U-B-R-G-W)
    kc.add_edge("WU", type="ColorPair",
        vertices={"White", "Blue"}, disposition="adjacent",
        guild="azorius", theme="design",
        synergies="Both prize deliberation over impulse. White's commitment to order gives Blue's knowledge a stable institutional home; Blue's rigor gives White's rules an evidence-based foundation rather than mere tradition.",
        tensions="Blue revises any system when a better model emerges — White's attachment to established order resists revision for its own sake. White's collective concern can override individual epistemic merit; Blue's truth-seeking can override social consensus.",
        persona="Asks 'how do we know what's right and good?' Carefully defined, algorithmic heuristics for doing things better. Rationality techniques and effective altruism.",
        at_best="Thoughtful systems that genuinely improve outcomes, principled engineering of fairness.",
        at_worst="Bureaucratic paralysis, rules that serve themselves rather than their purpose.",
        example_behaviors=[
            "Designing systems with careful attention to fairness",
            "Applying rationality techniques to improve outcomes",
            "Building algorithmic heuristics for better decision-making",
        ],
    )
    kc.add_edge("UB", type="ColorPair",
        vertices={"Blue", "Black"}, disposition="adjacent",
        guild="dimir", theme="growth_mindset",
        synergies="Blue's mastery of knowledge gives Black's ambition a precision instrument. Black's willingness to discard sentiment clears the path for Blue's analytical conclusions to be applied without compromise.",
        tensions="Blue treats knowledge as an end in itself; Black treats it as a means to satisfaction. Black's impatience with prolonged analysis conflicts with Blue's need for thoroughness; Blue's search for objective truth conflicts with Black's fundamentally self-referential goal.",
        persona="Asks 'how can I best achieve my goals?' Enlightened self-interest. You are not defined by your origins or constrained to the role society has set.",
        at_best="Brilliant strategic thinking, self-made excellence, pragmatic intelligence.",
        at_worst="Arrogant manipulation, treating people as instruments, cold scheming.",
        example_behaviors=[
            "Pursuing self-improvement with strategic focus",
            "Refusing to accept inherited limitations",
            "Applying intelligence pragmatically toward goals",
        ],
    )
    kc.add_edge("BR", type="ColorPair",
        vertices={"Black", "Red"}, disposition="adjacent",
        guild="rakdos", theme="independence",
        synergies="Black's self-reliance and Red's freedom point toward the same target: autonomy from external obligation. Black provides the strategic clarity; Red provides the passionate will to act on it immediately.",
        tensions="Black plans; Red acts. Black's long-term self-interest can be derailed by Red's impulsive pursuit of immediate satisfaction. Red's emotional authenticity conflicts with Black's cold instrumental reasoning.",
        persona="Asks 'how do I get what I want?' Fosters and defends independence — red from freedom, black from self-reliance. Live and let live.",
        at_best="Unapologetic authenticity, liberation from soul-crushing obligation, fierce self-expression.",
        at_worst="Destructive hedonism, cruelty dressed up as honesty, chaos without purpose.",
        example_behaviors=[
            "Rejecting obligations that don't serve genuine needs",
            "Expressing desires without apology",
            "Defending personal independence fiercely",
        ],
    )
    kc.add_edge("RG", type="ColorPair",
        vertices={"Red", "Green"}, disposition="adjacent",
        guild="gruul", theme="authenticity",
        synergies="Red's freedom from narrative and Green's acceptance of what is converge on the same present-moment orientation. Neither is interested in abstract ideals — both trust immediate experience over constructed frameworks.",
        tensions="Red generates momentum and change; Green resists disrupting what has proven itself. Red's passion can be destructive; Green's acceptance can be passive. Red wants to break constraints; Green wants to work within natural ones.",
        persona="Asks 'where am I now, and where should I go?' Dionysian presence — setting aside narratives and frames and just being in the moment.",
        at_best="Visceral aliveness, grounded instinct, acting from genuine feeling rather than performance.",
        at_worst="Anti-intellectual rejection of all structure, inability to plan or cooperate.",
        example_behaviors=[
            "Acting from gut instinct rather than calculation",
            "Being fully present in the moment",
            "Rejecting artificial narratives about how things should be",
        ],
    )
    kc.add_edge("GW", type="ColorPair",
        vertices={"Green", "White"}, disposition="adjacent",
        guild="selesnya", theme="community",
        synergies="Green's embrace of natural interdependence and White's commitment to collective order reinforce each other — both believe the individual is fulfilled through proper relationship with the whole.",
        tensions="White's order is designed and enforced; Green's harmony is grown and accepted. White wants to build better systems; Green believes the best system is already present in nature. White can override what is for what ought to be; Green cannot.",
        persona="Asks 'what's fair and good? What is sustainable?' The whole can be greater than the sum of its parts. Sacrifice for things larger than oneself.",
        at_best="Compassionate institutions, sustainable cooperation, genuine service.",
        at_worst="Groupthink, martyrdom without purpose, smothering collectivism.",
        example_behaviors=[
            "Building sustainable communities through shared sacrifice",
            "Putting collective wellbeing above individual desire",
            "Creating institutions that serve the common good",
        ],
    )

    # REQ-DEMO-03: 5 opposite edges (pentagon diagonals)
    kc.add_edge("WB", type="ColorPair",
        vertices={"White", "Black"}, disposition="opposite",
        guild="orzhov", theme="tribalism",
        synergies="White's strict codes give Black's self-interest a legible, enforceable structure — the in-group benefits from real coordination. Black's ruthlessness gives White's order teeth when gentler enforcement fails.",
        tensions="White's rules apply universally within their scope; Black's apply only where self-interest is served. Black's amoral pursuit of satisfaction corrodes White's commitment to impartial justice. White serves the group; Black uses the group.",
        persona="Asks 'who's in my circle of concern?' Strict codes within the group, near-impunity with outsiders. The good of the group vs. the good of the individual.",
        at_best="Fierce loyalty to one's people, clear moral commitment, protective solidarity.",
        at_worst="Us-versus-them bigotry, exploitation of outsiders, corruption within hierarchy.",
        example_behaviors=[
            "Drawing sharp lines between in-group and out-group",
            "Enforcing strict codes of conduct within the tribe",
            "Protecting one's own at the expense of outsiders",
        ],
    )
    kc.add_edge("WR", type="ColorPair",
        vertices={"White", "Red"}, disposition="opposite",
        guild="boros", theme="heroism",
        synergies="Red's passionate conviction and White's moral commitment channel into the same act: decisive defense of what is right. White gives Red's action a principled direction; Red gives White's principles the courage to be enforced.",
        tensions="White deliberates; Red acts. White's rule-following can constrain the urgent action Red's passion demands. Red's emotional certainty can override the careful deliberation White requires to ensure justice rather than merely punishment.",
        persona="Asks 'what needs to be done? What would a good person do?' Passion channeled through morality — warriors, soldiers, vigilantes.",
        at_best="Courageous action in defense of the vulnerable, moral clarity under pressure.",
        at_worst="Zealotry, self-righteous violence, inability to see shades of gray.",
        example_behaviors=[
            "Standing up for the vulnerable when it costs something",
            "Channeling passionate conviction through moral principles",
            "Taking decisive action when justice demands it",
        ],
    )
    kc.add_edge("UG", type="ColorPair",
        vertices={"Blue", "Green"}, disposition="opposite",
        guild="simic", theme="truth_seeking",
        synergies="Both are committed to seeing the world as it actually is — Blue through analysis, Green through acceptance. Blue's rigor and Green's reverence together resist the temptation to force findings into predetermined categories.",
        tensions="Blue wants to understand nature in order to improve it; Green wants to understand it in order to harmonize with it. Blue's drive toward optimization conflicts with Green's conviction that what is natural is already sufficient. Blue abstracts; Green embeds.",
        persona="Asks 'what do I not yet understand?' While they disagree on what to do with understanding, both are deeply committed to seeing the world as it is.",
        at_best="Profound insight that bridges knowledge and wisdom, patient investigation of deep truths.",
        at_worst="Endless inquiry without action, academic paralysis, detachment from human concerns.",
        example_behaviors=[
            "Pursuing understanding for its own sake",
            "Bridging analytical knowledge with intuitive wisdom",
            "Investigating deep truths with patience and humility",
        ],
    )
    kc.add_edge("UR", type="ColorPair",
        vertices={"Blue", "Red"}, disposition="opposite",
        guild="izzet", theme="creativity",
        synergies="Blue's drive toward perfection and Red's passionate action fuse into relentless creation. Blue provides the analytical framework; Red provides the energy to push past caution and convention.",
        tensions="Blue wants to understand fully before acting; Red acts first and adjusts. Blue's perfectionism frustrates Red's impatience; Red's volatility frustrates Blue's need for precision. Blue is systematic; Red is improvisational.",
        persona="Asks 'what can be achieved? What might be possible?' Passion combined with perfection — wild artistry and mad science.",
        at_best="Breathtaking invention, inspired creation, boundary-pushing discovery.",
        at_worst="Reckless experimentation, brilliance without responsibility, unstable genius.",
        example_behaviors=[
            "Combining analytical rigor with creative passion",
            "Pushing boundaries of what's thought possible",
            "Creating brilliant but sometimes unstable innovations",
        ],
    )
    kc.add_edge("BG", type="ColorPair",
        vertices={"Black", "Green"}, disposition="opposite",
        guild="golgari", theme="profanity",
        synergies="Green's acceptance of natural cycles — growth, decay, renewal — gives Black's ruthlessness an ecological framework: consuming is not merely selfish, it is part of the cycle. Black's willingness to face death directly enables Green's wisdom about decay.",
        tensions="Black exploits cycles for individual gain; Green participates in them for collective balance. Black's self-interest can strip-mine natural systems that Green regards as sacred. Green's patience conflicts with Black's drive for immediate results.",
        persona="Asks 'what costs must be paid to achieve the ideal?' Gets down in the dirt with rot and rebirth. Embraces the cycle of life and death without flinching.",
        at_best="Unflinching pragmatism, willingness to do what's necessary, ecological wisdom about decay and renewal.",
        at_worst="Nihilistic amorality, wallowing in darkness, exploiting natural cycles for selfish ends.",
        example_behaviors=[
            "Accepting the necessity of decay for renewal",
            "Getting hands dirty with unpleasant but necessary work",
            "Embracing the full cycle of growth and decomposition",
        ],
    )

    # REQ-DEMO-04: 10 valid ColorTriple faces (C(5,3)=10 triangles in K5).
    # No structure attribute asserted (REQ-DEMO-05) — structure is discovered via SPARQL.
    # NOTE: MTG explicitly enumerates all faces. This is a model-level choice,
    # not a framework invariant. See deferred issue in models/mtg/schema.py.
    # thematic_triad = exact themes of the three bounding edges (validated by SPARQL SHACL).
    kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"],
        clan="esper",
        thematic_triad=["design", "growth_mindset", "tribalism"],
        closure="When the design impulse, the growth mindset, and the tribal circle of concern assemble, the result is a system built for the advancement of a defined group — merit within, exclusivity without. The synergies between the pairs produce something colder than any pair alone: a technocracy that is rigorous, self-serving, and self-justifying.",
        persona="A coolly calculated, methodical approach toward building a better future for oneself and one's circle. Absent frivolous emotion or excessive concern for harmony.",
        at_best="Masterful strategic planning, precision execution, principled pragmatism in service of those who earned their seat.",
        at_worst="Cold technocracy, architecture of exclusion dressed as meritocracy, contempt for those outside the design.",
        example_behaviors=[
            "Redesigning systems to eliminate inefficiency and sentimentality",
            "Identifying who has the competence to make consequential decisions",
            "Executing long-term strategies with cold precision and without self-doubt",
        ],
    )
    kc.add_face("WUR", type="ColorTriple", boundary=["WU", "UR", "WR"],
        clan="jeskai",
        thematic_triad=["design", "creativity", "heroism"],
        closure="Design, creativity, and heroism assembled together produce the scholar-warrior: a person who studies in order to act, acts in order to discover, and returns to share what was learned. The cycle of training, mastery, and teaching is self-reinforcing — each iteration raises the ceiling of what is possible.",
        persona="A cycle of inspiration, investigation, and evaluation. An explorer striding boldly forth and returning with maps to share before departing again.",
        at_best="Heroic scholarship, principled innovation, the courage to explore and the discipline to bring back something useful.",
        at_worst="Restless perfectionism that can never be satisfied, crusading intellectualism that imposes its findings on others.",
        example_behaviors=[
            "Exploring boldly and sharing discoveries with others",
            "Cycling between inspired action and careful reflection",
            "Pursuing principled innovation for the common good",
        ],
    )
    kc.add_face("WUG", type="ColorTriple", boundary=["WU", "UG", "GW"],
        clan="bant",
        thematic_triad=["design", "truth_seeking", "community"],
        closure="Careful design, patient truth-seeking, and communal harmony converge into something uncommon: an institution that genuinely develops people rather than merely constraining or using them. The absence of Black means no tension toward exploitation — Bant's closure is civilization that has learned to cultivate.",
        persona="Civilization as a form of moral cultivation. Society exists not merely to function but to develop — Bant builds the structures that allow people to become their best selves, through patience, honor, and respect for what has already been grown.",
        at_best="Institutions that develop genuine human excellence, principled patience that enables real mastery, chivalric virtue that is both idealistic and effective.",
        at_worst="Complacent meritocracy that mistakes credential for virtue, gentle paternalism that stifles those it purports to develop, stability that becomes inertia.",
        example_behaviors=[
            "Mentoring and developing talent through structured, patient practice",
            "Upholding principles even when it is costly or inconvenient to do so",
            "Building institutions that genuinely help people grow into their potential",
        ],
    )
    kc.add_face("WBR", type="ColorTriple", boundary=["WB", "BR", "WR"],
        clan="mardu",
        thematic_triad=["tribalism", "independence", "heroism"],
        closure="Tribal loyalty, fierce independence, and heroic action fuse into the warrior's code: total commitment to your band in the moment of the fight, and total freedom from obligation once the fight is done. The closure is the deed — not sustained institution, not philosophical framework, but the act itself as its own justification. Mardu moves on.",
        persona="The folk hero archetype — chooses a people or principle to defend, stands ground, then moves on. No need for deeper truth or wisdom.",
        at_best="Decisive heroism, fierce clarity about what must be done, the courage to act and then let go.",
        at_worst="Mercenary volatility, violent tribalism, honor codes that justify cruelty to outsiders.",
        example_behaviors=[
            "Committing fully to the fight in front of you, not the fight you wish you were having",
            "Acting without needing philosophical justification — the deed speaks for itself",
            "Moving on once the immediate obligation is fulfilled",
        ],
    )
    kc.add_face("WBG", type="ColorTriple", boundary=["WB", "BG", "GW"],
        clan="abzan",
        thematic_triad=["tribalism", "profanity", "community"],
        closure="When tribal codes, ecological ruthlessness, and communal endurance operate together, the result is a group that survives by treating hardship as instruction. The synergy between golgari's cycle-wisdom and selesnya's communal bonds is hardened by orzhov's in-group discipline: Abzan outlasts because it absorbs loss rather than denying it.",
        persona="Endurance as a form of wisdom. The clan survives not by winning every battle but by outlasting every adversary. Ancient law exists because it has been tested by suffering — what remains standing has earned its authority.",
        at_best="Resilience that carries communities through catastrophe, solidarity forged under pressure, inherited discipline that actually works when things get hard.",
        at_worst="Crushing conformity that mistakes survival for flourishing, hostility to anything untested by suffering, sacrificing individuals to preserve the form of the group.",
        example_behaviors=[
            "Choosing proven methods over promising but unproven alternatives",
            "Honoring obligations even when they are personally costly",
            "Drawing strength from continuity with those who endured before",
        ],
    )
    kc.add_face("WRG", type="ColorTriple", boundary=["WR", "RG", "GW"],
        clan="naya",
        thematic_triad=["heroism", "authenticity", "community"],
        closure="Heroic action, present-moment authenticity, and communal belonging close into a single experience: celebration. When you defend from abundance rather than scarcity, when you act from passion within a community that already accepts you, the defense itself becomes joyful. Naya's closure is protection as expression — not obligation.",
        persona="The world as it should be — abundant, alive, and worth celebrating. Naya doesn't survive adversity so much as it radiates against it. Joy, belonging, and passion without needing to justify them.",
        at_best="Infectious generosity, warm-hearted defense of what's genuinely good, the courage to celebrate openly even when the world is difficult.",
        at_worst="Naïve blindness to real threats, sentimental attachment to a way of life that can't survive contact with the world, paradise thinking that turns parochial.",
        example_behaviors=[
            "Hosting and celebrating rather than hoarding and defending",
            "Expressing gratitude for what already exists rather than striving for what's missing",
            "Defending a way of life from a place of abundance rather than scarcity",
        ],
    )
    kc.add_face("UBR", type="ColorTriple", boundary=["UB", "BR", "UR"],
        clan="grixis",
        thematic_triad=["growth_mindset", "independence", "creativity"],
        closure="Strategic self-reinvention, fierce independence, and creative passion close into a force that refuses all inherited constraints on what is possible. The synergies between the pairs amplify each other: dimir's precision feeds izzet's invention, rakdos's defiance removes the last inhibitions. Grixis doesn't just break the status quo — it remakes reality in its own image.",
        persona="A bold and impassioned search for satisfaction, perfection, and self-expression. Eagerness to break the status quo and remake things in your own image.",
        at_best="Revolutionary creativity, passionate excellence, transformative vision unconstrained by precedent.",
        at_worst="Megalomaniacal destruction, brilliant cruelty, narcissistic reinvention that burns everything it cannot use.",
        example_behaviors=[
            "Breaking the status quo to rebuild something better",
            "Pursuing personal vision with passionate intensity",
            "Combining brilliance with bold self-expression",
        ],
    )
    kc.add_face("UBG", type="ColorTriple", boundary=["UB", "BG", "UG"],
        clan="sultai",
        thematic_triad=["growth_mindset", "profanity", "truth_seeking"],
        closure="Growth-seeking, ecological ruthlessness, and patient truth-seeking converge into the most calculating of orientations: a hunger that respects nothing except what actually works. Sultai's closure is that when you understand natural systems deeply enough to transgress their rules without destroying them, you gain access to power that those who respect the rules cannot touch.",
        persona="A driven wanting — not fiery or passionate but sure and unyielding. Willing to break any rule or law, but respectful of the power of nature and fate.",
        at_best="Deep strategic patience, knowledge that respects natural limits, pragmatic transgression in service of understanding.",
        at_worst="Calculating exploitation of natural systems, amoral pursuit of power through forbidden knowledge.",
        example_behaviors=[
            "Pursuing forbidden knowledge with patient determination",
            "Respecting natural power while bending social rules",
            "Combining strategic patience with unyielding ambition",
        ],
    )
    kc.add_face("URG", type="ColorTriple", boundary=["UR", "RG", "UG"],
        clan="temur",
        thematic_triad=["creativity", "authenticity", "truth_seeking"],
        closure="Creative passion, present-moment authenticity, and patient truth-seeking converge into embodied knowing — understanding accumulated through encounter rather than analysis. Unlike simic's careful inquiry or izzet's systematic invention, temur's knowing is shamanic: you understand the storm by being in it. The closure is that direct experience, unmediated by framework, generates insight that study alone cannot reach.",
        persona="Knowledge earned through encounter — not study or analysis but direct immersion in what is wild and uncontrolled. Temur accumulates understanding by living fully in the world as it actually is, without the mediation of frameworks or categories.",
        at_best="Embodied wisdom that can't be taught from books, fearless encounter with the unknown, creative insight born from genuine experience rather than inference.",
        at_worst="Dismissal of accumulated knowledge as inauthentic, restless movement that prevents depth, mistaking novelty of experience for genuine understanding.",
        example_behaviors=[
            "Seeking direct experience rather than second-hand information",
            "Trusting embodied knowledge earned through encounter over conclusions reached at a distance",
            "Engaging with what is wild and uncontrolled rather than taming it for systematic study",
        ],
    )
    kc.add_face("BRG", type="ColorTriple", boundary=["BR", "RG", "BG"],
        clan="jund",
        thematic_triad=["independence", "authenticity", "profanity"],
        closure="Independence, present-moment authenticity, and ecological brutality close into the starkest realism: the world is what it is, power determines outcomes, and pretense is the only real crime. Jund's closure is that when you strip every comforting narrative, what remains is raw vitality — unglamorous and honest, its own form of wholeness.",
        persona="A feral realism with no sugar coating. Self-aware self-indulgence that doesn't pretend to be anything it isn't. Refusal to follow contrived rules.",
        at_best="Radical honesty, raw vitality, living fully without pretense.",
        at_worst="Savage nihilism, predatory self-interest, contempt for civilization.",
        example_behaviors=[
            "Living with raw honesty and no pretense",
            "Refusing to follow rules that don't serve reality",
            "Embracing primal vitality without apology",
        ],
    )

    return kc


if __name__ == "__main__":
    kc = build_mtg_instance()
    print(kc.dump_graph())
