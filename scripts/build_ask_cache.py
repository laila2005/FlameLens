"""Pre-generate verified "Ask the NASA reports" answers for the suggested questions (data/curated/ask_cache.json).

Needs an API key for an OpenAI-compatible endpoint (default: Groq, model openai/gpt-oss-120b):
    set ASK_LLM_API_KEY=...            (or GROQ_API_KEY; optional ASK_LLM_BASE_URL, ASK_LLM_MODEL)
    python scripts/build_ask_cache.py  [PSI-25 PSI-107 ...]
The cache stores the model's raw answer; the server re-verifies it against the report pages on every request, so a
claim that stops matching is removed automatically. Never commit the key.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app import ask  # noqa: E402


def main():
    cfg = ask.config()
    if not cfg["live"]:
        raise SystemExit("Set ASK_LLM_API_KEY (or GROQ_API_KEY) first.")
    wanted = sys.argv[1:] or [i["psi_id"] for i in ask.stats()["investigations"]]
    for psi in wanted:
        for q in ask.suggestions(psi):
            r = ask.answer(psi, q)
            print(f"{psi:8} {r['source']:8} kept {len(r['claims'])} removed {r['removed_count']}  {q}"
                  + (f"  [{r['error']}]" if r.get("error") else ""))


if __name__ == "__main__":
    main()
