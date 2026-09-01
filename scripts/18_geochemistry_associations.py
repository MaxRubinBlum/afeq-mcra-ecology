#!/usr/bin/env python3
"""Exploratory lineage-geochemistry associations for metadata-matched EA samples.

This script uses Spearman rank correlations because lineage relative abundances
are bounded, zero-rich, and commonly non-normal. It reports both pooled and
site-stratified tables. These are exploratory associations, not causal models.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

CHEMISTRY = [
    "depth_cm",
    "methane",
    "sulfate_mM",
    "h2s_uM",
    "fe_uM",
    "dic_mM",
    "phosphate_uM",
]


def bh_fdr(pvalues: pd.Series) -> pd.Series:
    """Benjamini-Hochberg adjusted p-values, preserving missing values."""
    out = pd.Series(np.nan, index=pvalues.index, dtype=float)
    valid = pvalues.dropna().astype(float)
    if len(valid) == 0:
        return out
    order = valid.sort_values().index
    ranked = valid.loc[order].to_numpy()
    m = len(ranked)
    q = ranked * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    q = np.clip(q, 0, 1)
    out.loc[order] = q
    return out


def correlation_rows(data: pd.DataFrame, lineages: list[str], scope: str, min_n: int) -> list[dict]:
    rows = []
    for lineage in lineages:
        if lineage not in data.columns:
            continue
        for variable in CHEMISTRY:
            if variable not in data.columns:
                continue
            pair = data[[lineage, variable]].copy()
            pair[lineage] = pd.to_numeric(pair[lineage], errors="coerce")
            pair[variable] = pd.to_numeric(pair[variable], errors="coerce")
            pair = pair.dropna()
            if len(pair) < min_n or pair[lineage].nunique() < 2 or pair[variable].nunique() < 2:
                continue
            rho, p = spearmanr(pair[lineage], pair[variable])
            rows.append({
                "scope": scope,
                "lineage": lineage,
                "variable": variable,
                "n": len(pair),
                "spearman_rho": rho,
                "p_value": p,
                "nonzero_lineage_samples": int((pair[lineage] > 0).sum()),
            })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepared-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--top-lineages", type=int, default=10)
    ap.add_argument("--min-n", type=int, default=8)
    args = ap.parse_args()

    prep = Path(args.prepared_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rel = pd.read_csv(prep / "lineage_relative_abundance_pct.tsv", sep="\t", index_col=0).T
    meta = pd.read_csv(prep / "sample_metadata_ecology.tsv", sep="\t").set_index("sample_id")
    lineage_counts = pd.read_csv(prep / "lineage_counts.tsv", sep="\t", index_col=0)

    totals = lineage_counts.sum(axis=1).sort_values(ascending=False)
    lineages = totals.head(args.top_lineages).index.tolist()
    for aom in [
        "ANME-2d / Methanoperedenaceae-related",
        "ANME-3 / Methanovorans-related",
        "ANME-2a-related / Methanocomedens",
    ]:
        if aom in rel.columns and aom not in lineages:
            lineages.append(aom)

    joined = meta.join(rel[lineages], how="inner")
    for variable in CHEMISTRY:
        if variable in joined.columns:
            joined[variable] = pd.to_numeric(joined[variable], errors="coerce")

    matched = joined[joined["depth_cm"].notna()].copy()
    matched.to_csv(out / "metadata_lineage_joined.tsv", sep="\t", index=True, index_label="sample_id")

    rows = correlation_rows(matched, lineages, "pooled_EA", args.min_n)
    for site, site_data in matched.groupby("site"):
        if len(site_data) >= args.min_n:
            rows.extend(correlation_rows(site_data, lineages, f"site_{site}", args.min_n))

    stats = pd.DataFrame(rows)
    if len(stats):
        stats["fdr_bh"] = np.nan
        for scope, idx in stats.groupby("scope").groups.items():
            stats.loc[idx, "fdr_bh"] = bh_fdr(stats.loc[idx, "p_value"])
        stats = stats.sort_values(["scope", "fdr_bh", "p_value"], na_position="last")
    stats.to_csv(out / "lineage_geochemistry_spearman.tsv", sep="\t", index=False)

    anme = "ANME-2d / Methanoperedenaceae-related"
    if anme in matched.columns:
        focus_cols = ["site", "season", "depth_cm", "methane", "sulfate_mM", "h2s_uM", anme]
        matched[focus_cols].to_csv(
            out / "ANME2d_geochemistry_samples.tsv", sep="\t", index=True, index_label="sample_id"
        )

    print(f"Metadata-matched retained samples: {len(matched)}")
    print(f"Lineages tested: {len(lineages)}")
    print(f"Association tests written: {len(stats)}")
    print("Wrote joined metadata and correlation tables to", out)


if __name__ == "__main__":
    main()
