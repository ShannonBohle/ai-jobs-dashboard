"""Normalize WARN CSVs (from Big Local News's warn-scraper) into the events schema.
Headers vary by state, so columns are detected fuzzily and the mapping is printed per file.

Scrape + parse:  python src/ingest_warn.py ny tx il wa
Parse only (reuse existing data/raw/warn/*.csv):  python src/ingest_warn.py
"""
import sys, csv, subprocess, pathlib, glob, re
from datetime import datetime

def norm(h): return re.sub(r"[^a-z0-9]", "", (h or "").lower())

def pick(headers, tokens, avoid=()):
    for t in tokens:
        for h in headers:
            n = norm(h)
            if t in n and not any(a in n for a in avoid):
                return h
    return None

def parse_date(s):
    s = (s or "").strip()
    for f in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%d-%b-%y", "%B %d, %Y", "%b %d, %Y"):
        try: return datetime.strptime(s, f).strftime("%Y-%m-%d")
        except ValueError: pass
    return s

def main(states):
    outdir = pathlib.Path("data/raw/warn"); outdir.mkdir(parents=True, exist_ok=True)
    for s in states:
        subprocess.run(["warn-scraper", s, "--data-dir", str(outdir)], check=False)
    rows, i = [], 0
    for p in sorted(glob.glob(str(outdir / "*.csv"))):
        with open(p, errors="ignore", newline="") as f:
            rd = csv.DictReader(f)
            heads = rd.fieldnames or []
            c_date = pick(heads, ["noticedate", "datereceived", "receiveddate", "warndate",
                                  "dateofnotice", "initialreport", "datelayoff", "layoffdate",
                                  "effectivedate", "date"])
            c_co   = pick(heads, ["companyname", "company", "employer", "business",
                                  "jobsitename", "site", "name"], avoid=["contact", "county", "union"])
            c_txt  = pick(heads, ["reason", "notes", "comment", "remarks"])
            c_jobs = pick(heads, ["numberaffected", "affected", "employees", "layoffnumber",
                                  "workers", "jobs", "number"], avoid=["phone", "case"])
            c_loc  = pick(heads, ["city", "location", "county", "region", "address"])
            print(f"{pathlib.Path(p).name}: date={c_date!r} company={c_co!r} "
                  f"reason={c_txt!r} jobs={c_jobs!r} loc={c_loc!r}")
            for r in rd:
                i += 1
                rows.append({
                    "id": f"warn-{i}", "date": parse_date(r.get(c_date, "")) if c_date else "",
                    "source": pathlib.Path(p).stem, "company": (r.get(c_co, "") or "").strip() if c_co else "",
                    "location": (r.get(c_loc, "") or "").strip() if c_loc else "",
                    "jobs": (r.get(c_jobs, "") or "").strip() if c_jobs else "",
                    "excerpt": ((r.get(c_txt, "") or "")[:500]).strip() if c_txt else "",
                    "human_label": ""})
    rows.sort(key=lambda r: r["date"], reverse=True)
    with open("gold/events.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","date","source","company","location","jobs","excerpt","human_label"])
        w.writeheader(); w.writerows(rows)
    dated = sum(1 for r in rows if re.match(r"\d{4}-\d{2}-\d{2}", r["date"]))
    texted = sum(1 for r in rows if r["excerpt"])
    print(f"wrote gold/events.csv ({len(rows)} events; {dated} with parsed dates; {texted} with reason text)")

if __name__ == "__main__":
    main(sys.argv[1:])
