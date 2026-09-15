"""Interactive terminal labeler for gold/gold_set.csv - no Excel needed.
Shows each unlabeled row's company + stated reason; you press y / n / u.
Auto-drops press stubs still holding placeholder text. Saves after every answer.
Run: python src/label_gold_set.py      (r = relabel everything from scratch)
Keys: y = AI/automation explicitly credited | n = other or no cause | u = ambiguous
      s = skip for now | q = quit (progress saved)
"""
import csv, sys

PATH = "gold/gold_set.csv"

def save(rows, fields):
    with open(PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

def main():
    rows = list(csv.DictReader(open(PATH, encoding="utf-8", errors="ignore")))
    fields = list(rows[0].keys())
    kept = [r for r in rows if not r["excerpt"].startswith("PASTE EMPLOYER")]
    dropped = len(rows) - len(kept)
    if dropped:
        print(f"(dropped {dropped} unfilled press stubs)")
    rows = kept
    if "r" in sys.argv[1:]:
        for r in rows: r["human_label"] = ""
    todo = [r for r in rows if not r["human_label"].strip()]
    print(f"{len(todo)} rows to label. yes = text explicitly credits AI/automation;")
    print("no = other or no stated cause; unclear = vague (restructuring etc.), no cause named.")
    print("Label the CLAIM in the text, not your own guess about the company.\n")
    keys = {"y": "yes", "n": "no", "u": "unclear"}
    for i, r in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {r['company'][:55]}  ({r.get('jobs','')} jobs, {r.get('date','')})")
        print(f"    reason: {r['excerpt'][:220]}")
        while True:
            a = input("    y / n / u  (s=skip, q=quit): ").strip().lower()
            if a in keys:
                r["human_label"] = keys[a]; save(rows, fields); break
            if a == "s": break
            if a == "q":
                save(rows, fields)
                done = sum(1 for x in rows if x["human_label"].strip())
                print(f"saved; {done}/{len(rows)} labeled"); return
            print("    press y, n, u, s, or q")
    save(rows, fields)
    done = sum(1 for x in rows if x["human_label"].strip())
    print(f"\nAll saved: {done}/{len(rows)} rows labeled in {PATH}")
    print("Next: python src/classify_ai_attribution.py gold/gold_set.csv --ollama mistral:7b-instruct")
    print("Then: python src/eval_kappa.py gold/gold_set_labeled.csv")

if __name__ == "__main__":
    main()
