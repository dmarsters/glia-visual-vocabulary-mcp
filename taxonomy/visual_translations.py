"""
Visual Translations — Maps 5D morphospace coordinates to image generation vocabulary.

Follows prompt preferences: explicit geometric specifications, not suggestive descriptions.
Output vocabulary uses angles, distances, densities, and spatial relationships.
"""

from typing import List, Dict


def _interpolate_descriptors(value: float, low_descs: List[str], high_descs: List[str]) -> List[str]:
    """Select descriptors based on parameter value along 0-1 range."""
    if value < 0.3:
        return low_descs
    elif value < 0.7:
        # Blend: take some from each
        mid_count = max(1, len(low_descs) // 2)
        return low_descs[:mid_count] + high_descs[:mid_count]
    else:
        return high_descs


def translate_branching(value: float) -> Dict:
    """D1: Branching Complexity → geometric specifications."""
    if value < 0.25:
        return {
            "geometry": "smooth rounded contour, minimal edge detail",
            "specification": f"process count: 0-2, branching order: 0, surface roughness index: {value:.2f}",
            "texture": "uniform membrane surface, no fractal detail",
        }
    elif value < 0.50:
        return {
            "geometry": f"moderate branching at {int(60 + (1-value)*60)}° intervals from soma",
            "specification": f"process count: 3-6, branching order: 1-2, surface roughness index: {value:.2f}",
            "texture": "visible primary processes, smooth secondary branches",
        }
    elif value < 0.75:
        return {
            "geometry": f"dense branching at {int(30 + (1-value)*30)}° radial intervals from central soma",
            "specification": f"process count: 8-15, branching order: 3-4, surface roughness index: {value:.2f}",
            "texture": "intricate secondary branching, visible tertiary processes",
        }
    else:
        return {
            "geometry": f"fractal branching at {int(15 + (1-value)*20)}° radial intervals, "
                        f"process density decreasing at r² from center point",
            "specification": f"process count: 15+, branching order: 5+, surface roughness index: {value:.2f}",
            "texture": "high-frequency fractal detail, dense fine processes filling spatial domain",
        }


def translate_activation(value: float) -> Dict:
    """D2: Activation Energy → color/intensity specifications."""
    if value < 0.25:
        return {
            "palette": "cool blues and cyans, low saturation, diffuse ambient luminance",
            "intensity": f"luminance: {0.2 + value * 0.3:.2f}, contrast ratio: 1.2:1",
            "energy_vector": "no directional energy, isotropic glow",
        }
    elif value < 0.50:
        return {
            "palette": "cool-to-neutral shift, hints of green/yellow at process tips",
            "intensity": f"luminance: {0.2 + value * 0.5:.2f}, contrast ratio: 1.8:1",
            "energy_vector": "mild radial energy gradient from soma outward",
        }
    elif value < 0.75:
        return {
            "palette": "warm amber-orange at soma, transitioning to cooler tones at process tips",
            "intensity": f"luminance: {0.2 + value * 0.7:.2f}, contrast ratio: 2.5:1",
            "energy_vector": f"directional energy vectors at {int(value * 360)}° primary axis",
        }
    else:
        return {
            "palette": "hot white-yellow core, intense orange-red at membrane, sharp contrast against background",
            "intensity": f"luminance: {0.2 + value * 0.8:.2f}, contrast ratio: 4:1",
            "energy_vector": f"concentrated energy mass with pseudopod vectors at {int(value * 45)}° intervals",
        }


def translate_connectivity(value: float) -> Dict:
    """D3: Network Connectivity → spatial relationship specifications."""
    if value < 0.25:
        return {
            "topology": "isolated element, surrounded by negative space",
            "bridges": "no visible connections to adjacent elements",
            "tiling": "single unit, no spatial domain boundaries",
        }
    elif value < 0.50:
        return {
            "topology": "loosely coupled pair or small cluster",
            "bridges": f"{int(value * 8)} thin bridge structures connecting to nearest neighbors",
            "tiling": "partial domain boundaries visible, some overlap permitted",
        }
    elif value < 0.75:
        return {
            "topology": "mesh network with regular spacing",
            "bridges": f"gap-junction bridges at {int(120 / (value + 0.5)):.0f}° spacing to adjacent domains",
            "tiling": "non-overlapping territory tiling, boundary zones visible between domains",
        }
    else:
        return {
            "topology": "dense syncytial mesh, continuous cytoplasmic network",
            "bridges": f"gap-junction bridges to adjacent tiling domains at ~120° spacing, "
                       f"bridge density: {value:.2f}",
            "tiling": "complete territory tiling with no gaps, each domain ~50-100μm diameter",
        }


def translate_signal_propagation(value: float) -> Dict:
    """D4: Signal Propagation → temporal/dynamic specifications."""
    if value < 0.25:
        return {
            "dynamics": "frozen static composition, no temporal gradient",
            "wavefront": "none",
            "color_shift": "uniform tone across all elements",
        }
    elif value < 0.50:
        return {
            "dynamics": "subtle standing-wave pattern, low-amplitude oscillation implied",
            "wavefront": f"wavefront width: {int(value * 200)}μm, velocity: slow",
            "color_shift": "mild hue variation (±10° on color wheel) from center outward",
        }
    elif value < 0.75:
        return {
            "dynamics": "propagating calcium-wave gradient rolling across syncytial domain",
            "wavefront": f"wavefront width: {int(value * 200)}μm, visible leading edge, "
                         f"trailing recovery zone",
            "color_shift": "cool-blue (quiescent) → warm-amber (active wavefront) → "
                           "cool recovery trailing the wave",
        }
    else:
        return {
            "dynamics": "intense propagating wave cascade across multiple domains, "
                        "interference patterns where waves meet",
            "wavefront": f"wavefront width: {int(value * 200)}μm, sharp leading edge, "
                         f"multiple simultaneous wavefronts",
            "color_shift": "dramatic hue shift along wavefront: deep blue → white-hot → "
                           "amber → recovery blue, visible interference fringes at wave collision points",
        }


def translate_structural_role(value: float) -> Dict:
    """D5: Structural Role → architectural specifications."""
    if value < 0.25:
        return {
            "weight": "floating, weightless, atmospheric presence",
            "alignment": "no preferred orientation, isotropic distribution",
            "architecture": "ambient element, no load-bearing geometry",
        }
    elif value < 0.50:
        return {
            "weight": f"moderate visual weight, {value:.2f} opacity anchoring",
            "alignment": "mild directional preference, partial alignment to tissue axis",
            "architecture": "contributing to tissue texture but not dominant structure",
        }
    elif value < 0.75:
        return {
            "weight": f"substantial visual weight, {value:.2f} opacity, clear structural presence",
            "alignment": "parallel alignment to primary tissue axis, regular spacing",
            "architecture": "visible scaffolding geometry, load-bearing lines, organized lattice",
        }
    else:
        return {
            "weight": f"dominant structural mass, {value:.2f} opacity, architectural anchor",
            "alignment": "rigid parallel alignment spanning full field, columnar organization",
            "architecture": "load-bearing scaffold geometry, vertical axis from base to apex, "
                            "migration-guide rails visible",
        }


def translate_coordinates(coordinates: List[float]) -> Dict:
    """
    Full 5D → visual vocabulary translation.
    
    Returns a dict with per-dimension translations and a composed specification string.
    """
    d1, d2, d3, d4, d5 = coordinates

    translations = {
        "branching": translate_branching(d1),
        "activation": translate_activation(d2),
        "connectivity": translate_connectivity(d3),
        "signal": translate_signal_propagation(d4),
        "structure": translate_structural_role(d5),
    }

    # Compose into a single geometric specification string
    composed = (
        f"{translations['branching']['geometry']}. "
        f"{translations['activation']['energy_vector']}. "
        f"{translations['connectivity']['bridges']}. "
        f"{translations['signal']['dynamics']}. "
        f"{translations['structure']['architecture']}. "
        f"Palette: {translations['activation']['palette']}. "
        f"Signal dynamics: {translations['signal']['color_shift']}."
    )

    translations["composed_specification"] = composed
    translations["coordinates"] = coordinates

    return translations
