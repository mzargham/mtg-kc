"""
demo/demo_instance.py

MTG color wheel knowledge complex — full instance construction.
Layer 3: concrete data built using the models.mtg schema (layer 2)
and the kc framework (layer 1).

Authored in WP4, enriched in WP4.5 with essay-derived attributes.
Returns a ready-to-use KnowledgeComplex for the Marimo notebook.

REQ-DEMO-01 through REQ-DEMO-05.
"""

from kc.schema import SchemaBuilder
from kc.graph import KnowledgeComplex
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
    kc.add_face("WUB", type="ColorTriple", boundary=["WU", "UB", "WB"],
        clan="esper",
        persona="A coolly calculated, methodical approach toward building a better future for oneself and one's circle. Absent frivolous emotion or excessive concern for harmony.",
        at_best="Masterful strategic planning, building institutions that actually work, principled pragmatism.",
        at_worst="Cold technocracy, dismissal of human feeling, elitist tribalism.",
        example_behaviors=[
            "Building efficient systems that serve a select group",
            "Applying cold logic to complex social problems",
            "Strategic long-term planning without sentimentality",
        ],
    )
    kc.add_face("WUR", type="ColorTriple", boundary=["WU", "UR", "WR"],
        clan="jeskai",
        persona="A cycle of inspiration, investigation, and evaluation. An explorer striding boldly forth and returning with maps to share before departing again.",
        at_best="Heroic scholarship, sharing discovery for the common good, principled innovation.",
        at_worst="Restless perfectionism, inability to be satisfied, crusading intellectualism.",
        example_behaviors=[
            "Exploring boldly and sharing discoveries with others",
            "Cycling between inspired action and careful reflection",
            "Pursuing principled innovation for the common good",
        ],
    )
    kc.add_face("WUG", type="ColorTriple", boundary=["WU", "UG", "GW"],
        clan="bant",
        persona="A calm and peaceful stability underlying slow progression toward knowledge, wisdom, and fulfillment. Scaffolds rather than cages, patience rather than passion.",
        at_best="Serene wisdom, institutions that nurture growth, patient pursuit of understanding.",
        at_worst="Complacent stagnation, gentle tyranny of low expectations, passionless order.",
        example_behaviors=[
            "Building patient, nurturing institutional structures",
            "Pursuing wisdom through calm and steady progression",
            "Creating scaffolds that support growth without constraining it",
        ],
    )
    kc.add_face("WBR", type="ColorTriple", boundary=["WB", "BR", "WR"],
        clan="mardu",
        persona="The folk hero archetype — chooses a people or principle to defend, stands ground, then moves on. No need for deeper truth or wisdom.",
        at_best="Decisive heroism, fierce protection of the vulnerable, principled action without overthinking.",
        at_worst="Mercenary volatility, violent tribalism, honor codes that justify cruelty.",
        example_behaviors=[
            "Choosing a cause and defending it with total commitment",
            "Taking decisive action without need for deep justification",
            "Moving on once the immediate fight is won",
        ],
    )
    kc.add_face("WBG", type="ColorTriple", boundary=["WB", "BG", "GW"],
        clan="abzan",
        persona="Unyielding certainty about one's place in the world. Adherence to ancient law, savage will to survive and protect a way of life. Stolid practicality.",
        at_best="Enduring traditions that sustain communities, practical wisdom passed through generations.",
        at_worst="Fundamentalist rigidity, brutal enforcement of ancient codes, hostility to curiosity.",
        example_behaviors=[
            "Maintaining traditions that have proven their worth",
            "Protecting a way of life with unyielding determination",
            "Passing practical wisdom through generations",
        ],
    )
    kc.add_face("WRG", type="ColorTriple", boundary=["WR", "RG", "GW"],
        clan="naya",
        persona="A passionate presence tempered by tradition and belongingness. Full and vibrant commitment to one's chosen way of life, with fierce desire to protect what already is.",
        at_best="Warm-hearted community, joyful tradition, courageous protection of the good.",
        at_worst="Parochial tribalism, anti-intellectual hostility to change, sentimental blindness.",
        example_behaviors=[
            "Celebrating and protecting cherished traditions",
            "Committing fully to one's community and way of life",
            "Defending what's good with passionate conviction",
        ],
    )
    kc.add_face("UBR", type="ColorTriple", boundary=["UB", "BR", "UR"],
        clan="grixis",
        persona="A bold and impassioned search for satisfaction, perfection, and self-expression. Eagerness to break the status quo and remake things in your own image.",
        at_best="Revolutionary creativity, passionate excellence, transformative vision.",
        at_worst="Megalomaniacal destruction, brilliant cruelty, narcissistic reinvention.",
        example_behaviors=[
            "Breaking the status quo to rebuild something better",
            "Pursuing personal vision with passionate intensity",
            "Combining brilliance with bold self-expression",
        ],
    )
    kc.add_face("UBG", type="ColorTriple", boundary=["UB", "BG", "UG"],
        clan="sultai",
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
        persona="A childlike curiosity and Zen-like knowledge of self. Insatiable desire to play, explore, discover, and understand, without self-consciousness or ego.",
        at_best="Pure wonder, ego-less exploration, creative play that generates genuine insight.",
        at_worst="Aimless wandering, refusal to commit, childish avoidance of responsibility.",
        example_behaviors=[
            "Exploring with childlike curiosity and no ego",
            "Playing creatively as a path to genuine discovery",
            "Pursuing understanding without self-consciousness",
        ],
    )
    kc.add_face("BRG", type="ColorTriple", boundary=["BR", "RG", "BG"],
        clan="jund",
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
