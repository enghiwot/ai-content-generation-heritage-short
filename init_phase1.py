import json
import os
from datetime import datetime, timezone

# 1. Architecture & Pipeline Design Specification (DESIGN.md)
DESIGN_MD_CONTENT = """# Heritage Short: Architecture & Pipeline Design (`DESIGN.md`)

## 1. Narrative Core & Creative Vision
- **Theme / Quote:** *"This too shall pass."* — Elder brother's guiding wisdom.
- **Arc (50 Seconds, 5 Scenes):**
  1. **The Weight (Setup):** Late-night overwhelm at a desk; rain against glass; heavy shadows symbolizing acute stress.
  2. **The Anchor (Inciting Recall):** A worn handwritten note and memory of an elder brother's calm voice cutting through the noise.
  3. **The Passage (Metaphor):** Storm clouds breaking over Ethiopian highland hills into dawn light—visualizing impermanence.
  4. **The Shift (Resolution):** Morning sunlight hitting the desk; the protagonist exhaling and taking one steady step forward.
  5. **The Echo (Closing Title):** Quiet, grounded closing frame holding the quote *"This too shall pass."*

## 2. Pipeline Architecture
- **Stage 0 (`smoke_test.py`):** API health check, dynamic model discovery (`gemini-3.5-flash`), and exponential backoff validation.
- **Stage 1 (`storyboard.json`):** Deterministic contract defining scene timing, camera motion, style tokens, voiceover lines, and subtitles.
- **Stage 2 (Asset Generation):**
  - **Script & Prompt Refinement:** `gemini-3.5-flash` with automatic retry handling.
  - **Keyframes:** Style-locked 16:9 image prompts per scene (`1920x1080`).
  - **Narration (TTS):** Calm spoken-word audio timed to fit inside each scene's duration budget.
- **Stage 3 (FFmpeg Assembly):**
  - Ken Burns motion (`zoompan`) applied to keyframes to prevent static slides.
  - Crossfade transitions (`xfade`) synced with narration and SRT subtitles.

## 3. Consistency & Fault-Tolerance Strategy
- **Visual Consistency:** Every prompt prepends an immutable `style_bible` prefix so lighting, film stock, and character appearance remain consistent across cuts.
- **API Resilience:** Status-aware error handling skips `404` deprecated aliases immediately and applies exponential backoff on `503`/`429` spikes.
- **Observability (`runs.jsonl`):** Every API call appends a structured JSON line recording latency, parameters, model, and status.
"""

# 2. Engineering Failures & Mitigations Log (FAILURES.md)
FAILURES_MD_CONTENT = """# Engineering Failures & Mitigations Log (`FAILURES.md`)

## Entry 1: Python 3.8 SDK Incompatibility & Deprecated Package
- **Symptom:** `pip install google-genai` failed with `No matching distribution found`; legacy `google-generativeai` installed `0.1.0rc1` lacking `GenerativeModel`.
- **Root Cause:** Local environment defaulted to EOL Python 3.8.0.
- **Fix:** Upgraded runtime to modern Python, rebuilt virtual environment cleanly, and migrated to the official `google-genai` SDK.

## Entry 2: Model Alias Availability (`404 NOT_FOUND` & `503 UNAVAILABLE`)
- **Symptom:** `gemini-1.5-flash` and `gemini-2.5-flash` returned `404 NOT_FOUND` for new API keys; `gemini-3.8-flash` hit transient `503 UNAVAILABLE` high-demand spikes.
- **Root Cause:** Retired 1.5/2.5 model endpoints and peak-hour capacity saturation on 3.8-flash.
- **Fix:** Built dynamic model discovery in `smoke_test.py` that filters out retired aliases, prioritizes active `gemini-3` models (`gemini-3.5-flash`), and wraps API calls in exponential backoff retries while logging every attempt to `runs.jsonl`.
"""

