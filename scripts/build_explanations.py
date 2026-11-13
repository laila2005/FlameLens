"""Write data/curated/explanations.json: AI explanations for the habitat presets, made ahead of the demo.

Vercel cannot run a local model, so the live site serves this cache (re-verified on every request).
Needs an OpenAI-compatible endpoint, for example Ollama:
    ollama pull qwen2.5:7b-instruct
    set LLM_BASE_URL=http://localhost:11434/v1        (PowerShell: $env:LLM_BASE_URL="http://localhost:11434/v1")
    set LLM_MODEL=qwen2.5:7b-instruct
    python scripts/build_explanations.py               (all presets)
    python scripts/build_explanations.py moon-base     (one preset)
It prints how many claims the verifier keeps for each preset. Commit the JSON only if the kept claims read well.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import explain as ex  # noqa: E402
from backend.app.main import HABITATS  # noqa: E402
from backend.app.schemas import Target  # noqa: E402


def main(only):
    cfg = ex.llm_config()
    if not cfg["base_url"]:
        sys.exit("Set LLM_BASE_URL first (see the top of this file).")
    entries = ex.load_cache()
    for h in HABITATS:
        if only and h["id"] not in only:
            continue
        t = Target(**{k: h[k] for k in ("o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g", "fuel_state")})
        print(f"{h['name']}: asking {cfg['model']} ...", flush=True)
        try:
            entry = ex.cache_entry(t, h["id"], cfg)
        except Exception as e:
            print(f"  failed: {e}")
            continue
        kept, removed = ex.verify(entry["claims"], ex.retrieve(t))
        print(f"  kept {len(kept)}, removed {len(removed)}")
        for c in kept:
            print("   +", c["claim"])
        for c in removed:
            print("   -", c["reason"], "::", c["claim"][:100])
        entries[ex._key(t)] = entry
        ex.save_cache(entries)
    print(f"Saved {ex.CACHE_PATH}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
