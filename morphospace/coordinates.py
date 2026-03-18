"""
Coordinate Operations — distance computation, nearest-neighbor search.
"""

from typing import List, Dict, Optional, Tuple
from .trajectory import euclidean_distance, per_dimension_deltas

# Dimension names used throughout
DIMENSION_NAMES = [
    "branching_complexity",
    "activation_energy",
    "network_connectivity",
    "signal_propagation",
    "structural_role",
]


def compute_distance(
    coords_a: List[float],
    coords_b: List[float],
    label_a: str = "A",
    label_b: str = "B",
) -> Dict:
    """Compute Euclidean distance and per-dimension deltas between two points."""
    dist = euclidean_distance(coords_a, coords_b)
    deltas = per_dimension_deltas(coords_a, coords_b)
    
    return {
        "distance": round(dist, 4),
        "from": label_a,
        "to": label_b,
        "per_dimension": {
            name: {
                "from": round(a, 4),
                "to": round(b, 4),
                "delta": round(d, 4),
                "abs_delta": round(abs(d), 4),
            }
            for name, a, b, d in zip(DIMENSION_NAMES, coords_a, coords_b, deltas)
        },
        "dominant_dimension": DIMENSION_NAMES[
            max(range(len(deltas)), key=lambda i: abs(deltas[i]))
        ],
    }


def find_nearest(
    target_coords: List[float],
    candidates: Dict[str, List[float]],
    exclude: Optional[List[str]] = None,
    max_results: int = 5,
    max_distance: Optional[float] = None,
) -> List[Dict]:
    """
    Find nearest glia types to a target position in morphospace.
    
    Args:
        target_coords: 5D coordinate vector
        candidates: Dict of {type_name: coordinates}
        exclude: Type names to exclude from results
        max_results: Maximum number of results
        max_distance: Optional distance threshold
    
    Returns:
        List of {type, distance, coordinates, per_dimension_deltas} sorted by distance
    """
    exclude = exclude or []
    
    results = []
    for name, coords in candidates.items():
        if name in exclude:
            continue
        dist = euclidean_distance(target_coords, coords)
        if max_distance is not None and dist > max_distance:
            continue
        results.append({
            "type": name,
            "distance": round(dist, 4),
            "coordinates": {
                dim: round(v, 4) for dim, v in zip(DIMENSION_NAMES, coords)
            },
        })
    
    results.sort(key=lambda x: x["distance"])
    return results[:max_results]


def interpolate_activation(
    keyframes: Dict[float, List[float]],
    activation_intensity: float,
) -> List[float]:
    """
    Interpolate 5D coordinates at a specific activation intensity
    using linear interpolation between the nearest keyframes.
    
    This is the fast path for single-point lookups when you don't
    need a full trajectory. All 5 dimensions shift simultaneously.
    """
    sorted_keys = sorted(keyframes.keys())
    
    # Clamp to valid range
    if activation_intensity <= sorted_keys[0]:
        return list(keyframes[sorted_keys[0]])
    if activation_intensity >= sorted_keys[-1]:
        return list(keyframes[sorted_keys[-1]])
    
    # Find bracketing keyframes
    for i in range(len(sorted_keys) - 1):
        if sorted_keys[i] <= activation_intensity <= sorted_keys[i + 1]:
            t_low = sorted_keys[i]
            t_high = sorted_keys[i + 1]
            coords_low = keyframes[t_low]
            coords_high = keyframes[t_high]
            
            # Linear interpolation factor
            frac = (activation_intensity - t_low) / (t_high - t_low)
            
            return [
                low + frac * (high - low)
                for low, high in zip(coords_low, coords_high)
            ]
    
    # Fallback (shouldn't reach here)
    return list(keyframes[sorted_keys[0]])
