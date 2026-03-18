"""
Glia Visual Vocabulary — Type Definitions & 5D Morphospace Coordinates

Each glia type has canonical coordinates in 5D morphospace:
  D1: Branching Complexity  (compact/smooth → highly ramified)
  D2: Activation Energy     (quiescent → reactive/phagocytic)
  D3: Network Connectivity  (isolated unit → syncytial/gap-junction coupled)
  D4: Signal Propagation    (static/frozen → propagating waves)
  D5: Structural Role       (passive/ambient → load-bearing scaffold)
"""

DIMENSION_DEFINITIONS = {
    "D1_branching_complexity": {
        "name": "Branching Complexity",
        "range": [0.0, 1.0],
        "low": "Compact, smooth membrane, minimal processes",
        "high": "Highly ramified, fractal branching, dense fine processes",
        "visual_low": "rounded silhouettes, smooth contours, minimal edge detail",
        "visual_high": "dense branching patterns, fractal edges, intricate silhouettes, high-frequency detail",
    },
    "D2_activation_energy": {
        "name": "Activation Energy",
        "range": [0.0, 1.0],
        "low": "Quiescent, resting, homeostatic surveillance",
        "high": "Fully reactive, phagocytic, maximal metabolic engagement",
        "visual_low": "cool palette, soft luminance, diffuse ambient glow",
        "visual_high": "warm/intense coloring, compact energetic forms, directional energy vectors, high contrast",
    },
    "D3_network_connectivity": {
        "name": "Network Connectivity",
        "range": [0.0, 1.0],
        "low": "Isolated unit, no coupling to neighbors",
        "high": "Syncytial network, extensive gap-junction coupling, shared cytoplasm",
        "visual_low": "solitary forms, negative space isolation, individual elements",
        "visual_high": "repeating connected motifs, tiling patterns, bridge structures, mesh topology visible",
    },
    "D4_signal_propagation": {
        "name": "Signal Propagation",
        "range": [0.0, 1.0],
        "low": "Static, no active signaling, frozen state",
        "high": "Propagating calcium waves, rolling cascades across domains",
        "visual_low": "frozen composition, uniform tone, static equilibrium",
        "visual_high": "wave-like gradients, propagation trails, temporal blur, hue shifts along wavefront",
    },
    "D5_structural_role": {
        "name": "Structural Role",
        "range": [0.0, 1.0],
        "low": "Passive, ambient presence, no load-bearing function",
        "high": "Load-bearing scaffold, architectural support, tissue organization",
        "visual_low": "floating, weightless, atmospheric presence",
        "visual_high": "rigid geometry, parallel alignment, visual weight, scaffolding lines, columnar structure",
    },
}

