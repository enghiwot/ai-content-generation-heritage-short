import json
import os
import time
from datetime import datetime, timezone
from google import genai
from google.genai.errors import APIError

# with retry logic to handle UNAVAILABLE: This model is currently experiencing high demand and
# auto-discovery for stable gemini models option using via auto-fallback
# after several trial in 10 seconds gemini-3.5-flash is verified
def get_candidate_models(client):
    """Discover active models, prioritizing gemini-3.8-flash and skipping deprecated 1.5/2.5 aliases."""
    candidates = ["gemini-3.8-flash"]
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            if "gemini-3" in name and name not in candidates:
                candidates.append(name)
    except Exception as e:
        print(f"Model discovery warning: {e}")
    return candidates

def run_smoke_test():
    client = genai.Client()
    candidates = get_candidate_models(client)
    prompt = "Hello! Confirming my pipeline smoke test is operational. Reply in one short sentence."
    
    print(f"Candidate models in priority order: {candidates}")
    
    success = False
    response_text = ""
    latency_ms = 0
    used_model = candidates[0]

    for model_name in candidates:
        used_model = model_name
        print(f"\nTesting model: {model_name}...")
        max_retries = 3
        delay = 5  # Longer initial backoff for 503 demand spikes

        for attempt in range(1, max_retries + 1):
            start_time = time.time()
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                latency_ms = (time.time() - start_time) * 1000
                success = True
                response_text = response.text.strip()
                print(f"Success on attempt {attempt}! Response: '{response_text}' (Latency: {latency_ms:.2f} ms)")
                break

            except APIError as e:
                latency_ms = (time.time() - start_time) * 1000
                response_text = str(e)
                print(f"Attempt {attempt} failed (Code {e.code}): {e.message}")

                # If 404 (not found/deprecated), don't retry this model—move to next candidate
                if e.code == 404:
                    print(f"Model {model_name} unavailable (404). Switching to next candidate...")
                    break

                if attempt < max_retries:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                response_text = str(e)
                print(f"Attempt {attempt} unexpected error: {e}")
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2

        if success:
            break

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "smoke_test",
        "model": used_model,
        "parameters": {
            "temperature": 1.0,
            "prompt": prompt
        },
        "success": success,
        "latency_ms": round(latency_ms, 2),
        "cost_estimate_usd": 0.0,
        "output_summary": response_text[:100] if success else "FAILED"
    }

    with open("runs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print("\nLog entry appended successfully to D:\\10academy\\runs.jsonl")

if __name__ == "__main__":
    run_smoke_test()