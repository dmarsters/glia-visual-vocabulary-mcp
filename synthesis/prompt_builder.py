"""
Prompt Builder — Assembles deterministic morphospace data into structured context
for Layer 3 Claude synthesis.

Follows prompt preferences:
  - Explicit geometric specifications, not suggestive descriptions
  - Neutral compositional parameters
  - Translate taxonomy to image generation vocabulary
  - Let image generator optimize composition naturally

Also supports frame-sequence output for video/animation workflows.
"""

from typing import List, Dict, Optional


def build_enhancement_context(
    glia_type: str,
    glia_profile: Dict,
    visual_translation: Dict,
    base_prompt: str,
    style: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    """
    Build the structured context string that Layer 3 (Claude) receives.
    
    This is the deterministic pre-processing: all taxonomy lookups and
    coordinate translations are already resolved. Claude only needs to
    do creative synthesis on top of this resolved context.
    """
    sections = []
    
    sections.append(f"BASE PROMPT: {base_prompt}")
    sections.append(f"\nGLIA TYPE: {glia_profile['name']}")
    sections.append(f"MORPHOLOGY: {glia_profile['morphology']}")
    sections.append(f"KEY VISUAL: {glia_profile['key_visual']}")
    
    sections.append(f"\nGEOMETRIC SPECIFICATION (from 5D morphospace):")
    sections.append(visual_translation["composed_specification"])
    
    sections.append(f"\nPER-DIMENSION DETAIL:")
    sections.append(f"  Branching: {visual_translation['branching']['geometry']}")
    sections.append(f"  Branching texture: {visual_translation['branching']['texture']}")
    sections.append(f"  Energy: {visual_translation['activation']['energy_vector']}")
    sections.append(f"  Palette: {visual_translation['activation']['palette']}")
    sections.append(f"  Connectivity: {visual_translation['connectivity']['topology']}")
    sections.append(f"  Bridges: {visual_translation['connectivity']['bridges']}")
    sections.append(f"  Tiling: {visual_translation['connectivity']['tiling']}")
    sections.append(f"  Dynamics: {visual_translation['signal']['dynamics']}")
    sections.append(f"  Signal color: {visual_translation['signal']['color_shift']}")
    sections.append(f"  Structure: {visual_translation['structure']['architecture']}")
    sections.append(f"  Weight: {visual_translation['structure']['weight']}")
    
    if style:
        sections.append(f"\nVISUAL STYLE: {style}")
    if context:
        sections.append(f"CONTEXT: {context}")
    
    sections.append(f"\nVISUAL KEYWORDS: {', '.join(glia_profile.get('visual_keywords', []))}")
    
    return "\n".join(sections)


def build_frame_sequence_context(
    trajectory_states: List[List[float]],
    trajectory_per_step: List[Dict],
    glia_type_start: str,
    glia_type_end: str,
    profile_start: Dict,
    profile_end: Dict,
    visual_translations_sequence: List[Dict],
    base_prompt: str,
    num_frames: int,
    fps: float = 12.0,
    style: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    """
    Build structured context for frame-sequence (video/animation) output.
    
    Each frame gets its own geometric specification derived from the
    trajectory position at that timestep. Claude synthesizes per-frame
    prompts that maintain visual coherence across the sequence.
    """
    sections = []
    
    sections.append(f"FRAME SEQUENCE REQUEST")
    sections.append(f"Base prompt: {base_prompt}")
    sections.append(f"Frames: {num_frames}, Target FPS: {fps}")
    sections.append(f"Duration: {num_frames / fps:.1f}s")
    sections.append(f"\nTRANSITION: {profile_start['name']} → {profile_end['name']}")
    sections.append(f"Start morphology: {profile_start['morphology']}")
    sections.append(f"End morphology: {profile_end['morphology']}")
    
    if style:
        sections.append(f"\nVISUAL STYLE: {style}")
    if context:
        sections.append(f"CONTEXT: {context}")
    
    # Sample frames evenly from trajectory
    total_steps = len(visual_translations_sequence)
    if total_steps <= num_frames:
        frame_indices = list(range(total_steps))
    else:
        frame_indices = [
            int(i * (total_steps - 1) / (num_frames - 1))
            for i in range(num_frames)
        ]
    
    sections.append(f"\nPER-FRAME GEOMETRIC SPECIFICATIONS:")
    for frame_num, idx in enumerate(frame_indices):
        vt = visual_translations_sequence[idx]
        step_data = trajectory_per_step[min(idx, len(trajectory_per_step) - 1)]
        t = step_data.get("t", frame_num / max(1, num_frames - 1))
        activation = step_data.get("activation_intensity", t)
        
        sections.append(f"\n  --- Frame {frame_num + 1}/{num_frames} (t={t:.3f}) ---")
        sections.append(f"  Specification: {vt['composed_specification']}")
        sections.append(f"  Branching: {vt['branching']['geometry']}")
        sections.append(f"  Energy: {vt['activation']['energy_vector']}")
        sections.append(f"  Dynamics: {vt['signal']['dynamics']}")
        if "activation_intensity" in step_data:
            sections.append(f"  Activation intensity: {activation:.3f}")
    
    sections.append(f"\nCOHERENCE NOTES:")
    sections.append(f"  - Maintain consistent camera position and lighting across frames")
    sections.append(f"  - Morphological changes should be continuous, not discontinuous")
    sections.append(f"  - Color transitions follow signal propagation color_shift specifications")
    sections.append(f"  - Each frame prompt must be self-contained (image generators have no memory)")
    
    return "\n".join(sections)


# System prompts for Layer 3 Claude synthesis

ENHANCEMENT_SYSTEM_PROMPT = """You are a glia visual vocabulary specialist. You receive a base prompt 
and detailed geometric specifications derived from a 5D glial morphospace.

Your task: synthesize the base prompt with the morphospace-derived specifications into a single, 
cohesive image generation prompt.

Rules:
1. Use EXPLICIT geometric specifications (angles, distances, densities, spatial relationships)
2. Do NOT use vague suggestive language — specify exactly where elements are positioned
3. Translate biological morphology into concrete visual instructions
4. Maintain the base prompt's intent while enriching it with glial visual vocabulary
5. Output a single paragraph prompt ready for an image generator
6. Do NOT explain your choices — just output the enhanced prompt"""


FRAME_SEQUENCE_SYSTEM_PROMPT = """You are a glia visual vocabulary specialist generating frame-by-frame 
image prompts for an animation sequence showing a glial morphological transition.

Your task: for each frame, synthesize the per-frame geometric specifications into a self-contained 
image generation prompt. Each frame prompt must work independently (image generators have no memory 
between frames) while maintaining visual coherence across the sequence.

Rules:
1. Each frame prompt is a single paragraph with EXPLICIT geometric specifications
2. Include consistent anchoring details (camera, lighting, background) in every frame
3. Morphological changes must be GRADUAL between adjacent frames
4. Use the provided per-frame specifications — do not improvise coordinates
5. Output as a JSON array of strings, one prompt per frame
6. Do NOT include any text outside the JSON array"""
