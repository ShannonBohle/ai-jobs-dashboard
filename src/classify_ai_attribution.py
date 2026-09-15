"""Tag layoff events for AI attribution; judge = Claude API, local Ollama, or offline mock.
Reads a CSV with id,company,excerpt[,human_label]; writes *_labeled.csv with model_label/model_rationale.

  Ollama (local, no key):  python src/classify_ai_attribution.py gold/gold_set.csv --ollama llama3.1
  Claude API:              set ANTHROPIC_API_KEY=... ; python src/classify_ai_attribution.py gold/gold_set.csv
  Offline plumbing test:   python src/classify_ai_attribution.py gold/events_demo.csv --mock

Caches per judge model under data/processed/, keyed by row id.
"""
import sys, csv, json, re, pathlib, urllib.request

PROMPT = """You label layoff/WARN notices for AI attribution. Apply these rules IN ORDER; Rule 1 overrides all others.
RULE 1: If the stated reason mentions AI, artificial intelligence, automation, machine learning, or
chatbots ANYWHERE - even alongside another reason - label "yes".
RULE 2: Otherwise, if any other cause is stated, or the reason is a bare category such as "Layoff",
"Mass Layoff", "Plant Closure", "Economic", "Merger", "Bankruptcy", "Relocation",
"Contract Termination", "Funding Loss", or "Other", label "no".
RULE 3: Otherwise, if the text only uses vague efficiency / restructuring / reorganization /
transformation language that hints at automation without naming it, label "unclear".
Worked examples: "Restructuring driven by artificial intelligence adoption" -> yes.
"Plant Closure" -> no. "Operational efficiency initiative" -> unclear.
This records the CLAIMED cause as stated in the text, not the true cause.
Return only JSON: {"label":"yes|no|unclear","rationale":"<=25 words"}"""

def parse_json(out):
    out = out.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    d = json.loads(out)
    if d.get("label") not in ("yes", "no", "unclear"):
        raise ValueError(f"bad label: {d.get('label')!r}")
    return {"label": d["label"], "rationale": str(d.get("rationale", ""))[:200]}

def ollama_check(model):
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            tags = [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        sys.exit("Ollama isn't reachable at localhost:11434. Start the Ollama app (or run `ollama serve`) and retry.")
    if not any(t == model or t.split(":")[0] == model.split(":")[0] for t in tags):
        sys.exit(f"Model '{model}' not installed. Installed: {', '.join(tags) or 'none'}. Run: ollama pull {model}")

def ollama_classify(model, text):
    body = {"model": model, "stream": False, "format": "json", "options": {"temperature": 0},
            "messages": [{"role": "system", "content": PROMPT},
                         {"role": "user", "content": text[:4000]}]}
    req = urllib.request.Request("http://localhost:11434/api/chat",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["message"]["content"]

def mock_classify(text):
    t = text.lower()
    hit = any(k in t for k in ("ai ", "ai.", "ai-", "artificial intel", "machine learning",
                               "machine-learning", "automat", "chatbot", "coding assistants"))
    soft = any(k in t for k in ("efficien", "restructur", "reorganiz", "transformation", "consolidat"))
    lab = "yes" if hit else ("unclear" if soft else "no")
    return json.dumps({"label": lab, "rationale": "mock keyword heuristic (offline test only)"})

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else "gold/events.csv"
    mock = "--mock" in argv
    ollama = "--ollama" in argv
    model = "mock"
    client = None
    if ollama:
        i = argv.index("--ollama")
        model = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].endswith(".csv") else "llama3.1"
        ollama_check(model)
    elif not mock:
        import anthropic
        client = anthropic.Anthropic()
        model = "claude-sonnet-4-6"

    safe = re.sub(r"[^A-Za-z0-9._-]", "_", model)
    cache_p = pathlib.Path(f"data/processed/attribution_cache_{safe}.json")
    cache_p.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}

    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="ignore")))
    for n, r in enumerate(rows, 1):
        if r["id"] not in cache:
            text = f'{r.get("company", "")}: {r.get("excerpt", "")}'
            for attempt in (1, 2):
                try:
                    if mock: out = mock_classify(text)
                    elif ollama: out = ollama_classify(model, text)
                    else:
                        msg = client.messages.create(model=model, max_tokens=200, system=PROMPT,
                                                     messages=[{"role": "user", "content": text[:4000]}])
                        out = msg.content[0].text
                    cache[r["id"]] = parse_json(out)
                    break
                except (json.JSONDecodeError, ValueError):
                    if attempt == 2:
                        sys.exit(f"Judge returned unparseable output twice on row {r['id']} - try a larger model.")
            cache_p.write_text(json.dumps(cache, indent=1))
        r["model_label"] = cache[r["id"]]["label"]
        r["model_rationale"] = cache[r["id"]]["rationale"]
        print(f"  {n}/{len(rows)}  {r['id']}: {r['model_label']}")
    out_path = path.replace(".csv", "_labeled.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"wrote {out_path} ({len(rows)} rows; judge={model}; cache={cache_p})")

if __name__ == "__main__":
    main(sys.argv[1:])
