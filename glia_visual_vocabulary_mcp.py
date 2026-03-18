"""
Glia Visual Vocabulary MCP Server

Three-layer architecture:
  Layer 1: Pure taxonomy (0 tokens) — list_glia_types, get_glia_profile, etc.
  Layer 2: Deterministic computation (0 tokens) — distances, trajectories, parameter mapping
  Layer 3: Claude synthesis (~100-200 tokens) — enhance_prompt_with_glia, generate_frame_sequence

Entrypoint for FastMCP Cloud: glia_visual_vocabulary_mcp.py:mcp
"""

from fastmcp import FastMCP
from typing import Optional, List, Dict, Tuple
import json
import numpy as np

from taxonomy.glia_types import (
    GLIA_TYPES,
    DIMENSION_DEFINITIONS,
    ACTIVATION_TRAJECTORIES,
)
from taxonomy.visual_translations import (
    translate_coordinates,
    translate_branching,
    translate_activation,
    translate_connectivity,
    translate_signal_propagation,
    translate_structural_role,
)
from morphospace.trajectory import compute_trajectory, compute_activation_trajectory
from morphospace.coordinates import (
    compute_distance,
    find_nearest,
    interpolate_activation,
    DIMENSION_NAMES,
)
from synthesis.prompt_builder import (
    build_enhancement_context,
    build_frame_sequence_context,
    ENHANCEMENT_SYSTEM_PROMPT,
    FRAME_SEQUENCE_SYSTEM_PROMPT,
)


mcp = FastMCP("glia-visual-vocabulary")


@mcp.tool()
def get_server_info() -> dict:
    """Get server metadata, capabilities, and Phase 2.6/2.7 status."""
    return {
        "server": "glia-visual-vocabulary",
        "version": "2.7.0",
        "description": "Glia visual vocabulary with 5D morphospace, rhythmic presets, "
                       "and attractor visualization prompt generation",
        "architecture": {
            "layer_1": "Pure taxonomy (0 tokens): 9 glia types, 5D coordinates, activation trajectories",
            "layer_2": "Deterministic computation (0 tokens): distances, trajectories, "
                       "Phase 2.6 presets, Phase 2.7 attractor prompts",
            "layer_3": "Claude synthesis (~100-200 tokens): prompt enhancement, frame sequences",
        },
        "morphospace": {
            "dimensions": 5,
            "parameter_names": GLIA_PARAMETER_NAMES,
            "canonical_states": 9,
            "activation_trajectories": 2,
        },
        "phase_2_6_enhancements": {
            "rhythmic_presets": True,
            "preset_count": len(GLIA_RHYTHMIC_PRESETS),
            "periods": sorted(set(c["steps_per_cycle"] for c in GLIA_RHYTHMIC_PRESETS.values())),
            "forced_orbit_integration": True,
            "patterns": ["sinusoidal", "triangular", "square"],
        },
        "phase_2_7_enhancements": {
            "attractor_visualization": True,
            "visual_type_count": len(GLIA_VISUAL_TYPES),
            "prompt_modes": ["composite", "split_view", "sequence"],
            "supported_targets": ["ComfyUI", "Stable Diffusion", "DALL-E"],
        },
        "tier_4d_integration": {
            "ready": True,
            "domain_registry_config": True,
            "predicted_emergent_attractors": 5,
        },
    }


# ═══════════════════════════════════════════════════════════════════
# LAYER 1 — Pure Taxonomy (0 tokens)
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_glia_types(
    filter_category: Optional[str] = None,
) -> dict:
    """
    List all 9 glia types with their 5D morphospace coordinates.
    
    Optional filter_category: 'astrocyte', 'microglia', 'myelinating', 'other'
    to show subsets.
    """
    category_map = {
        "astrocyte": ["astrocyte_protoplasmic", "astrocyte_fibrous"],
        "microglia": ["microglia_ramified", "microglia_amoeboid"],
        "myelinating": ["oligodendrocyte", "schwann_cell"],
        "other": ["ng2_opc", "ependymal", "radial_glia"],
    }
    
    if filter_category and filter_category in category_map:
        type_keys = category_map[filter_category]
    else:
        type_keys = list(GLIA_TYPES.keys())
    
    result = {}
    for key in type_keys:
        gt = GLIA_TYPES[key]
        result[key] = {
            "name": gt["name"],
            "coordinates": {
                dim: round(val, 2)
                for dim, val in zip(DIMENSION_NAMES, gt["coordinates"])
            },
        }
    
    return {
        "count": len(result),
        "filter": filter_category,
        "types": result,
    }


@mcp.tool()
def get_glia_profile(glia_type: str) -> dict:
    """
    Get full profile for a glia type: morphology, 5D coordinates,
    visual translation, biological notes, and visual keywords.
    
    glia_type: one of astrocyte_protoplasmic, astrocyte_fibrous,
    microglia_ramified, microglia_amoeboid, oligodendrocyte,
    ng2_opc, ependymal, radial_glia, schwann_cell
    """
    if glia_type not in GLIA_TYPES:
        available = ", ".join(sorted(GLIA_TYPES.keys()))
        return {"error": f"Unknown glia type: '{glia_type}'. Available: {available}"}
    
    gt = GLIA_TYPES[glia_type]
    translation = translate_coordinates(gt["coordinates"])
    
    return {
        "type": glia_type,
        "name": gt["name"],
        "morphology": gt["morphology"],
        "key_visual": gt["key_visual"],
        "biological_notes": gt["biological_notes"],
        "visual_keywords": gt["visual_keywords"],
        "coordinates": {
            dim: round(val, 4)
            for dim, val in zip(DIMENSION_NAMES, gt["coordinates"])
        },
        "visual_translation": {
            "composed_specification": translation["composed_specification"],
            "branching": translation["branching"],
            "activation": translation["activation"],
            "connectivity": translation["connectivity"],
            "signal": translation["signal"],
            "structure": translation["structure"],
        },
    }


@mcp.tool()
def get_morphospace_dimensions() -> dict:
    """
    Get the 5 morphospace dimension definitions with range semantics
    and visual translation rules.
    """
    return {
        "dimensions": DIMENSION_DEFINITIONS,
        "count": len(DIMENSION_DEFINITIONS),
        "note": "All dimensions range 0.0-1.0. Coordinates map to visual "
                "vocabulary via translate_coordinates().",
    }


