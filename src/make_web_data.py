"""Export dashboard-ready JSON into the Next.js app's public/data folder.
Run from the kit root AFTER build_dataset + classify + kappa:
  python src/make_web_data.py --judge "mistral:7b-instruct (rubric v3)"
Writes: dashboard_data.json, events.json, gold.json, methods.txt
"""
import csv, json, sys, shutil, pathlib, re, math, datetime
from collections import Counter

def denan(o):
    if isinstance(o, float) and math.isnan(o): return None
    if isinstance(o, dict): return {k: denan(v) for k, v in o.items()}
    if isinstance(o, list): return [denan(v) for v in o]
    return o

OUT = pathlib.Path("dashboard-app/public/data")
LABELS = ["yes", "no", "unclear"]
AI = re.compile(r"\b(ai\b|a\.i\.|artificial intel|automat|machine learning|chatbot)", re.I)

def kappa(pairs):
    n = len(pairs)
    if not n: return None, None
    obs = sum(1 for h, m in pairs if h == m) / n
    hc, mc = Counter(h for h, _ in pairs), Counter(m for _, m in pairs)
    exp = sum((hc[l] / n) * (mc[l] / n) for l in LABELS)
    return (obs - exp) / (1 - exp) if exp < 1 else 1.0, obs

def main():
    judge = "local LLM"
    if "--judge" in sys.argv:
        judge = sys.argv[sys.argv.index("--judge") + 1]
    OUT.mkdir(parents=True, exist_ok=True)

    dash = denan(json.load(open("data/processed/dashboard_data.json")))
    json.dump(dash, open(OUT / "dashboard_data.json", "w"), allow_nan=False)
    shutil.copy("METHODS.md", OUT / "methods.txt")

    ev = list(csv.DictReader(open("gold/events.csv", encoding="utf-8", errors="ignore")))
    events = [{"date": r["date"], "company": r["company"], "location": r.get("location", ""),
               "jobs": r.get("jobs", ""), "excerpt": r["excerpt"], "source": r["source"],
               "ai_mention": bool(AI.search(r["excerpt"]))} for r in ev]
    json.dump(events, open(OUT / "events.json", "w", encoding="utf-8"))

    g = list(csv.DictReader(open("gold/gold_set_labeled.csv", encoding="utf-8", errors="ignore")))
    pairs = [(r["human_label"].strip().lower(), r["model_label"].strip().lower())
             for r in g if r.get("human_label", "").strip() and r.get("model_label", "").strip()]
    k, agree = kappa(pairs)
    conf = Counter(pairs)
    # monthly timeline from WARN events + optional hand-cited Challenger series
    monthly = {}
    for r in ev:
        m = r["date"][:7]
        if re.match(r"^\d{4}-\d{2}$", m):
            d = monthly.setdefault(m, {"month": m, "events": 0, "jobs": 0, "ai_mentions": 0})
            d["events"] += 1
            jr = re.sub(r"[^0-9]", "", r.get("jobs", "") or "")
            if jr: d["jobs"] += int(jr)
            if AI.search(r["excerpt"]): d["ai_mentions"] += 1
    challenger, ticker = [], None
    ch_p = pathlib.Path("data/raw/challenger_ai_monthly.csv")
    if ch_p.exists():
        for r in csv.DictReader(open(ch_p, encoding="utf-8")):
            row = {"month": r["month"],
                   "ai_cuts": int(r["ai_cuts"]) if r.get("ai_cuts") else None,
                   "total_cuts": int(r["total_cuts"]) if r.get("total_cuts") else None,
                   "note": r.get("note", "")}
            if r["month"].startswith("YTD"):
                ticker = {"value": row["ai_cuts"], "asof": "January-May 2026",
                          "source": "Challenger, Gray & Christmas"}
            else:
                challenger.append(row)
    macro = None
    mc_p = pathlib.Path("data/raw/macro_context.csv")
    if mc_p.exists():
        rows_mc = list(csv.DictReader(open(mc_p, encoding="utf-8")))
        if rows_mc:
            r = sorted(rows_mc, key=lambda x: x["month"])[-1]
            macro = {"month": r["month"], "total_change": int(r["total_change"]),
                     "unemp_rate": float(r["unemp_rate"]) if r.get("unemp_rate") else None,
                     "info_change": int(r["info_change"]) if r.get("info_change") else None,
                     "note": r.get("note", "")}
    g_rows = list(csv.DictReader(open("gold/gold_set_labeled.csv", encoding="utf-8", errors="ignore")))
    confirmed = [{"month": r["date"][:7], "company": r["company"], "jobs": int(re.sub(r"[^0-9]", "", r.get("jobs","") or "0") or 0)}
                 for r in g_rows if r.get("human_label","").strip().lower() == "yes" and re.match(r"^\d{4}-\d{2}", r.get("date",""))]
    seen = {(c["month"], c["company"].lower()) for c in confirmed}
    for r in events:
        if r["ai_mention"] and re.match(r"^\d{4}-\d{2}", r["date"]):
            key = (r["date"][:7], r["company"].lower())
            if key not in seen:
                seen.add(key)
                confirmed.append({"month": r["date"][:7], "company": r["company"],
                                  "jobs": int(re.sub(r"[^0-9]", "", r.get("jobs","") or "0") or 0)})
    confirmed.sort(key=lambda c: c["month"])
    timeline = {"retrieved": datetime.date.today().isoformat(), "ticker": ticker, "macro": macro, "confirmed": confirmed,
                "warn_monthly": sorted(monthly.values(), key=lambda d: d["month"]),
                "challenger": challenger}
    json.dump(denan(timeline), open(OUT / "timeline.json", "w"), allow_nan=False)

    gold = {"judge": judge, "n": len(pairs),
            "kappa": round(k, 3) if k is not None else None,
            "agreement": round(agree, 3) if agree is not None else None,
            "confusion": {f"{h}|{m}": conf[(h, m)] for h in LABELS for m in LABELS if conf[(h, m)]},
            "rows": [{"company": r["company"], "excerpt": r["excerpt"], "human": r["human_label"],
                      "model": r["model_label"], "rationale": r.get("model_rationale", "")} for r in g]}
    json.dump(gold, open(OUT / "gold.json", "w", encoding="utf-8"))
    print(f"wrote {OUT}/dashboard_data.json, events.json ({len(events)}), timeline.json ({len(timeline['warn_monthly'])} months, {len(challenger)} Challenger pts), gold.json (n={len(pairs)}, kappa={gold['kappa']}), methods.txt")

if __name__ == "__main__":
    main()
