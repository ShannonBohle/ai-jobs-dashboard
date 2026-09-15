"""Join AI-exposure scores to BLS OEWS employment; emit dashboard JSON.
Sources (see DATA_SOURCES.md): Felten AIOE; Eloundou et al. occ-level beta; BLS OEWS national.
Run: python src/build_dataset.py [--oews data/raw/national_May2021_dl.csv]
"""
import json, argparse, re
import pandas as pd

def norm_soc(s):
    s = str(s).strip()
    m = re.match(r"(\d{2}-\d{4})", s)
    return m.group(1) if m else None

def main(oews_path):
    aioe = pd.read_excel("data/raw/AIOE_DataAppendix.xlsx", sheet_name="Appendix A")
    aioe.columns = ["soc", "title_aioe", "aioe"]
    aioe["soc"] = aioe["soc"].map(norm_soc)

    gpt = pd.read_csv("data/raw/occ_level.csv")
    gpt["soc"] = gpt["O*NET-SOC Code"].map(norm_soc)
    # beta = share of tasks where an LLM (or LLM+software at 0.5 weight) halves completion time
    gpt = (gpt.groupby("soc", as_index=False)
              .agg(gpt_beta_model=("dv_rating_beta", "mean"),
                   gpt_beta_human=("human_rating_beta", "mean"),
                   title_gpt=("Title", "first")))

    oews = pd.read_csv(oews_path, dtype=str)
    oews = oews[oews["O_GROUP"].str.lower().eq("detailed")].copy()
    oews["soc"] = oews["OCC_CODE"].map(norm_soc)
    for c in ("TOT_EMP", "A_MEDIAN"):
        oews[c] = pd.to_numeric(oews[c].str.replace(",", "").replace({"*": None, "#": None}), errors="coerce")
    oews = oews[["soc", "OCC_TITLE", "TOT_EMP", "A_MEDIAN"]].rename(
        columns={"OCC_TITLE": "title", "TOT_EMP": "employment", "A_MEDIAN": "median_wage"})

    df = oews.merge(aioe[["soc", "aioe"]], on="soc", how="left") \
             .merge(gpt[["soc", "gpt_beta_model", "gpt_beta_human"]], on="soc", how="left")
    df["soc_major"] = df["soc"].str[:2]

    matched = df.dropna(subset=["aioe", "gpt_beta_model"])
    cov = {
        "occupations_total": int(len(df)),
        "occupations_with_both_scores": int(len(matched)),
        "employment_total": int(df["employment"].sum()),
        "employment_covered": int(matched["employment"].sum()),
    }
    w = matched["employment"]
    summary = {
        "emp_weighted_aioe": round(float((matched["aioe"] * w).sum() / w.sum()), 4),
        "emp_weighted_gpt_beta_model": round(float((matched["gpt_beta_model"] * w).sum() / w.sum()), 4),
        "emp_weighted_gpt_beta_human": round(float((matched["gpt_beta_human"] * w).sum() / w.sum()), 4),
        "aioe_gpt_spearman": round(float(matched["aioe"].corr(matched["gpt_beta_model"], method="spearman")), 4),
    }
    top = matched.nlargest(15, "gpt_beta_model")[["soc", "title", "employment", "gpt_beta_model", "aioe"]]
    out = {
        "coverage": cov, "summary": summary,
        "top_exposed": top.to_dict(orient="records"),
        "occupations": df.round(4).where(pd.notna(df), None).to_dict(orient="records"),
    }
    df.round(4).to_csv("data/processed/occupations_joined.csv", index=False)
    with open("data/processed/dashboard_data.json", "w") as f:
        json.dump(out, f, indent=1)
    print("coverage:", cov); print("summary:", summary)
    print("wrote data/processed/dashboard_data.json and occupations_joined.csv")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--oews", default="data/raw/national_May2021_dl.csv")
    main(ap.parse_args().oews)