@mcp.tool()
def list_state_modifiers(glia_type: Optional[str] = None) -> dict:
    """
    List available activation state transitions.
    
    Only microglia and astrocytes have defined activation trajectories.
    Optional glia_type filter: 'microglia' or 'astrocyte'.
    """
    if glia_type and glia_type not in ACTIVATION_TRAJECTORIES:
        return {
            "error": f"No activation trajectory defined for '{glia_type}'. "
                     f"Available: {', '.join(ACTIVATION_TRAJECTORIES.keys())}",
        }
    
    keys = [glia_type] if glia_type else list(ACTIVATION_TRAJECTORIES.keys())
    
    result = {}
    for key in keys:
        traj = ACTIVATION_TRAJECTORIES[key]
        result[key] = {
            "description": traj["description"],
            "base_type": traj["base_type"],
            "terminal_type": traj["terminal_type"],
            "states": {
                str(k): {
                    "label": v["label"],
                    "coordinates": {
                        dim: round(c, 2)
                        for dim, c in zip(DIMENSION_NAMES, v["coords"])
                    },
                }
                for k, v in traj["states"].items()
            },
            "trajectory_notes": traj["trajectory_notes"],
        }
    
    return {"modifiers": result, "count": len(result)}


# ═══════════════════════════════════════════════════════════════════
# LAYER 2 — Deterministic Computation (0 tokens)
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def map_glia_parameters(
    glia_type: str,
    activation_intensity: Optional[float] = None,
    branching_override: Optional[float] = None,
    connectivity_override: Optional[float] = None,
    signal_override: Optional[float] = None,
    structure_override: Optional[float] = None,
) -> dict:
    """
    Map glia type to adjusted 5D coordinates with visual translation.
    
    If activation_intensity is provided (0.0-1.0) for microglia or astrocyte,
    all 5 dimensions shift simultaneously along the biological activation path.
    Individual dimension overrides can further adjust specific coordinates.
    
    Returns adjusted coordinates and full visual translation.
    """
    if glia_type not in GLIA_TYPES:
        available = ", ".join(sorted(GLIA_TYPES.keys()))
        return {"error": f"Unknown glia type: '{glia_type}'. Available: {available}"}
    
    coords = list(GLIA_TYPES[glia_type]["coordinates"])
    activation_applied = False
    
    # Apply activation trajectory if requested
    if activation_intensity is not None:
        activation_intensity = max(0.0, min(1.0, activation_intensity))
        # Determine which activation trajectory to use
        traj_key = None
        if glia_type.startswith("microglia"):
            traj_key = "microglia"
        elif glia_type.startswith("astrocyte"):
            traj_key = "astrocyte"
        
        if traj_key and traj_key in ACTIVATION_TRAJECTORIES:
            keyframes = {
                k: v["coords"]
                for k, v in ACTIVATION_TRAJECTORIES[traj_key]["states"].items()
            }
            coords = interpolate_activation(keyframes, activation_intensity)
            activation_applied = True
    
    # Apply individual overrides
    overrides = [
        branching_override,
        None,  # activation_energy is controlled by activation_intensity, not directly
        connectivity_override,
        signal_override,
        structure_override,
    ]
    for i, override in enumerate(overrides):
        if override is not None:
            coords[i] = max(0.0, min(1.0, override))
    
    translation = translate_coordinates(coords)
    gt = GLIA_TYPES[glia_type]
    
    return {
        "type": glia_type,
        "name": gt["name"],
        "activation_applied": activation_applied,
        "activation_intensity": activation_intensity,
        "coordinates": {
            dim: round(val, 4)
            for dim, val in zip(DIMENSION_NAMES, coords)
        },
        "visual_translation": {
            "composed_specification": translation["composed_specification"],
            "branching": translation["branching"],
            "activation": translation["activation"],
            "connectivity": translation["connectivity"],
            "signal": translation["signal"],
            "structure": translation["structure"],
        },
    }


@mcp.tool()
def compute_glia_distance(
    type_a: str,
    type_b: str,
) -> dict:
    """
    Compute Euclidean distance between two glia types in 5D morphospace.
    Returns overall distance and per-dimension deltas.
    """
    if type_a not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{type_a}'"}
    if type_b not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{type_b}'"}
    
    return compute_distance(
        GLIA_TYPES[type_a]["coordinates"],
        GLIA_TYPES[type_b]["coordinates"],
        label_a=GLIA_TYPES[type_a]["name"],
        label_b=GLIA_TYPES[type_b]["name"],
    )


@mcp.tool()
def compute_glia_trajectory(
    start_type: str,
    end_type: str,
    num_steps: int = 30,
) -> dict:
    """
    Compute RK4-integrated trajectory between two glia types through
    5D morphospace. Returns per-step coordinates, convergence analysis,
    and path efficiency metrics.
    """
    if start_type not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{start_type}'"}
    if end_type not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{end_type}'"}
    
    num_steps = max(5, min(100, num_steps))
    
    result = compute_trajectory(
        GLIA_TYPES[start_type]["coordinates"],
        GLIA_TYPES[end_type]["coordinates"],
        num_steps=num_steps,
        dimension_names=DIMENSION_NAMES,
    )
    
    result["start_type"] = GLIA_TYPES[start_type]["name"]
    result["end_type"] = GLIA_TYPES[end_type]["name"]
    
    return result


@mcp.tool()
def find_nearby_glia(
    glia_type: Optional[str] = None,
    coordinates: Optional[List[float]] = None,
    max_results: int = 5,
    max_distance: Optional[float] = None,
) -> dict:
    """
    Find nearest glia types to a given type or arbitrary 5D coordinates.
    Provide either glia_type OR coordinates (list of 5 floats).
    """
    if glia_type and glia_type not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{glia_type}'"}
    
    if glia_type:
        target = GLIA_TYPES[glia_type]["coordinates"]
        exclude = [glia_type]
        label = GLIA_TYPES[glia_type]["name"]
    elif coordinates and len(coordinates) == 5:
        target = coordinates
        exclude = []
        label = f"custom({', '.join(f'{c:.2f}' for c in coordinates)})"
    else:
        return {"error": "Provide either glia_type or coordinates (list of 5 floats)"}
    
    candidates = {k: v["coordinates"] for k, v in GLIA_TYPES.items()}
    
    results = find_nearest(
        target, candidates,
        exclude=exclude,
        max_results=max_results,
        max_distance=max_distance,
    )
    
    return {
        "query": label,
        "results": results,
        "count": len(results),
    }


