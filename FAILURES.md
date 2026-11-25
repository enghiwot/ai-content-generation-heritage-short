# Engineering Failures & Mitigations Log (`FAILURES.md`)

## Entry 1: Python 3.8 SDK Incompatibility & Deprecated Package
- **Symptom:** `pip install google-genai` failed with `No matching distribution found`; legacy `google-generativeai` installed `0.1.0rc1` lacking `GenerativeModel`.
- **Root Cause:** Local environment defaulted to EOL Python 3.8.0.
- **Fix:** Upgraded runtime to modern Python, rebuilt virtual environment cleanly, and migrated to the official `google-genai` SDK.

## Entry 2: Model Alias Availability (`404 NOT_FOUND` & `503 UNAVAILABLE`)
- **Symptom:** `gemini-1.5-flash` and `gemini-2.5-flash` returned `404 NOT_FOUND` for new API keys; `gemini-3.8-flash` hit transient `503 UNAVAILABLE` high-demand spikes.
- **Root Cause:** Retired 1.5/2.5 model endpoints and peak-hour capacity saturation on 3.8-flash.
- **Fix:** Built dynamic model discovery in `smoke_test.py` that filters out retired aliases, prioritizes active `gemini-3` models (`gemini-3.5-flash`), and wraps API calls in exponential backoff retries while logging every attempt to `runs.jsonl`.
