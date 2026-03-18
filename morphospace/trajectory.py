"""
Vendored RK4 Trajectory Computation — from aesthetic-dynamics-core

4th-order Runge-Kutta integration through N-dimensional morphospace.
Produces smooth interpolated paths between two coordinate positions,
with convergence analysis and path efficiency metrics.

Vendored rather than imported as a dependency to keep FastMCP Cloud
deployment clean (empty dependencies in pyproject.toml).
"""

import math
from typing import List, Dict, Tuple, Optional


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp value to range."""
    return max(low, min(high, value))


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """Euclidean distance between two N-dimensional coordinate vectors."""
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def per_dimension_deltas(a: List[float], b: List[float]) -> List[float]:
    """Per-dimension signed deltas from a to b."""
    return [bi - ai for ai, bi in zip(a, b)]


def _sigmoid_progress(t: float, k: float = 6.0) -> float:
    """
    Compute sigmoid-shaped progress from 0→1.
    
    Produces slow departure, rapid midpoint transition, slow arrival —
    biologically plausible for state transitions.
    """
    return 1.0 / (1.0 + math.exp(-k * (t - 0.5)))


# Precompute normalization so sigmoid(0)→0.0 and sigmoid(1)→1.0
_SIG_K = 6.0
_SIG_AT_0 = _sigmoid_progress(0.0, _SIG_K)
_SIG_AT_1 = _sigmoid_progress(1.0, _SIG_K)


def _normalized_sigmoid(t: float) -> float:
    """Sigmoid normalized to exactly [0, 1] at endpoints."""
    raw = _sigmoid_progress(t, _SIG_K)
    return (raw - _SIG_AT_0) / (_SIG_AT_1 - _SIG_AT_0)


def _velocity_field(
    current: List[float],
    target: List[float],
    t: float,
    total_t: float,
    start: List[float],
) -> List[float]:
    """
    Compute velocity for sigmoid-shaped interpolation.
    
    Uses the derivative of normalized sigmoid to produce smooth
    acceleration/deceleration while guaranteeing exact convergence.
    The position at time t is: start + sigmoid(t) * (target - start),
    so velocity = sigmoid'(t) * (target - start).
    """
    s = t / total_t if total_t > 0 else 0.5
    # Derivative of normalized sigmoid
    raw_sig = _sigmoid_progress(s, _SIG_K)
    raw_deriv = _SIG_K * raw_sig * (1.0 - raw_sig)
    norm_deriv = raw_deriv / (_SIG_AT_1 - _SIG_AT_0)
    
    full_delta = per_dimension_deltas(start, target)
    return [d * norm_deriv / total_t for d in full_delta]


def rk4_step(
    state: List[float],
    target: List[float],
    t: float,
    dt: float,
    total_t: float,
    start: List[float],
) -> List[float]:
    """Single RK4 integration step through morphospace."""
    k1 = _velocity_field(state, target, t, total_t, start)
    
    state_k2 = [s + 0.5 * dt * k for s, k in zip(state, k1)]
    k2 = _velocity_field(state_k2, target, t + 0.5 * dt, total_t, start)
    
    state_k3 = [s + 0.5 * dt * k for s, k in zip(state, k2)]
    k3 = _velocity_field(state_k3, target, t + 0.5 * dt, total_t, start)
    
    state_k4 = [s + dt * k for s, k in zip(state, k3)]
    k4 = _velocity_field(state_k4, target, t + dt, total_t, start)
    
    new_state = [
        _clamp(s + (dt / 6.0) * (a + 2 * b + 2 * c + d))
        for s, a, b, c, d in zip(state, k1, k2, k3, k4)
    ]
    return new_state


def compute_trajectory(
    start: List[float],
    end: List[float],
    num_steps: int = 30,
    dimension_names: Optional[List[str]] = None,
) -> Dict:
    """
    Compute RK4-integrated trajectory between two positions in morphospace.
    
    Returns:
        Dict with:
            - states: list of coordinate vectors at each step
            - analysis: convergence metrics, path efficiency
            - per_step: per-step metadata (distance remaining, velocity magnitude)
    """
    if dimension_names is None:
        dimension_names = [f"D{i+1}" for i in range(len(start))]
    
    total_t = 1.0
    dt = total_t / num_steps
    
    states = [list(start)]
    current = list(start)
    
    total_path_length = 0.0
    per_step_data = []
    
    for step in range(num_steps):
        t = step * dt
        prev = list(current)
        current = rk4_step(current, end, t, dt, total_t, start)
        states.append(list(current))
        
        step_distance = euclidean_distance(prev, current)
        total_path_length += step_distance
        remaining = euclidean_distance(current, end)
        
        per_step_data.append({
            "step": step + 1,
            "t": round(t + dt, 4),
            "coordinates": {name: round(v, 4) for name, v in zip(dimension_names, current)},
            "step_distance": round(step_distance, 4),
            "remaining_distance": round(remaining, 4),
        })
    
    # Analysis
    straight_line = euclidean_distance(start, end)
    path_efficiency = straight_line / total_path_length if total_path_length > 0 else 1.0
    final_error = euclidean_distance(states[-1], end)
    
    analysis = {
        "straight_line_distance": round(straight_line, 4),
        "total_path_length": round(total_path_length, 4),
        "path_efficiency": round(path_efficiency, 4),
        "final_convergence_error": round(final_error, 6),
        "num_steps": num_steps,
        "converged": final_error < 0.01,
    }
    
    return {
        "start": {name: round(v, 4) for name, v in zip(dimension_names, start)},
        "end": {name: round(v, 4) for name, v in zip(dimension_names, end)},
        "states": states,
        "analysis": analysis,
        "per_step": per_step_data,
    }


def compute_activation_trajectory(
    base_coords: List[float],
    activation_keyframes: Dict[float, List[float]],
    num_steps: int = 30,
    start_activation: float = 0.0,
    end_activation: float = 1.0,
    dimension_names: Optional[List[str]] = None,
) -> Dict:
    """
    Compute trajectory along a biological activation path.
    
    Unlike compute_trajectory (which goes point-to-point), this follows
    a keyframed path through morphospace where intermediate waypoints
    are biologically defined (e.g., ramified → hypertrophic → bushy → amoeboid).
    
    activation_keyframes: {activation_level: coordinates} — sorted by key
    Each coordinate set represents a biologically characterized state.
    The trajectory interpolates smoothly between these waypoints.
    """
    if dimension_names is None:
        dimension_names = [f"D{i+1}" for i in range(len(base_coords))]
    
    # Sort keyframes
    sorted_keys = sorted(activation_keyframes.keys())
    
    # Build piecewise trajectory through keyframe waypoints
    states = []
    per_step_data = []
    total_path_length = 0.0
    
    steps_per_segment = max(1, num_steps // max(1, len(sorted_keys) - 1))
    
    for i in range(len(sorted_keys) - 1):
        seg_start_activation = sorted_keys[i]
        seg_end_activation = sorted_keys[i + 1]
        seg_start_coords = activation_keyframes[seg_start_activation]
        seg_end_coords = activation_keyframes[seg_end_activation]
        
        # RK4 between this pair of keyframes
        segment = compute_trajectory(
            seg_start_coords, seg_end_coords, steps_per_segment, dimension_names
        )
        
        # Collect states (skip first of subsequent segments to avoid duplicates)
        start_idx = 0 if i == 0 else 1
        for j, step_data in enumerate(segment["per_step"][start_idx:], start=len(per_step_data)):
            # Map t back to activation space
            local_t = step_data["t"]
            activation = seg_start_activation + local_t * (seg_end_activation - seg_start_activation)
            step_data["activation_intensity"] = round(activation, 4)
            step_data["step"] = j + 1
            per_step_data.append(step_data)
        
        seg_states = segment["states"][start_idx:]
        states.extend(seg_states)
        total_path_length += segment["analysis"]["total_path_length"]
    
    # Analysis
    full_start = activation_keyframes[sorted_keys[0]]
    full_end = activation_keyframes[sorted_keys[-1]]
    straight_line = euclidean_distance(full_start, full_end)
    path_efficiency = straight_line / total_path_length if total_path_length > 0 else 1.0
    
    analysis = {
        "straight_line_distance": round(straight_line, 4),
        "total_path_length": round(total_path_length, 4),
        "path_efficiency": round(path_efficiency, 4),
        "num_keyframes": len(sorted_keys),
        "num_steps_total": len(per_step_data),
        "start_activation": start_activation,
        "end_activation": end_activation,
    }
    
    return {
        "start": {name: round(v, 4) for name, v in zip(dimension_names, full_start)},
        "end": {name: round(v, 4) for name, v in zip(dimension_names, full_end)},
        "keyframes": {
            str(k): {name: round(v, 4) for name, v in zip(dimension_names, activation_keyframes[k])}
            for k in sorted_keys
        },
        "states": states,
        "analysis": analysis,
        "per_step": per_step_data,
    }