@mcp.tool()
def compute_activation_path(
    glia_type: str,
    start_activation: float = 0.0,
    end_activation: float = 1.0,
    num_steps: int = 30,
) -> dict:
    """
    Compute trajectory along a biological activation path.
    
    Activation modifies ALL 5 dimensions simultaneously along biologically
    defined keyframes. Only available for microglia and astrocyte types.
    
    Returns per-step coordinates with activation_intensity values,
    suitable for driving frame-sequence animation.
    """
    traj_key = None
    if glia_type.startswith("microglia"):
        traj_key = "microglia"
    elif glia_type.startswith("astrocyte"):
        traj_key = "astrocyte"
    
    if not traj_key or traj_key not in ACTIVATION_TRAJECTORIES:
        return {
            "error": f"No activation trajectory for '{glia_type}'. "
                     f"Available: microglia (ramified/amoeboid), astrocyte (protoplasmic/fibrous)"
        }
    
    traj = ACTIVATION_TRAJECTORIES[traj_key]
    keyframes = {k: v["coords"] for k, v in traj["states"].items()}
    
    # Filter keyframes to requested activation range
    filtered = {
        k: v for k, v in keyframes.items()
        if start_activation <= k <= end_activation
    }
    # Ensure start and end points exist via interpolation
    if start_activation not in filtered:
        filtered[start_activation] = interpolate_activation(keyframes, start_activation)
    if end_activation not in filtered:
        filtered[end_activation] = interpolate_activation(keyframes, end_activation)
    
    num_steps = max(5, min(100, num_steps))
    
    base_coords = GLIA_TYPES[traj["base_type"]]["coordinates"]
    
    result = compute_activation_trajectory(
        base_coords=base_coords,
        activation_keyframes=filtered,
        num_steps=num_steps,
        start_activation=start_activation,
        end_activation=end_activation,
        dimension_names=DIMENSION_NAMES,
    )
    
    result["glia_type"] = glia_type
    result["trajectory_description"] = traj["description"]
    result["trajectory_notes"] = traj["trajectory_notes"]
    result["state_labels"] = {
        str(k): v["label"]
        for k, v in traj["states"].items()
        if start_activation <= k <= end_activation
    }
    
    return result


# ═══════════════════════════════════════════════════════════════════
# PHASE 2.6 — Rhythmic Presets (Layer 2, 0 tokens)
# ═══════════════════════════════════════════════════════════════════
#
# Period strategy for cross-domain composition:
#   14 — fills gap 12-15 in global period landscape
#   18 — synchronizes with nuclear, catastrophe, diatom
#   20 — synchronizes with microscopy, catastrophe, diatom
#   26 — fills gap 25-30 (near discovered Period 27 gap-filler)
#   30 — synchronizes with microscopy, diatom, heraldic (major hub)
#   36 — LCM harmonics (2×18, 3×12), novel higher-period resonance
#
# All presets use forced orbit integration: guaranteed periodic
# closure, zero drift, 100% detection in Tier 4D discovery.

GLIA_PARAMETER_NAMES = [
    "branching_complexity",
    "activation_energy",
    "network_connectivity",
    "signal_propagation",
    "structural_role",
]

# Canonical coordinates indexed by state ID for preset lookup
GLIA_STATE_COORDINATES = {
    name: {
        dim: coord
        for dim, coord in zip(GLIA_PARAMETER_NAMES, gt["coordinates"])
    }
    for name, gt in GLIA_TYPES.items()
}

GLIA_RHYTHMIC_PRESETS = {
    "activation_cascade": {
        "state_a": "microglia_ramified",
        "state_b": "microglia_amoeboid",
        "pattern": "sinusoidal",
        "num_cycles": 3,
        "steps_per_cycle": 18,
        "description": "Immune surveillance → phagocytic activation → recovery. "
                       "Branching retracts as activation energy surges, signal propagation "
                       "intensifies. Period 18 synchronizes with nuclear/catastrophe/diatom.",
    },
    "network_pulse": {
        "state_a": "astrocyte_protoplasmic",
        "state_b": "ependymal",
        "pattern": "sinusoidal",
        "num_cycles": 3,
        "steps_per_cycle": 20,
        "description": "Syncytial network oscillation between stellate astrocyte mesh and "
                       "ciliary ependymal flow. Connectivity stays high while branching and "
                       "signal modes shift. Period 20 synchronizes with microscopy/catastrophe/diatom.",
    },
    "myelination_rhythm": {
        "state_a": "oligodendrocyte",
        "state_b": "schwann_cell",
        "pattern": "triangular",
        "num_cycles": 4,
        "steps_per_cycle": 14,
        "description": "Symmetric CNS ↔ PNS myelination oscillation. Both states are "
                       "structural and low-activation, but differ in connectivity and branching. "
                       "Period 14 fills the gap between 12 and 15 in the global landscape.",
    },
    "developmental_arc": {
        "state_a": "radial_glia",
        "state_b": "astrocyte_protoplasmic",
        "pattern": "sinusoidal",
        "num_cycles": 2,
        "steps_per_cycle": 30,
        "description": "Progenitor scaffold → mature astrocyte maturation rhythm. Large "
                       "morphospace traverse: structural drops, branching and connectivity "
                       "surge. Period 30 locks with the major cross-domain hub.",
    },
    "surveillance_sweep": {
        "state_a": "microglia_ramified",
        "state_b": "ng2_opc",
        "pattern": "square",
        "num_cycles": 3,
        "steps_per_cycle": 26,
        "description": "Sharp switching between immune surveillance (ramified microglia) "
                       "and progenitor monitoring (NG2/OPC). Square wave creates abrupt "
                       "morphological transitions. Period 26 fills gap 25-30.",
    },
    "structural_remodeling": {
        "state_a": "astrocyte_fibrous",
        "state_b": "radial_glia",
        "pattern": "triangular",
        "num_cycles": 2,
        "steps_per_cycle": 36,
        "description": "White-matter scaffold remodeling between fibrous astrocyte and "
                       "radial glia architectures. Both high-structure but different alignment "
                       "and connectivity. Period 36 creates LCM harmonics (2×18, 3×12).",
    },
}


