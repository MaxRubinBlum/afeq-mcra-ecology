#!/usr/bin/env python3
"""Bray-Curtis ordination and transparent one-factor PERMANOVA tests.

The community matrix is transformed as sqrt(relative abundance) before
Bray-Curtis calculation. This keeps Bray-Curtis' ecological interpretation while
reducing the leverage of the most abundant ASVs.

The PERMANOVA implementation here is deliberately limited to ONE factor at a
time. Tests are stratified to reduce obvious design confounding:
  * site differences within each season among EA sites;
  * season differences within EA1 and EA2, which were sampled in all seasons.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt

SEASON_ORDER = ["Sep24", "Jan25", "Apr25", "Jul25"]


def pcoa(distance: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Classical PCoA from a square distance matrix."""
    n = distance.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (distance ** 2) @ J
    eigvals, eigvecs = np.linalg.eigh(B)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    positive = eigvals > 1e-12
    coords = eigvecs[:, positive] * np.sqrt(eigvals[positive])
    return coords, eigvals, eigvals[positive]


def permanova_one_factor(distance: np.ndarray, groups: np.ndarray, permutations: int, rng: np.random.Generator) -> tuple[float, float, float]:
    """One-way PERMANOVA pseudo-F, R2, and permutation p-value."""
    groups = np.asarray(groups)
    n = len(groups)
    levels = np.unique(groups)
    if len(levels) < 2:
        return np.nan, np.nan, np.nan

    d2 = distance ** 2
    ss_total = d2[np.triu_indices(n, 1)].sum() / n

    def statistic(labels: np.ndarray) -> tuple[float, float]:
        ss_within = 0.0
        for level in np.unique(labels):
            idx = np.where(labels == level)[0]
            ng = len(idx)
            if ng > 1:
                sub = d2[np.ix_(idx, idx)]
                ss_within += sub[np.triu_indices(ng, 1)].sum() / ng
        ss_between = ss_total - ss_within
        df_between = len(np.unique(labels)) - 1
        df_within = n - len(np.unique(labels))
        F = (ss_between / df_between) / (ss_within / df_within)
        R2 = ss_between / ss_total
        return F, R2

    observed_F, observed_R2 = statistic(groups)
    exceed = 0
    for _ in range(permutations):
        permuted = rng.permutation(groups)
        perm_F, _ = statistic(permuted)
        if perm_F >= observed_F - 1e-12:
            exceed += 1
    p = (exceed + 1) / (permutations + 1)
    return observed_F, observed_R2, p


def permdisp_one_factor(distance: np.ndarray, groups: np.ndarray, permutations: int, rng: np.random.Generator) -> tuple[float, float]:
    """Permutation test for differences in multivariate dispersion."""
    coords, _, _ = pcoa(distance)
    groups = np.asarray(groups)

    def dispersion_f(labels: np.ndarray) -> float:
        dist_to_centroid = np.zeros(len(labels))
        for level in np.unique(labels):
            idx = np.where(labels == level)[0]
            centroid = coords[idx].mean(axis=0)
            dist_to_centroid[idx] = np.linalg.norm(coords[idx] - centroid, axis=1)
        grand = dist_to_centroid.mean()
        ss_between = 0.0
        ss_within = 0.0
        for level in np.unique(labels):
            vals = dist_to_centroid[labels == level]
            ss_between += len(vals) * (vals.mean() - grand) ** 2
            ss_within += ((vals - vals.mean()) ** 2).sum()
        df_between = len(np.unique(labels)) - 1
        df_within = len(labels) - len(np.unique(labels))
        return (ss_between / df_between) / (ss_within / df_within)

    observed = dispersion_f(groups)
    exceed = 0
    for _ in range(permutations):
        permuted = rng.permutation(groups)
        F = dispersion_f(permuted)
        if F >= observed - 1e-12:
            exceed += 1
    return observed, (exceed + 1) / (permutations + 1)


