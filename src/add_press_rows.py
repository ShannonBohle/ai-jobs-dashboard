"""Add press-sourced events to gold/gold_set.csv interactively - no Excel.
For each: company, source tag (e.g. press-sec, press-reuters), date, jobs, and the
employer's STATED reason (quote or tight paraphrase). Leaves human_label blank;
run label_gold_set.py afterward to label only the new rows.
Run: python src/add_press_rows.py
"""
import csv, re

PATH = "gold/gold_set.csv"

def main():
    rows = list(csv.DictReader(open(PATH, encoding="utf-8", errors="ignore")))
    fields = list(rows[0].keys())
    used = [int(m.group(1)) for r in rows if (m := re.match(r"press-(\d+)", r["id"]))]
    n = max(used, default=0)
    print("Add press rows; blank company = done.\n")
    added = 0
    while True:
        co = input("Company: ").strip()
        if not co: break
        src = input("  source tag (press-sec / press-reuters / ...): ").strip() or "press"
        date = input("  date YYYY-MM-DD (optional): ").strip()
        jobs = input("  jobs affected (optional): ").strip()
        excerpt = input("  employer's stated reason: ").strip()
        if not excerpt:
            print("  (skipped - reason required)"); continue
        n += 1; added += 1
        rows.append({k: "" for k in fields} | {"id": f"press-{n:02}", "date": date,
                    "source": src, "company": co, "jobs": jobs, "excerpt": excerpt[:500]})
        with open(PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
        print(f"  saved as press-{n:02}\n")
    print(f"{added} added. Next: python src/label_gold_set.py")

if __name__ == "__main__":
    main()