# 3. Deterministic Storyboard Contract (storyboard.json)
STORYBOARD_DATA = {
    "project_meta": {
        "title": "This Too Shall Pass",
        "inspiration": "Elder brother's enduring wisdom during moments of overwhelm",
        "target_duration_sec": 50,
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "fps": 24,
        "text_model": "gemini-3.5-flash"
    },
    "style_bible": {
        "visual_prefix": (
            "Cinematic 35mm film still, Kodak Portra 400 color grading, shallow depth of field, "
            "natural atmospheric lighting, photorealistic, high emotional realism, 16:9 aspect ratio "
            "--no text, watermarks, distorted hands"
        ),
        "character_anchor": (
            "An East African young adult in their late 20s wearing a dark textured knit sweater, "
            "thoughtful expression"
        ),
        "audio_tone": (
            "Warm, unhurried, intimate spoken-word narration with soft ambient rain transitioning "
            "into gentle morning acoustic resonance"
        )
    },
    "scenes": [
        {
            "scene_id": 1,
            "title": "The Weight",
            "duration_sec": 10,
            "narration": "There are nights when the weight of everything unfinished feels permanent.",
            "visual_prompt": (
                "An East African young adult in their late 20s wearing a dark textured knit sweater, "
                "sitting at a cluttered wooden desk late at night, illuminated only by a warm desk lamp, "
                "rain streaks on a dark window behind them, exhausted posture, head resting in one hand."
            ),
            "camera_motion": "slow_push_in",
            "transition_out": "fade",
            "subtitle_text": "There are nights when the weight of everything unfinished feels permanent."
        },
        {
            "scene_id": 2,
            "title": "The Anchor",
            "duration_sec": 10,
            "narration": "That is when I hear my older brother's voice—steady, unshaken, reminding me.",
            "visual_prompt": (
                "Extreme close-up on a weathered cream-colored notebook on a wooden desk, a fountain pen "
                "resting beside a handwritten note, soft warm tungsten lamp glow highlighting paper grain "
                "and dust motes in the air."
            ),
            "camera_motion": "slow_pan_right",
            "transition_out": "fade",
            "subtitle_text": "That is when I hear my older brother's voice—steady, unshaken, reminding me."
        },
        {
            "scene_id": 3,
            "title": "The Passage",
            "duration_sec": 10,
            "narration": "No storm owns the sky forever. Even the heaviest hour moves.",
            "visual_prompt": (
                "Wide cinematic landscape of misty Ethiopian highland hills at the break of dawn, heavy dark "
                "rain clouds parting as golden morning sunbeams pierce through the valley below, atmospheric mist."
            ),
            "camera_motion": "slow_pull_out",
            "transition_out": "fade",
            "subtitle_text": "No storm owns the sky forever. Even the heaviest hour moves."
        },
        {
            "scene_id": 4,
            "title": "The Shift",
            "duration_sec": 11,
            "narration": "You do not have to solve the whole road tonight. Just breathe, and take the next step.",
            "visual_prompt": (
                "Morning golden sunlight streaming through a clean window onto a tidy wooden desk, "
                "an East African young adult in their late 20s wearing a dark textured knit sweater standing "
                "calmly by the window holding a warm ceramic mug, peaceful expression."
            ),
            "camera_motion": "slow_push_in",
            "transition_out": "fade",
            "subtitle_text": "You do not have to solve the whole road tonight. Just breathe, and take the next step."
        },
        {
            "scene_id": 5,
            "title": "The Echo",
            "duration_sec": 9,
            "narration": "This too shall pass.",
            "visual_prompt": (
                "Minimalist sunlit wooden tabletop with warm morning shadows of windowpanes cast across the grain, "
                "a single small green plant leaf catching golden light, tranquil stillness."
            ),
            "camera_motion": "static_hold",
            "transition_out": "fade_to_black",
            "subtitle_text": "\"This too shall pass.\""
        }
    ]
}


def build_phase1_artifacts():
    # Create standard output directories for Phase 2 assets
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Write DESIGN.md
    with open("DESIGN.md", "w", encoding="utf-8") as f:
        f.write(DESIGN_MD_CONTENT.strip() + "\n")

    # Write FAILURES.md
    with open("FAILURES.md", "w", encoding="utf-8") as f:
        f.write(FAILURES_MD_CONTENT.strip() + "\n")

    # Write storyboard.json with clean indentation
    with open("storyboard.json", "w", encoding="utf-8") as f:
        json.dump(STORYBOARD_DATA, f, indent=2, ensure_ascii=False)

    # Validate the JSON contract immediately
    with open("storyboard.json", "r", encoding="utf-8") as f:
        loaded = json.load(f)

    total_sec = sum(scene["duration_sec"] for scene in loaded["scenes"])
    print(f"[OK] DESIGN.md created.")
    print(f"[OK] FAILURES.md created.")
    print(f"[OK] storyboard.json created & validated: {len(loaded['scenes'])} scenes, {total_sec}s total runtime.")
    print(f"[OK] Workspace directories ready: assets/images, assets/audio, output")

    # Log the contract creation to runs.jsonl
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "phase1_contract_init",
        "model": loaded["project_meta"]["text_model"],
        "parameters": {
            "scenes": len(loaded["scenes"]),
            "target_duration_sec": total_sec
        },
        "success": True,
        "latency_ms": 0.0,
        "cost_estimate_usd": 0.0,
        "output_summary": "Initialized DESIGN.md, FAILURES.md, and validated 5-scene storyboard.json"
    }
    with open("runs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    print("[OK] Logged milestone to runs.jsonl.")


if __name__ == "__main__":
    build_phase1_artifacts()