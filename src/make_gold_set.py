"""Build gold/gold_set.csv automatically from gold/events.csv.
Picks: every AI-mention row, ~20 varied ordinary-reason rows, ~8 euphemism rows,
plus blank press-row stubs for curated employer statements.
Run: python src/make_gold_set.py     Then: open gold/gold_set.csv, fill human_label
(yes/no/unclear) for every kept row, replace or delete the press stubs, save.
"""
import csv, re, random

AI = re.compile(r"\b(ai\b|a\.i\.|artificial intel|automat|machine learning|chatbot|llm)", re.I)
UNCLEAR = re.compile(r"restructur|efficien|reorganiz|cost reduction|consolidat|transformation", re.I)

def main():
    rows = [r for r in csv.DictReader(open("gold/events.csv", encoding="utf-8", errors="ignore"))
            if r["excerpt"].strip()]
    random.seed(45)

    ai_rows = [r for r in rows if AI.search(r["excerpt"])]
    unclear_pool = [r for r in rows if UNCLEAR.search(r["excerpt"]) and not AI.search(r["excerpt"])]
    plain_pool   = [r for r in rows if not AI.search(r["excerpt"]) and not UNCLEAR.search(r["excerpt"])]

    def diverse(pool, n):
        seen, out = set(), []
        for r in random.sample(pool, min(len(pool), n * 6)):
            key = re.sub(r"\W", "", r["excerpt"].lower())[:28]
            if key not in seen:
                seen.add(key); out.append(r)
            if len(out) == n: break
        return out

    picks = ai_rows + diverse(plain_pool, 20) + diverse(unclear_pool, 8)
    stubs = [{"id": f"press-{i:02}", "date": "", "source": "press-SOURCE?", "company": "COMPANY?",
              "location": "", "jobs": "",
              "excerpt": "PASTE EMPLOYER'S STATED REASON HERE (quote or tight paraphrase)",
              "human_label": ""} for i in range(1, 9)]

    fields = ["id","date","source","company","location","jobs","excerpt","human_label"]
    with open("gold/gold_set.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in picks: w.writerow({k: r.get(k, "") for k in fields})
        w.writerows(stubs)

    print(f"wrote gold/gold_set.csv: {len(ai_rows)} AI-mention + 20 ordinary + 8 euphemism rows + 8 press stubs")
    print("Your part: open it in Excel, type human_label (yes/no/unclear) per row;")
    print("fill in or DELETE the press stubs (don't leave placeholders); Ctrl+S, keep CSV format.")
    print("Rubric: yes = text explicitly credits AI/automation; no = other or no stated cause;")
    print("unclear = ambiguous (restructuring/efficiency with no cause named). Label the CLAIM, not your guess.")

if __name__ == "__main__":
    main()