# ── Phase 2.6 computation helpers ────────────────────────────────

def _generate_oscillation(num_steps: int, num_cycles: float, pattern: str) -> np.ndarray:
    """Generate oscillation pattern in [0, 1]."""
    t = np.linspace(0, 2 * np.pi * num_cycles, num_steps, endpoint=False)
    if pattern == "sinusoidal":
        return 0.5 * (1.0 + np.sin(t))
    elif pattern == "triangular":
        t_norm = (t / (2 * np.pi)) % 1.0
        return np.where(t_norm < 0.5, 2.0 * t_norm, 2.0 * (1.0 - t_norm))
    elif pattern == "square":
        t_norm = (t / (2 * np.pi)) % 1.0
        return np.where(t_norm < 0.5, 0.0, 1.0)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def _generate_preset_trajectory(preset_config: dict) -> dict:
    """
    Generate forced orbit trajectory for a single Phase 2.6 preset.

    Returns dict with 'states' (list of coordinate dicts), 'per_step'
    (per-step analysis), and metadata.
    """
    state_a_id = preset_config["state_a"]
    state_b_id = preset_config["state_b"]

    vec_a = np.array(GLIA_TYPES[state_a_id]["coordinates"])
    vec_b = np.array(GLIA_TYPES[state_b_id]["coordinates"])

    num_cycles = preset_config["num_cycles"]
    steps_per_cycle = preset_config["steps_per_cycle"]
    total_steps = num_cycles * steps_per_cycle

    alpha = _generate_oscillation(total_steps, num_cycles, preset_config["pattern"])

    trajectory = np.outer(1.0 - alpha, vec_a) + np.outer(alpha, vec_b)

    states = []
    per_step = []
    for i in range(total_steps):
        coord_dict = {
            dim: round(float(trajectory[i, j]), 4)
            for j, dim in enumerate(GLIA_PARAMETER_NAMES)
        }
        states.append(coord_dict)

        per_step.append({
            "step": i,
            "alpha": round(float(alpha[i]), 4),
            "coordinates": coord_dict,
        })

    return {
        "preset": preset_config,
        "state_a": state_a_id,
        "state_b": state_b_id,
        "total_steps": total_steps,
        "period": steps_per_cycle,
        "states": states,
        "per_step": per_step,
    }


def _extract_visual_vocabulary_from_params(
    params: dict,
    strength: float = 1.0,
) -> dict:
    """
    Map a 5D glia parameter state to nearest visual vocabulary type.

    Uses Euclidean distance in normalized parameter space.
    Returns nearest type, distance, and weighted keywords.
    """
    target = np.array([params.get(dim, 0.5) for dim in GLIA_PARAMETER_NAMES])
    min_dist = float("inf")
    nearest_type = None
    nearest_entry = None

    for vtype_name, vtype_data in GLIA_VISUAL_TYPES.items():
        vtype_coords = np.array([
            vtype_data["coords"][dim] for dim in GLIA_PARAMETER_NAMES
        ])
        dist = float(np.linalg.norm(target - vtype_coords))
        if dist < min_dist:
            min_dist = dist
            nearest_type = vtype_name
            nearest_entry = vtype_data

    # Weight cutoff: if distance > 0.15, reduce keyword contribution
    effective_strength = strength
    if min_dist > 0.15:
        effective_strength = strength * max(0.0, 1.0 - (min_dist - 0.15) / 0.85)

    return {
        "nearest_type": nearest_type,
        "distance": round(min_dist, 4),
        "keywords": nearest_entry["keywords"] if nearest_entry else [],
        "strength": round(effective_strength, 4),
    }


# ── Phase 2.6 tools ─────────────────────────────────────────────

@mcp.tool()
def list_glia_presets() -> dict:
    """
    List all Phase 2.6 rhythmic presets with period, pattern, and
    state transition information.

    Periods: [14, 18, 20, 26, 30, 36]
    Patterns: sinusoidal, triangular, square
    """
    result = {}
    for name, cfg in GLIA_RHYTHMIC_PRESETS.items():
        result[name] = {
            "period": cfg["steps_per_cycle"],
            "pattern": cfg["pattern"],
            "num_cycles": cfg["num_cycles"],
            "total_steps": cfg["num_cycles"] * cfg["steps_per_cycle"],
            "state_a": cfg["state_a"],
            "state_b": cfg["state_b"],
            "description": cfg["description"],
        }
    return {
        "presets": result,
        "count": len(result),
        "periods": sorted(set(c["steps_per_cycle"] for c in GLIA_RHYTHMIC_PRESETS.values())),
        "period_strategy": {
            "14": "Gap-filler: fills 12-15 gap in global landscape",
            "18": "Sync: nuclear, catastrophe, diatom",
            "20": "Sync: microscopy, catastrophe, diatom",
            "26": "Gap-filler: fills 25-30 gap (near discovered Period 27)",
            "30": "Sync: microscopy, diatom, heraldic (major hub Period 30)",
            "36": "LCM harmonics: 2×18, 3×12, novel higher-period resonance",
        },
    }


