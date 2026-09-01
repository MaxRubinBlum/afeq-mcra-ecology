#!/usr/bin/env python3
"""Calculate and plot depth-resolved Shannon diversity from mcrA ASV counts.

Shannon is calculated at the ASV level, not after taxonomic aggregation.
The default workflow uses repeated rarefaction to a common sequencing depth so
alpha diversity is compared at standardized sampling effort.

For every eligible sample, the script performs independent multivariate
hypergeometric subsampling without replacement, calculates Shannon diversity in
each iteration, then reports the mean and standard deviation across iterations.
Samples below the rarefaction depth are retained in the output table with
included=False and no Shannon value.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

SITE_ORDER = ["EA1", "EA2", "EA3", "EA4"]
MONTH_ORDER = ["September", "January", "April", "July"]


def shannon_from_counts(counts: np.ndarray) -> float:
    counts = counts[counts > 0]
    if counts.size == 0:
        return np.nan
    p = counts / counts.sum()
    return float(-(p * np.log(p)).sum())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepared-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--rarefaction-depth", type=int, default=5000)
    ap.add_argument("--iterations", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--dpi", type=int, default=600)
    args = ap.parse_args()

    prep = Path(args.prepared_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    counts = pd.read_csv(prep / "asv_counts_filtered.tsv", sep="\t", index_col=0)
    meta = pd.read_csv(prep / "sample_metadata_ecology.tsv", sep="\t")
    meta = meta[meta["site"].isin(SITE_ORDER) & meta["depth_cm"].notna()].copy()

    rng = np.random.default_rng(args.seed)
    rows = []

    for _, m in meta.iterrows():
        sample = m["sample_id"]
        if sample not in counts.columns:
            continue
        x = counts[sample].to_numpy(dtype=np.int64)
        total = int(x.sum())
        unrarefied = shannon_from_counts(x)

        if total < args.rarefaction_depth:
            rows.append({
                "sample_id": sample,
                "site": m["site"],
                "Month": m.get("Month", ""),
                "season": m.get("season", ""),
                "depth_cm": m["depth_cm"],
                "library_reads": total,
                "unrarefied_shannon": unrarefied,
                "included": False,
                "shannon": np.nan,
                "shannon_sd": np.nan,
            })
            continue

        values = []
        for _ in range(args.iterations):
            draw = rng.multivariate_hypergeometric(x, args.rarefaction_depth)
            values.append(shannon_from_counts(draw))

        rows.append({
            "sample_id": sample,
            "site": m["site"],
            "Month": m.get("Month", ""),
            "season": m.get("season", ""),
            "depth_cm": m["depth_cm"],
            "library_reads": total,
            "unrarefied_shannon": unrarefied,
            "included": True,
            "shannon": float(np.mean(values)),
            "shannon_sd": float(np.std(values, ddof=1)),
        })

    alpha = pd.DataFrame(rows)
    alpha["site_order"] = alpha["site"].map({s: i for i, s in enumerate(SITE_ORDER)})
    alpha["month_order"] = alpha["Month"].map({m: i for i, m in enumerate(MONTH_ORDER)})
    alpha = alpha.sort_values(["site_order", "month_order", "depth_cm"])
    alpha.drop(columns=["site_order", "month_order"]).to_csv(
        out / "shannon_depth_data.tsv", sep="\t", index=False
    )

    diag = alpha[["library_reads", "unrarefied_shannon"]].dropna()
    rho, p = spearmanr(diag["library_reads"], diag["unrarefied_shannon"])
    pd.DataFrame([{
        "n": len(diag),
        "spearman_rho_library_reads_vs_unrarefied_shannon": rho,
        "p_value": p,
        "rarefaction_depth": args.rarefaction_depth,
        "iterations": args.iterations,
        "seed": args.seed,
    }]).to_csv(out / "shannon_library_depth_diagnostic.tsv", sep="\t", index=False)

    summary = (
        alpha[alpha["included"]]
        .groupby(["site", "Month"], as_index=False)
        .agg(
            n=("sample_id", "size"),
            mean_shannon=("shannon", "mean"),
            sd_shannon=("shannon", "std"),
            min_shannon=("shannon", "min"),
            max_shannon=("shannon", "max"),
        )
    )
    summary["site_order"] = summary["site"].map({s: i for i, s in enumerate(SITE_ORDER)})
    summary["month_order"] = summary["Month"].map({m: i for i, m in enumerate(MONTH_ORDER)})
    summary.sort_values(["site_order", "month_order"]).drop(
        columns=["site_order", "month_order"]
    ).to_csv(out / "shannon_site_month_summary.tsv", sep="\t", index=False)

    included = alpha[alpha["included"]].copy()
    if included.empty:
        raise RuntimeError("No samples meet the rarefaction depth")

    xmin = np.floor((included["shannon"].min() - 0.12) * 10) / 10
    xmax = np.ceil((included["shannon"].max() + 0.12) * 10) / 10

    fig, axes = plt.subplots(2, 2, figsize=(9.4, 8.8), sharex=True, sharey=True)
    axes = axes.ravel()

    for ax, site in zip(axes, SITE_ORDER):
        site_df = included[included["site"] == site]
        for month in MONTH_ORDER:
            sub = site_df[site_df["Month"] == month].sort_values("depth_cm")
            if sub.empty:
                continue
            line = ax.plot(sub["shannon"], sub["depth_cm"], marker="o",
                           markersize=5.2, linewidth=1.35, label=month, zorder=3)[0]
            ax.errorbar(sub["shannon"], sub["depth_cm"], xerr=sub["shannon_sd"],
                        fmt="none", ecolor=line.get_color(), elinewidth=0.7,
                        capsize=1.8, alpha=0.65, zorder=2)

        excluded = alpha[(alpha["site"] == site) & (~alpha["included"])]
        for _, row in excluded.iterrows():
            ax.text(xmin + 0.03, row["depth_cm"], "×",
                    ha="left", va="center", fontsize=11, alpha=0.55)

        ax.set_title(site, fontsize=12, fontweight="bold")
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(40, 0)
        ax.set_yticks([0, 10, 20, 30, 40])
        ax.grid(axis="y", linewidth=0.45, alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=9)

    axes[2].set_xlabel("Shannon diversity", fontsize=11)
    axes[3].set_xlabel("Shannon diversity", fontsize=11)
    axes[0].set_ylabel("Sediment depth (cm)", fontsize=11)
    axes[2].set_ylabel("Sediment depth (cm)", fontsize=11)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title="Sampling month", loc="upper center",
               bbox_to_anchor=(0.5, 0.995), ncol=4, frameon=False,
               fontsize=9, title_fontsize=9.5)
    fig.subplots_adjust(top=0.90, bottom=0.08, left=0.10, right=0.98,
                        hspace=0.18, wspace=0.16)

    fig.savefig(out / "shannon_depth.png", dpi=args.dpi, bbox_inches="tight")
    fig.savefig(out / "shannon_depth.pdf", bbox_inches="tight")
    fig.savefig(out / "shannon_depth.svg", bbox_inches="tight")
    plt.close(fig)

    print(f"Depth-resolved samples considered: {len(alpha)}")
    print(f"Samples retained at {args.rarefaction_depth} reads: {int(alpha['included'].sum())}")
    print(f"Samples below rarefaction depth: {int((~alpha['included']).sum())}")
    print("Wrote Shannon data, diagnostic, summary, and figure files to", out)


if __name__ == "__main__":
    main()