# Canonical 5D coordinates for each glia type
# Format: [D1_branching, D2_activation, D3_connectivity, D4_signal, D5_structure]
GLIA_TYPES = {
    "astrocyte_protoplasmic": {
        "name": "Astrocyte (Protoplasmic)",
        "coordinates": [0.85, 0.20, 0.90, 0.75, 0.40],
        "morphology": "Bushy, cloud-like soma with dense fine processes radiating in all directions. "
                       "Each astrocyte tiles a non-overlapping spatial domain. Found in gray matter.",
        "key_visual": "Stellate radiation from central soma, territory tiling with minimal overlap, "
                      "gap-junction bridges to adjacent domains at ~120° spacing",
        "biological_notes": "Ensheath synapses (tripartite synapse), buffer K+, regulate blood-brain barrier. "
                            "Calcium waves propagate through syncytial network via gap junctions.",
        "visual_keywords": [
            "stellate", "radiating", "bushy", "cloud-like", "tiling",
            "territory", "fine processes", "gap-junction bridges",
        ],
    },
    "astrocyte_fibrous": {
        "name": "Astrocyte (Fibrous)",
        "coordinates": [0.55, 0.15, 0.65, 0.50, 0.80],
        "morphology": "Elongated processes aligned parallel to axon bundles. Less bushy than "
                       "protoplasmic, more directional. Found in white matter.",
        "key_visual": "Parallel-aligned processes creating directional scaffolding, "
                      "elongated forms following axon tract geometry",
        "biological_notes": "Support myelinated fiber tracts, maintain white matter architecture. "
                            "Less elaborate branching than protoplasmic counterparts.",
        "visual_keywords": [
            "elongated", "parallel", "directional", "scaffolding",
            "linear", "tract-following", "white matter flow",
        ],
    },
    "microglia_ramified": {
        "name": "Microglia (Ramified)",
        "coordinates": [0.90, 0.10, 0.20, 0.30, 0.10],
        "morphology": "Delicate, highly branched surveillance morphology. Fine processes constantly "
                       "extending and retracting, sampling the local environment.",
        "key_visual": "Fractal-like branching at fine scale, delicate exploratory processes, "
                      "high complexity in a small spatial footprint",
        "biological_notes": "Immune surveillance state. Processes scan ~1.5x their soma volume per hour. "
                            "First responders to CNS perturbation.",
        "visual_keywords": [
            "fractal", "delicate", "surveillance", "fine detail",
            "exploratory", "watchful", "intricate", "high-frequency branching",
        ],
    },
    "microglia_amoeboid": {
        "name": "Microglia (Amoeboid)",
        "coordinates": [0.15, 0.95, 0.35, 0.80, 0.10],
        "morphology": "Compact, rounded, phagocytic form. Retracted processes, enlarged soma, "
                       "actively motile with pseudopod extensions.",
        "key_visual": "Compact intense mass, rounded contour with pseudopod protrusions, "
                      "directional movement vectors, concentrated energy",
        "biological_notes": "Fully activated phagocytic state. Releases cytokines, engulfs debris. "
                            "High metabolic rate, rapid directed migration.",
        "visual_keywords": [
            "compact", "rounded", "intense", "phagocytic",
            "pseudopod", "motile", "concentrated", "directional",
        ],
    },
    "oligodendrocyte": {
        "name": "Oligodendrocyte",
        "coordinates": [0.45, 0.10, 0.50, 0.15, 0.85],
        "morphology": "Compact cell body with organized processes that wrap concentrically around "
                       "axon segments. Each cell myelinates up to 50 axon internodes.",
        "key_visual": "Concentric wrapping geometry, repeating myelination segments with "
                      "nodes of Ranvier as punctuation points between wrapped regions",
        "biological_notes": "Produce myelin sheaths in CNS. Wrapping is highly organized: "
                            "alternating myelinated internodes and bare nodes of Ranvier.",
        "visual_keywords": [
            "concentric", "wrapping", "rhythmic", "segmented",
            "node punctuation", "organized", "layered", "insulating",
        ],
    },
    "ng2_opc": {
        "name": "NG2 / Oligodendrocyte Precursor Cell",
        "coordinates": [0.60, 0.40, 0.45, 0.35, 0.30],
        "morphology": "Multipolar with moderate branching. Intermediate form between progenitor "
                       "and mature oligodendrocyte. Exploratory, proliferative.",
        "key_visual": "Multipolar exploratory branching, transitional morphology suggesting "
                      "potential rather than commitment, moderate process density",
        "biological_notes": "Only dividing glia population in adult brain. Receive synaptic input. "
                            "Can differentiate into myelinating oligodendrocytes.",
        "visual_keywords": [
            "multipolar", "transitional", "exploratory", "potential",
            "intermediate", "proliferative", "uncommitted", "branching",
        ],
    },
    "ependymal": {
        "name": "Ependymal Cell",
        "coordinates": [0.20, 0.10, 0.75, 0.60, 0.55],
        "morphology": "Ciliated columnar epithelial cells in uniform packing along ventricle surfaces. "
                       "Cilia beat in coordinated waves creating directional CSF flow.",
        "key_visual": "Uniform columnar packing with surface cilia, directional flow patterns, "
                      "rhythmic coordinated beating visible as wave texture",
        "biological_notes": "Line brain ventricles. Ciliary beating drives cerebrospinal fluid circulation. "
                            "Some types (tanycytes) have neuroendocrine functions.",
        "visual_keywords": [
            "ciliated", "columnar", "uniform", "directional flow",
            "surface rhythm", "coordinated", "epithelial", "wave texture",
        ],
    },
    "radial_glia": {
        "name": "Radial Glia",
        "coordinates": [0.30, 0.10, 0.30, 0.20, 0.95],
        "morphology": "Bipolar cells spanning the full cortical thickness from ventricle to pial surface. "
                       "Long radial process serves as migration scaffold for newborn neurons.",
        "key_visual": "Vertical axis spanning full field height, scaffold geometry, "
                      "bipolar elongation with apical and basal attachments",
        "biological_notes": "Primary progenitor cells during brain development. Guide neuronal migration "
                            "along their radial processes. Give rise to astrocytes postnatally.",
        "visual_keywords": [
            "bipolar", "vertical", "spanning", "scaffold",
            "architectural", "migration guide", "developmental", "columnar axis",
        ],
    },
    "schwann_cell": {
        "name": "Schwann Cell",
        "coordinates": [0.15, 0.10, 0.05, 0.10, 0.80],
        "morphology": "Single-axon wrapping in peripheral nervous system. Each Schwann cell "
                       "myelinates one internode of one axon. Intimate 1:1 relationship.",
        "key_visual": "Intimate containment wrapping, single-axon focus, segmented coverage "
                      "with clear boundaries between individual cell territories",
        "biological_notes": "PNS myelination. Unlike oligodendrocytes (multi-axon), each Schwann cell "
                            "wraps a single axon segment. Critical for nerve regeneration.",
        "visual_keywords": [
            "intimate", "containment", "single-wrap", "segmented",
            "peripheral", "1:1 relationship", "isolated units", "regenerative",
        ],
    },
}


