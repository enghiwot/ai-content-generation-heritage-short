# Heritage Short: Architecture & Pipeline Design (`DESIGN.md`)

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