@mcp.tool()
def apply_glia_preset(
    preset_name: str,
    num_cycles: Optional[int] = None,
) -> dict:
    """
    Generate a forced orbit trajectory from a Phase 2.6 rhythmic preset.

    Guaranteed periodic closure, zero drift. Returns per-step coordinates
    suitable for driving frame-sequence animation or Tier 4D composition.

    preset_name: one of activation_cascade, network_pulse, myelination_rhythm,
                 developmental_arc, surveillance_sweep, structural_remodeling
    num_cycles: override default cycle count (optional)
    """
    if preset_name not in GLIA_RHYTHMIC_PRESETS:
        available = ", ".join(sorted(GLIA_RHYTHMIC_PRESETS.keys()))
        return {"error": f"Unknown preset: '{preset_name}'. Available: {available}"}

    cfg = dict(GLIA_RHYTHMIC_PRESETS[preset_name])
    if num_cycles is not None:
        cfg["num_cycles"] = max(1, min(20, num_cycles))

    traj = _generate_preset_trajectory(cfg)

    # Compute visual translations at key points (start, quarter, half, three-quarter)
    key_indices = [0, len(traj["states"]) // 4, len(traj["states"]) // 2,
                   3 * len(traj["states"]) // 4]
    key_translations = []
    for idx in key_indices:
        coords = [traj["states"][idx][dim] for dim in GLIA_PARAMETER_NAMES]
        translation = translate_coordinates(coords)
        key_translations.append({
            "step": idx,
            "coordinates": traj["states"][idx],
            "composed_specification": translation["composed_specification"],
        })

    return {
        "preset": preset_name,
        "period": traj["period"],
        "pattern": cfg["pattern"],
        "total_steps": traj["total_steps"],
        "state_a": {
            "id": traj["state_a"],
            "name": GLIA_TYPES[traj["state_a"]]["name"],
        },
        "state_b": {
            "id": traj["state_b"],
            "name": GLIA_TYPES[traj["state_b"]]["name"],
        },
        "key_translations": key_translations,
        "trajectory": traj["per_step"],
    }


@mcp.tool()
def compute_glia_trajectory_between_states(
    start_state: str,
    end_state: str,
    num_steps: int = 60,
) -> dict:
    """
    Compute smooth interpolation trajectory between two canonical glia states.

    Uses forced orbit (single half-cycle sinusoidal) for smooth transition.
    Distinct from compute_glia_trajectory which uses RK4 gradient integration —
    this uses the Phase 2.6 forced orbit method for guaranteed smoothness.

    Returns per-step coordinates with visual translations at key frames.
    """
    if start_state not in GLIA_TYPES:
        return {"error": f"Unknown state: '{start_state}'"}
    if end_state not in GLIA_TYPES:
        return {"error": f"Unknown state: '{end_state}'"}

    num_steps = max(5, min(200, num_steps))

    vec_a = np.array(GLIA_TYPES[start_state]["coordinates"])
    vec_b = np.array(GLIA_TYPES[end_state]["coordinates"])

    # Smooth sinusoidal interpolation (half cycle: 0 → 1)
    t = np.linspace(0, np.pi, num_steps)
    alpha = 0.5 * (1.0 - np.cos(t))

    trajectory = np.outer(1.0 - alpha, vec_a) + np.outer(alpha, vec_b)

    states = []
    for i in range(num_steps):
        states.append({
            dim: round(float(trajectory[i, j]), 4)
            for j, dim in enumerate(GLIA_PARAMETER_NAMES)
        })

    # Visual translations at 5 key frames
    key_indices = [0, num_steps // 4, num_steps // 2, 3 * num_steps // 4, num_steps - 1]
    key_frames = []
    for idx in key_indices:
        coords = [states[idx][dim] for dim in GLIA_PARAMETER_NAMES]
        translation = translate_coordinates(coords)
        key_frames.append({
            "step": idx,
            "alpha": round(float(alpha[idx]), 4),
            "coordinates": states[idx],
            "composed_specification": translation["composed_specification"],
        })

    return {
        "start_state": start_state,
        "end_state": end_state,
        "num_steps": num_steps,
        "method": "forced_orbit_sinusoidal",
        "key_frames": key_frames,
        "trajectory": [
            {"step": i, "alpha": round(float(alpha[i]), 4), "coordinates": s}
            for i, s in enumerate(states)
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# PHASE 2.7 — Attractor Visualization Prompt Generation (Layer 2)
# ═══════════════════════════════════════════════════════════════════
#
# Visual vocabulary types map 5D morphospace regions to image-generation
# keywords. Each type anchored at a canonical glia state, with 6-8
# keywords optimized for text-to-image prompt composition.

GLIA_VISUAL_TYPES = {
    "stellate_syncytium": {
        "coords": {
            "branching_complexity": 0.85,
            "activation_energy": 0.20,
            "network_connectivity": 0.90,
            "signal_propagation": 0.75,
            "structural_role": 0.40,
        },
        "keywords": [
            "stellate radiating processes from central soma",
            "gap-junction mesh connecting tiled territories",
            "calcium wave propagation across syncytial network",
            "bushy cloud-like process canopy",
            "non-overlapping domain tiling at 120° intervals",
            "cool-to-amber wavefront gradient",
        ],
        "anchored_to": "astrocyte_protoplasmic",
    },
    "phagocytic_burst": {
        "coords": {
            "branching_complexity": 0.15,
            "activation_energy": 0.95,
            "network_connectivity": 0.35,
            "signal_propagation": 0.80,
            "structural_role": 0.10,
        },
        "keywords": [
            "compact intense rounded mass",
            "pseudopod extensions at 45° intervals",
            "hot white-yellow core with orange-red membrane",
            "directional migration vectors",
            "concentrated phagocytic energy",
            "sharp 4:1 contrast ratio against background",
        ],
        "anchored_to": "microglia_amoeboid",
    },
    "myelinating_lattice": {
        "coords": {
            "branching_complexity": 0.45,
            "activation_energy": 0.10,
            "network_connectivity": 0.50,
            "signal_propagation": 0.15,
            "structural_role": 0.85,
        },
        "keywords": [
            "concentric wrapping geometry around axon segments",
            "segmented myelination with node-of-Ranvier punctuation",
            "organized insulating layers",
            "cool-blue low-saturation palette",
            "rigid structural scaffolding lines",
            "rhythmic repeating internode pattern",
        ],
        "anchored_to": "oligodendrocyte",
    },
    "surveillance_fractal": {
        "coords": {
            "branching_complexity": 0.90,
            "activation_energy": 0.10,
            "network_connectivity": 0.20,
            "signal_propagation": 0.30,
            "structural_role": 0.10,
        },
        "keywords": [
            "fractal branching at 15° radial intervals",
            "delicate exploratory processes filling spatial domain",
            "high-frequency fine detail on small footprint",
            "isolated element in negative space",
            "cool diffuse ambient glow",
            "watchful surveillance morphology",
        ],
        "anchored_to": "microglia_ramified",
    },
    "ciliary_flow": {
        "coords": {
            "branching_complexity": 0.20,
            "activation_energy": 0.10,
            "network_connectivity": 0.75,
            "signal_propagation": 0.60,
            "structural_role": 0.55,
        },
        "keywords": [
            "ciliated columnar packing along ventricle surface",
            "directional flow pattern with wave texture",
            "coordinated rhythmic beating",
            "mesh network at regular spacing",
            "propagating calcium-wave gradient",
            "uniform epithelial surface with structural weight",
        ],
        "anchored_to": "ependymal",
    },
    "developmental_scaffold": {
        "coords": {
            "branching_complexity": 0.30,
            "activation_energy": 0.10,
            "network_connectivity": 0.30,
            "signal_propagation": 0.20,
            "structural_role": 0.95,
        },
        "keywords": [
            "bipolar vertical axis spanning full field height",
            "migration-guide scaffold geometry",
            "rigid columnar organization",
            "dominant structural mass at 0.95 opacity",
            "frozen static composition",
            "architectural anchor with parallel alignment",
        ],
        "anchored_to": "radial_glia",
    },
    "transitional_progenitor": {
        "coords": {
            "branching_complexity": 0.60,
            "activation_energy": 0.40,
            "network_connectivity": 0.45,
            "signal_propagation": 0.35,
            "structural_role": 0.30,
        },
        "keywords": [
            "multipolar exploratory branching at 60° intervals",
            "transitional morphology between states",
            "moderate process density with visible primaries",
            "cool-to-neutral palette with green-yellow process tips",
            "loosely coupled small cluster",
            "proliferative potential in uncommitted form",
        ],
        "anchored_to": "ng2_opc",
    },
}


# ── Phase 2.7 tools ─────────────────────────────────────────────

@mcp.tool()
def get_glia_visual_types() -> dict:
    """
    List all glia visual vocabulary types with their 5D coordinates
    and image-generation keywords.

    Each type anchors a region of glia morphospace and provides 6-8
    keywords optimized for text-to-image prompt composition (ComfyUI,
    Stable Diffusion, DALL-E).
    """
    result = {}
    for vtype_name, vtype_data in GLIA_VISUAL_TYPES.items():
        result[vtype_name] = {
            "coordinates": vtype_data["coords"],
            "keywords": vtype_data["keywords"],
            "anchored_to": vtype_data["anchored_to"],
        }
    return {
        "visual_types": result,
        "count": len(result),
        "parameter_names": GLIA_PARAMETER_NAMES,
    }


@mcp.tool()
def generate_glia_attractor_prompt(
    state: Optional[dict] = None,
    glia_type: Optional[str] = None,
    mode: str = "composite",
    strength: float = 1.0,
) -> dict:
    """
    Generate image-generation-ready prompt from a 5D glia parameter state.

    Three modes:
      composite  — single blended prompt combining nearest visual vocabulary
      split_view — separate prompt per morphospace region (for multi-panel)
      sequence   — keyframe prompts for animated transitions

    Provide either:
      state: dict of {branching_complexity, activation_energy, ...} values [0-1]
      glia_type: canonical type name (uses its default coordinates)

    strength: 0.0-1.0, controls keyword weighting in cross-domain composition
    """
    if glia_type and glia_type in GLIA_TYPES:
        params = {
            dim: coord
            for dim, coord in zip(GLIA_PARAMETER_NAMES, GLIA_TYPES[glia_type]["coordinates"])
        }
    elif state:
        params = {dim: state.get(dim, 0.5) for dim in GLIA_PARAMETER_NAMES}
    else:
        return {
            "error": "Provide either 'state' (dict of parameter values) or "
                     "'glia_type' (canonical type name)."
        }

    strength = max(0.0, min(1.0, strength))

    # Find nearest visual type
    vocab = _extract_visual_vocabulary_from_params(params, strength)

    # Get full visual translation
    coords_list = [params[dim] for dim in GLIA_PARAMETER_NAMES]
    translation = translate_coordinates(coords_list)

    if mode == "composite":
        # Blend keywords with geometric specification
        weighted_keywords = vocab["keywords"][:int(len(vocab["keywords"]) * max(0.3, vocab["strength"]))] if vocab["keywords"] else []
        prompt_parts = weighted_keywords + [translation["composed_specification"]]
        prompt = ", ".join(prompt_parts)

        return {
            "mode": "composite",
            "prompt": prompt,
            "nearest_visual_type": vocab["nearest_type"],
            "distance": vocab["distance"],
            "strength": vocab["strength"],
            "coordinates": params,
            "keywords_used": len(weighted_keywords),
            "total_keywords": len(vocab["keywords"]),
        }

    elif mode == "split_view":
        # Per-dimension breakdown for multi-panel composition
        panels = {}
        for dim_name in GLIA_PARAMETER_NAMES:
            dim_val = params[dim_name]
            dim_key = f"D{GLIA_PARAMETER_NAMES.index(dim_name)+1}_{dim_name}"
            trans_fn = {
                "branching_complexity": translate_branching,
                "activation_energy": translate_activation,
                "network_connectivity": translate_connectivity,
                "signal_propagation": translate_signal_propagation,
                "structural_role": translate_structural_role,
            }[dim_name]
            dim_trans = trans_fn(dim_val)
            panels[dim_key] = {
                "value": round(dim_val, 4),
                "translation": dim_trans,
            }

        return {
            "mode": "split_view",
            "panels": panels,
            "nearest_visual_type": vocab["nearest_type"],
            "distance": vocab["distance"],
            "coordinates": params,
            "composed_specification": translation["composed_specification"],
        }

    elif mode == "sequence":
        # Generate keyframe prompts along a preset trajectory
        # Find the preset whose states are closest to this point
        best_preset = None
        best_dist = float("inf")
        target_vec = np.array([params[dim] for dim in GLIA_PARAMETER_NAMES])

        for pname, pcfg in GLIA_RHYTHMIC_PRESETS.items():
            mid_a = np.array(GLIA_TYPES[pcfg["state_a"]]["coordinates"])
            mid_b = np.array(GLIA_TYPES[pcfg["state_b"]]["coordinates"])
            midpoint = 0.5 * (mid_a + mid_b)
            dist = float(np.linalg.norm(target_vec - midpoint))
            if dist < best_dist:
                best_dist = dist
                best_preset = pname

        # Generate trajectory for matched preset
        traj = _generate_preset_trajectory(GLIA_RHYTHMIC_PRESETS[best_preset])

        # Sample 6 keyframes
        n_keys = min(6, traj["total_steps"])
        key_indices = [int(i * (traj["total_steps"] - 1) / (n_keys - 1)) for i in range(n_keys)]

        keyframes = []
        for idx in key_indices:
            kf_params = traj["states"][idx]
            kf_coords = [kf_params[dim] for dim in GLIA_PARAMETER_NAMES]
            kf_trans = translate_coordinates(kf_coords)
            kf_vocab = _extract_visual_vocabulary_from_params(kf_params, strength)
            kf_keywords = kf_vocab["keywords"][:4] if kf_vocab["keywords"] else []
            keyframes.append({
                "step": idx,
                "coordinates": kf_params,
                "prompt": ", ".join(kf_keywords + [kf_trans["composed_specification"]]),
                "nearest_type": kf_vocab["nearest_type"],
            })

        return {
            "mode": "sequence",
            "matched_preset": best_preset,
            "preset_distance": round(best_dist, 4),
            "period": traj["period"],
            "total_steps": traj["total_steps"],
            "keyframes": keyframes,
        }

    else:
        return {"error": f"Unknown mode: '{mode}'. Use 'composite', 'split_view', or 'sequence'."}


@mcp.tool()
def get_glia_domain_registry_config() -> dict:
    """
    Export domain configuration for Tier 4D compositional limit cycle discovery.

    Returns the full registry entry needed to add glia to the emergent
    attractor characterization system: parameter names, state coordinates,
    preset periods, and predicted emergent attractors with basin size estimates.
    """
    presets_export = {}
    for name, cfg in GLIA_RHYTHMIC_PRESETS.items():
        presets_export[name] = {
            "period": cfg["steps_per_cycle"],
            "state_a": cfg["state_a"],
            "state_b": cfg["state_b"],
            "pattern": cfg["pattern"],
        }

    periods = sorted(set(c["steps_per_cycle"] for c in GLIA_RHYTHMIC_PRESETS.values()))

    # Predicted emergent attractors based on period interactions
    predicted_attractors = {
        "period_30_reinforcement": {
            "period": 30,
            "mechanism": "LCM synchronization",
            "domains_involved": ["glia", "microscopy", "diatom", "heraldic"],
            "predicted_basin_size": 0.12,
            "confidence": "high",
            "notes": "Glia Period 30 (developmental_arc) reinforces the strongest "
                     "known cross-domain hub. Expected to strengthen Period 30 basin.",
        },
        "period_14_gap_filler": {
            "period": 14,
            "mechanism": "Gap-filling (12-15)",
            "domains_involved": ["glia"],
            "predicted_basin_size": 0.04,
            "confidence": "medium",
            "notes": "Novel period filling the 12-15 gap. May create new attractor "
                     "or interact with Period 15 harmonics.",
        },
        "period_36_lcm_hub": {
            "period": 36,
            "mechanism": "LCM(12, 18, 36) harmonic hub",
            "domains_involved": ["glia", "diatom", "nuclear", "catastrophe"],
            "predicted_basin_size": 0.05,
            "confidence": "medium",
            "notes": "2×18 and 3×12 create multi-domain synchronization. "
                     "May strengthen or create basin near Period 36.",
        },
        "period_26_gap_filler": {
            "period": 26,
            "mechanism": "Gap-filling (25-30)",
            "domains_involved": ["glia"],
            "predicted_basin_size": 0.03,
            "confidence": "medium",
            "notes": "Near the discovered Period 27 gap-filler. May compete, "
                     "merge, or create a distinct basin.",
        },
        "composite_beat_candidate": {
            "period": 22,
            "mechanism": "Composite beat: 36 - 14 = 22",
            "domains_involved": ["glia"],
            "predicted_basin_size": 0.02,
            "confidence": "low",
            "notes": "If Period 36 and Period 14 both establish basins, their "
                     "difference frequency may stabilize. Speculative.",
        },
    }

    return {
        "domain_id": "glia",
        "display_name": "Glia Visual Vocabulary",
        "mcp_server": "glia-visual-vocabulary",
        "parameter_names": GLIA_PARAMETER_NAMES,
        "parameter_count": len(GLIA_PARAMETER_NAMES),
        "state_coordinates": GLIA_STATE_COORDINATES,
        "state_count": len(GLIA_STATE_COORDINATES),
        "presets": presets_export,
        "preset_count": len(presets_export),
        "periods": periods,
        "visual_types": {
            name: {
                "coords": vt["coords"],
                "keyword_count": len(vt["keywords"]),
            }
            for name, vt in GLIA_VISUAL_TYPES.items()
        },
        "visual_type_count": len(GLIA_VISUAL_TYPES),
        "predicted_emergent_attractors": predicted_attractors,
        "tier_4d_integration": {
            "ready": True,
            "phase_2_6": True,
            "phase_2_7": True,
            "forced_orbit": True,
            "registration_function": "register_glia_domain",
        },
    }


# ═══════════════════════════════════════════════════════════════════
# LAYER 3 — Claude Synthesis (~100-200 tokens)
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def enhance_prompt_with_glia(
    base_prompt: str,
    glia_type: str,
    activation_intensity: Optional[float] = None,
    style: Optional[str] = None,
    context: Optional[str] = None,
) -> dict:
    """
    Enhance a base prompt with glia visual vocabulary.
    
    Layer 3 tool: uses Claude to synthesize the base prompt with
    deterministically resolved morphospace specifications.
    
    glia_type: any of the 9 canonical types
    activation_intensity: 0.0-1.0, only for microglia/astrocyte types
    style: photorealistic, abstract, surreal, stylized, or custom string
    context: scientific, artistic, educational, or custom string
    
    Returns: enhanced prompt with explicit geometric specifications.
    """
    if glia_type not in GLIA_TYPES:
        available = ", ".join(sorted(GLIA_TYPES.keys()))
        return {"error": f"Unknown glia type: '{glia_type}'. Available: {available}"}
    
    # Resolve coordinates (Layer 2 operation)
    coords = list(GLIA_TYPES[glia_type]["coordinates"])
    if activation_intensity is not None:
        traj_key = None
        if glia_type.startswith("microglia"):
            traj_key = "microglia"
        elif glia_type.startswith("astrocyte"):
            traj_key = "astrocyte"
        if traj_key and traj_key in ACTIVATION_TRAJECTORIES:
            keyframes = {
                k: v["coords"]
                for k, v in ACTIVATION_TRAJECTORIES[traj_key]["states"].items()
            }
            coords = interpolate_activation(keyframes, activation_intensity)
    
    # Translate coordinates to visual vocabulary (Layer 1/2 operation)
    translation = translate_coordinates(coords)
    gt = GLIA_TYPES[glia_type]
    
    # Build context for Claude
    enhancement_context = build_enhancement_context(
        glia_type=glia_type,
        glia_profile=gt,
        visual_translation=translation,
        base_prompt=base_prompt,
        style=style,
        context=context,
    )
    
    return {
        "type": glia_type,
        "activation_intensity": activation_intensity,
        "coordinates_used": {
            dim: round(val, 4) for dim, val in zip(DIMENSION_NAMES, coords)
        },
        "enhancement_context": enhancement_context,
        "system_prompt": ENHANCEMENT_SYSTEM_PROMPT,
        "note": "Pass enhancement_context as user message and system_prompt as system "
                "message to Claude for creative synthesis. Or use directly as structured "
                "prompt context for any LLM.",
    }


@mcp.tool()
def generate_frame_sequence(
    base_prompt: str,
    start_type: str,
    end_type: str,
    num_frames: int = 12,
    fps: float = 12.0,
    num_trajectory_steps: int = 60,
    use_activation_path: bool = False,
    style: Optional[str] = None,
    context: Optional[str] = None,
) -> dict:
    """
    Generate per-frame prompt specifications for video/animation.
    
    Computes a trajectory through 5D morphospace (either point-to-point
    or along a biological activation path), then samples frames and
    generates per-frame geometric specifications.
    
    use_activation_path: if True and types are microglia or astrocyte
    variants, follows the biological activation trajectory instead of
    a direct morphospace path.
    
    Returns: frame sequence context ready for Claude synthesis,
    plus per-frame coordinates and visual translations.
    """
    if start_type not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{start_type}'"}
    if end_type not in GLIA_TYPES:
        return {"error": f"Unknown glia type: '{end_type}'"}
    
    num_frames = max(2, min(120, num_frames))
    num_trajectory_steps = max(num_frames, min(200, num_trajectory_steps))
    
    # Compute trajectory
    if use_activation_path:
        # Determine if we can use activation path
        traj_key = None
        if start_type.startswith("microglia") and end_type.startswith("microglia"):
            traj_key = "microglia"
        elif start_type.startswith("astrocyte") and end_type.startswith("astrocyte"):
            traj_key = "astrocyte"
        
        if traj_key:
            traj = ACTIVATION_TRAJECTORIES[traj_key]
            keyframes = {k: v["coords"] for k, v in traj["states"].items()}
            base_coords = GLIA_TYPES[traj["base_type"]]["coordinates"]
            
            trajectory = compute_activation_trajectory(
                base_coords=base_coords,
                activation_keyframes=keyframes,
                num_steps=num_trajectory_steps,
                dimension_names=DIMENSION_NAMES,
            )
        else:
            # Fall back to direct trajectory
            trajectory = compute_trajectory(
                GLIA_TYPES[start_type]["coordinates"],
                GLIA_TYPES[end_type]["coordinates"],
                num_steps=num_trajectory_steps,
                dimension_names=DIMENSION_NAMES,
            )
    else:
        trajectory = compute_trajectory(
            GLIA_TYPES[start_type]["coordinates"],
            GLIA_TYPES[end_type]["coordinates"],
            num_steps=num_trajectory_steps,
            dimension_names=DIMENSION_NAMES,
        )
    
    # Generate visual translations for each trajectory state
    visual_translations_seq = [
        translate_coordinates(state)
        for state in trajectory["states"]
    ]
    
    # Build frame sequence context
    frame_context = build_frame_sequence_context(
        trajectory_states=trajectory["states"],
        trajectory_per_step=trajectory["per_step"],
        glia_type_start=start_type,
        glia_type_end=end_type,
        profile_start=GLIA_TYPES[start_type],
        profile_end=GLIA_TYPES[end_type],
        visual_translations_sequence=visual_translations_seq,
        base_prompt=base_prompt,
        num_frames=num_frames,
        fps=fps,
        style=style,
        context=context,
    )
    
    # Also return sampled frame data for direct use
    total_steps = len(trajectory["states"])
    if total_steps <= num_frames:
        frame_indices = list(range(total_steps))
    else:
        frame_indices = [
            int(i * (total_steps - 1) / (num_frames - 1))
            for i in range(num_frames)
        ]
    
    sampled_frames = []
    for frame_num, idx in enumerate(frame_indices):
        vt = visual_translations_seq[idx]
        coords = trajectory["states"][idx]
        sampled_frames.append({
            "frame": frame_num + 1,
            "trajectory_index": idx,
            "coordinates": {
                dim: round(val, 4)
                for dim, val in zip(DIMENSION_NAMES, coords)
            },
            "composed_specification": vt["composed_specification"],
        })
    
    return {
        "start_type": GLIA_TYPES[start_type]["name"],
        "end_type": GLIA_TYPES[end_type]["name"],
        "num_frames": num_frames,
        "fps": fps,
        "duration_seconds": round(num_frames / fps, 2),
        "used_activation_path": use_activation_path and traj_key is not None if use_activation_path else False,
        "trajectory_analysis": trajectory["analysis"],
        "sampled_frames": sampled_frames,
        "frame_sequence_context": frame_context,
        "system_prompt": FRAME_SEQUENCE_SYSTEM_PROMPT,
        "note": "Pass frame_sequence_context as user message and system_prompt as system "
                "message to Claude. Claude returns a JSON array of per-frame prompts.",
    }

if __name__ == "__main__":
    mcp.run()