def run_test(name: str, indices: np.ndarray, group_values: np.ndarray, D: np.ndarray, permutations: int, rng: np.random.Generator) -> dict:
    subD = D[np.ix_(indices, indices)]
    groups = group_values[indices]
    F, r2, p = permanova_one_factor(subD, groups, permutations, rng)
    dispF, dispp = permdisp_one_factor(subD, groups, permutations, rng)
    return {
        "test": name,
        "n": len(indices),
        "groups": len(np.unique(groups)),
        "pseudo_F": F,
        "R2": r2,
        "permanova_p": p,
        "dispersion_F": dispF,
        "permdisp_p": dispp,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepared-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--permutations", type=int, default=999)
    ap.add_argument("--seed", type=int, default=20260901)
    args = ap.parse_args()

    prep = Path(args.prepared_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    counts = pd.read_csv(prep / "asv_counts_filtered.tsv", sep="\t", index_col=0).T
    meta = pd.read_csv(prep / "sample_metadata_ecology.tsv", sep="\t").set_index("sample_id").loc[counts.index]
    meta.index.name = "sample_id"

    rel = counts.div(counts.sum(axis=1), axis=0)
    transformed = np.sqrt(rel.to_numpy(dtype=float))
    D = squareform(pdist(transformed, metric="braycurtis"))

    coords, eigvals, positive = pcoa(D)
    explained = positive / positive.sum()
    coord_df = pd.DataFrame({
        "sample_id": counts.index,
        "PCoA1": coords[:, 0],
        "PCoA2": coords[:, 1],
    }).merge(meta.reset_index(), on="sample_id", how="left")
    coord_df.to_csv(out / "bray_pcoa_coordinates.tsv", sep="\t", index=False)

    pd.DataFrame({"eigenvalue": eigvals}).to_csv(out / "pcoa_eigenvalues.tsv", sep="\t", index=False)
    pd.DataFrame(D, index=counts.index, columns=counts.index).to_csv(
        out / "bray_curtis_distance.tsv", sep="\t", index_label="sample_id"
    )

    fig, ax = plt.subplots(figsize=(8, 7))
    for site, grp in coord_df.groupby("site", sort=True):
        ax.scatter(grp["PCoA1"], grp["PCoA2"], label=site, alpha=0.78, s=42)
    ax.axhline(0, linewidth=0.6, alpha=0.3)
    ax.axvline(0, linewidth=0.6, alpha=0.3)
    ax.set_xlabel(f"PCoA1 ({100*explained[0]:.1f}% of positive-axis variation)")
    ax.set_ylabel(f"PCoA2 ({100*explained[1]:.1f}% of positive-axis variation)")
    ax.set_title("mcrA ASV composition: Bray-Curtis PCoA")
    ax.legend(title="Site", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    plt.tight_layout()
    plt.savefig(out / "bray_pcoa_by_site.png", dpi=220)
    plt.close()

    rng = np.random.default_rng(args.seed)
    sites = meta["site"].to_numpy(str)
    seasons = meta["season"].to_numpy(str)
    tests = []

    for season in SEASON_ORDER:
        idx = np.where((seasons == season) & np.char.startswith(sites.astype(str), "EA"))[0]
        kept_levels = [x for x in np.unique(sites[idx]) if np.sum(sites[idx] == x) >= 2]
        idx = np.array([i for i in idx if sites[i] in kept_levels], dtype=int)
        if len(kept_levels) >= 2:
            tests.append(run_test(f"site_within_{season}", idx, sites, D, args.permutations, rng))

    for site in ["EA1", "EA2"]:
        idx = np.where(sites == site)[0]
        tests.append(run_test(f"season_within_{site}", idx, seasons, D, args.permutations, rng))

    idx = np.arange(len(sites))
    tests.append(run_test("site_all_samples_descriptive", idx, sites, D, args.permutations, rng))

    results = pd.DataFrame(tests)
    results.to_csv(out / "permanova_permdisp_tests.tsv", sep="\t", index=False)

    negative_fraction = abs(eigvals[eigvals < 0].sum()) / positive.sum() if np.any(eigvals < 0) else 0.0
    print(f"Samples: {len(counts)}")
    print(f"ASVs: {counts.shape[1]}")
    print(f"PCoA1: {100*explained[0]:.2f}% of positive-axis variation")
    print(f"PCoA2: {100*explained[1]:.2f}% of positive-axis variation")
    print(f"Absolute negative eigenvalue sum / positive sum: {negative_fraction:.4f}")
    print("Wrote Bray-Curtis, PCoA, PERMANOVA, and PERMDISP outputs to", out)


if __name__ == "__main__":
    main()
