"""Cohen's kappa + confusion matrix: model vs human labels on the gold set.
Run: python src/eval_kappa.py gold/gold_set.csv   (expects columns human_label,model_label)
Self-test: python src/eval_kappa.py --demo
"""
import sys, csv
from collections import Counter

LABELS = ["yes", "no", "unclear"]

def kappa(pairs):
    n = len(pairs)
    obs = sum(1 for h, m in pairs if h == m) / n
    hc, mc = Counter(h for h, _ in pairs), Counter(m for _, m in pairs)
    exp = sum((hc[l] / n) * (mc[l] / n) for l in LABELS)
    return (obs - exp) / (1 - exp) if exp < 1 else 1.0, obs

def confusion(pairs):
    c = Counter(pairs)
    head = "human\\model".ljust(14) + "".join(l.ljust(9) for l in LABELS)
    rows = [head] + [h.ljust(14) + "".join(str(c[(h, m)]).ljust(9) for m in LABELS) for h in LABELS]
    return "\n".join(rows)

def main():
    if "--demo" in sys.argv:
        pairs = [("yes","yes")]*8+[("no","no")]*9+[("unclear","unclear")]*3+[("yes","unclear"),("no","yes"),("unclear","no")]
    else:
        with open(sys.argv[1], encoding="utf-8", errors="ignore") as f:
            rows = [r for r in csv.DictReader(f) if r.get("human_label") and r.get("model_label")]
        pairs = [(r["human_label"].strip().lower(), r["model_label"].strip().lower()) for r in rows]
    k, agree = kappa(pairs)
    print(f"n={len(pairs)}  raw agreement={agree:.3f}  Cohen's kappa={k:.3f}")
    print(confusion(pairs))

if __name__ == "__main__":
    main()