# Activation trajectory definitions
# These define how 5D coordinates shift as activation_intensity goes from 0.0 to 1.0
# Format: {dimension_index: (delta_at_full_activation)} — added to base coordinates
ACTIVATION_TRAJECTORIES = {
    "microglia": {
        "description": "Ramified surveillance → amoeboid phagocytic",
        "base_type": "microglia_ramified",
        "terminal_type": "microglia_amoeboid",
        "states": {
            0.0: {"label": "Ramified (surveillance)", "coords": GLIA_TYPES["microglia_ramified"]["coordinates"]},
            0.3: {"label": "Hypertrophic (primed)", "coords": [0.60, 0.45, 0.28, 0.50, 0.10]},
            0.6: {"label": "Bushy (reactive)", "coords": [0.35, 0.70, 0.32, 0.65, 0.10]},
            1.0: {"label": "Amoeboid (phagocytic)", "coords": GLIA_TYPES["microglia_amoeboid"]["coordinates"]},
        },
        "trajectory_notes": "D1 (branching) drops sharply as processes retract. "
                            "D2 (activation) rises continuously. "
                            "D3 (connectivity) increases slightly (cytokine signaling to neighbors). "
                            "D4 (signal) rises as ATP/purinergic signaling increases. "
                            "D5 (structure) stays low throughout — microglia are never structural.",
    },
    "astrocyte": {
        "description": "Quiescent homeostatic → reactive → scar-forming",
        "base_type": "astrocyte_protoplasmic",
        "terminal_type": None,  # scar-forming is a distinct endpoint, not another canonical type
        "states": {
            0.0: {"label": "Quiescent (homeostatic)", "coords": GLIA_TYPES["astrocyte_protoplasmic"]["coordinates"]},
            0.3: {"label": "Mild reactive (GFAP+)", "coords": [0.75, 0.40, 0.85, 0.80, 0.50]},
            0.6: {"label": "Moderate reactive (hypertrophic)", "coords": [0.60, 0.60, 0.70, 0.85, 0.65]},
            1.0: {"label": "Scar-forming (severe)", "coords": [0.35, 0.80, 0.45, 0.40, 0.90]},
        },
        "trajectory_notes": "D1 (branching) decreases as processes thicken and simplify. "
                            "D2 (activation) rises with GFAP upregulation. "
                            "D3 (connectivity) initially maintained then drops as scar isolates. "
                            "D4 (signal) peaks at moderate reactivity then drops as scar forms. "
                            "D5 (structure) rises dramatically — scar tissue is maximally structural.",
    },
}
