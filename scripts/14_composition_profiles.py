#!/usr/bin/env python3
"""Create descriptive mcrA composition tables and depth-profile figures.

This script performs visualization only. It does not run hypothesis tests or
assign ecological meaning to patterns.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

SEASON_ORDER = ["Sep24", "Jan25", "Apr25", "Jul25"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepared-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--top-n", type=int, default=8)
    args = ap.parse_args()

    prep = Path(args.prepared_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    long = pd.read_csv(prep / "lineage_relative_abundance_long.tsv", sep="\t")
    lineage_counts = pd.read_csv(prep / "lineage_counts.tsv", sep="\t", index_col=0)

    totals = lineage_counts.sum(axis=1).sort_values(ascending=False)
    top = totals.head(args.top_n).index.tolist()
    anme2d = "ANME-2d / Methanoperedenaceae-related"
    if anme2d not in top:
        top.append(anme2d)

    plot_long = long.copy()
    plot_long["plot_lineage"] = plot_long["lineage"].where(plot_long["lineage"].isin(top), "Other mcrA")

    # Sum collapsed categories within a sample before calculating group means.
    sample_comp = (
        plot_long.groupby(["sample_id", "site", "season", "plot_lineage"], observed=True)["relative_abundance_pct"]
        .sum().reset_index()
    )
    mean_comp = (
        sample_comp.groupby(["site", "season", "plot_lineage"], observed=True)["relative_abundance_pct"]
        .mean().reset_index()
    )
    wide = mean_comp.pivot_table(
        index=["site", "season"], columns="plot_lineage",
        values="relative_abundance_pct", fill_value=0
    )

    site_order = sorted(wide.index.get_level_values("site").unique(), key=lambda x: (not x.startswith("EA"), x))
    ordered_idx = []
    for site in site_order:
        for season in SEASON_ORDER:
            if (site, season) in wide.index:
                ordered_idx.append((site, season))
    wide = wide.loc[ordered_idx]

    col_order = [x for x in top if x in wide.columns] + (["Other mcrA"] if "Other mcrA" in wide.columns else [])
    wide = wide[col_order]
    wide.to_csv(out / "site_season_mean_composition.tsv", sep="\t")

    ax = wide.plot(kind="bar", stacked=True, figsize=(15, 7), width=0.85)
    ax.set_ylabel("Mean relative abundance (%)")
    ax.set_xlabel("Site × season")
    ax.set_ylim(0, 100)
    ax.set_title("mcrA lineage composition by site and season")
    ax.legend(title="Lineage", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    labels = [f"{site}\n{season.replace('24','').replace('25','')}" for site, season in wide.index]
    ax.set_xticklabels(labels, rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(out / "composition_site_season.png", dpi=220)
    plt.close()

    prof = long[(long["site"] == "EA1") & (long["lineage"] == anme2d) & long["depth_cm"].notna()].copy()
    prof["season"] = pd.Categorical(prof["season"], categories=SEASON_ORDER, ordered=True)
    prof = prof.sort_values(["season", "depth_cm"])
    prof[["sample_id", "season", "depth_cm", "relative_abundance_pct", "methane", "sulfate_mM", "h2s_uM"]].to_csv(
        out / "EA1_ANME2d_profile.tsv", sep="\t", index=False
    )

    fig, ax = plt.subplots(figsize=(7, 7))
    for season, grp in prof.groupby("season", observed=True):
        ax.plot(grp["relative_abundance_pct"], grp["depth_cm"], marker="o", label=str(season))
    ax.invert_yaxis()
    ax.set_xlabel("ANME-2d relative abundance (%)")
    ax.set_ylabel("Sediment depth (cm)")
    ax.set_title("EA1: ANME-2d relative abundance by depth")
    ax.legend(title="Season", frameon=False)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(out / "EA1_ANME2d_vertical_profile.png", dpi=220)
    plt.close()

    aom = long[long["lineage"] == anme2d].copy()
    aom_summary = aom.groupby(["site", "season"], observed=True)["relative_abundance_pct"].agg(
        ["count", "mean", "median", "max"]
    ).reset_index()
    aom_summary.to_csv(out / "ANME2d_site_season_summary.tsv", sep="\t", index=False)

    print("Wrote descriptive composition/profile tables and figures to", out)


if __name__ == "__main__":
    main()
