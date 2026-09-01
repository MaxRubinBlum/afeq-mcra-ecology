#!/usr/bin/env python3
"""Prepare clean mcrA tables for ecological analysis.

This script performs only transparent, project-approved filtering:
  1. remove blank/NTC samples;
  2. remove ASVs found only in controls;
  3. remove biological libraries with <1,000 reads;
  4. harmonize taxonomy into ecology labels;
  5. join the corrected Afeq metadata where a matching EA sample exists.

It does NOT rarefy the data and it does NOT alter the original feature table.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
import pandas as pd

CONTROL_RE = re.compile(r"blank|ntc", re.I)
MONTH_PREFIX = {
    "September": "Sep24",
    "January": "Jan25",
    "April": "Apr25",
    "July": "Jul25",
}
AOM_CLADE_LABELS = {
    "ANME-2d": "ANME-2d / Methanoperedenaceae-related",
    "ANME-3": "ANME-3 / Methanovorans-related",
    "ANME-2a": "ANME-2a-related / Methanocomedens",
}


def read_feature_table(path: str) -> pd.DataFrame:
    """Read a QIIME-exported BIOM TSV as ASV x sample counts."""
    return pd.read_csv(path, sep="\t", skiprows=1, index_col=0)


def extract_rank(taxonomy: str, prefix: str) -> str:
    for item in str(taxonomy or "").split(";"):
        item = item.strip()
        if item.startswith(prefix):
            value = item[len(prefix):].strip()
            if value and value.lower() not in {"unclassified", "uncultured", "unknown"}:
                return value
    return ""


def gtdb_ecology_label(taxonomy: str) -> str:
    """Return a conservative human-readable label from GTDB taxonomy."""
    if not taxonomy or taxonomy == "Unassigned":
        return "Unresolved mcrA"

    genus = extract_rank(taxonomy, "g__")
    family = extract_rank(taxonomy, "f__")
    order = extract_rank(taxonomy, "o__")

    if genus == "Methanoperedens" or family == "Methanoperedenaceae":
        return "ANME-2d / Methanoperedenaceae-related"
    if genus.startswith("Methanovorans"):
        return "ANME-3 / Methanovorans-related"
    if genus.startswith("Methanocomedens"):
        return "ANME-2a-related / Methanocomedens"

    if genus:
        return genus
    if family:
        return f"{family}-related"
    if order:
        return f"{order}-related"
    return "Unresolved mcrA"


def build_ecology_labels(master: pd.DataFrame, phy: pd.DataFrame) -> pd.DataFrame:
    """Create one ecology label per ASV."""
    phy_map = phy.set_index("ASV").to_dict("index") if len(phy) else {}
    rows = []

    for _, row in master.iterrows():
        asv = row["ASV"]
        taxonomy = row.get("GTDB_taxonomy", "")
        label = gtdb_ecology_label(taxonomy)
        source = "GTDB"
        confidence = ""

        p = phy_map.get(asv)
        if p:
            aom_clade = str(p.get("AOM_clade", "")).strip()
            phy_label = str(p.get("phylogenetic_assignment", "")).strip()
            if aom_clade in AOM_CLADE_LABELS:
                label = AOM_CLADE_LABELS[aom_clade]
                source = "phylogeny"
                confidence = p.get("assignment_confidence", "")
            elif phy_label == "Unresolved environmental mcrA lineage":
                label = phy_label
                source = "phylogeny"
                confidence = p.get("assignment_confidence", "")

        rows.append({
            "ASV": asv,
            "final_ecology_label": label,
            "label_source": source,
            "label_confidence": confidence,
            "GTDB_taxonomy": taxonomy,
            "GTDB_best_identity": row.get("GTDB_best_identity", ""),
            "environmental_taxonomy": row.get("environmental_taxonomy", ""),
            "environmental_best_identity": row.get("environmental_best_identity", ""),
        })

    return pd.DataFrame(rows)


def canonical_metadata_id(row: pd.Series) -> str | None:
    month = MONTH_PREFIX.get(str(row.get("Month", "")).strip())
    name = str(row.get("name ", "")).strip()
    match = re.search(r"(EA\d+-.+)$", name)
    if not month or not match:
        return None
    return f"{month}-{match.group(1)}"


def parse_sample_name(sample_id: str) -> tuple[str, str, str]:
    match = re.match(r"^(Sep24|Jan25|Apr25|Jul25)-([^-]+)-(.+)$", sample_id)
    if not match:
        return "", "", ""
    return match.group(1), match.group(2), match.group(3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature-table", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--phylogeny", required=True)
    ap.add_argument("--metadata-xlsx", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--min-reads", type=int, default=1000)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    counts = read_feature_table(args.feature_table)
    master = pd.read_csv(args.master, sep="\t")
    phy = pd.read_csv(args.phylogeny, sep="\t")
    metadata = pd.read_excel(args.metadata_xlsx)

    sample_totals = counts.sum(axis=0)
    controls = [s for s in counts.columns if CONTROL_RE.search(s)]
    biological = [s for s in counts.columns if s not in controls]

    bio_sum = counts[biological].sum(axis=1)
    ctrl_sum = counts[controls].sum(axis=1) if controls else pd.Series(0, index=counts.index)
    control_exclusive = counts.index[(bio_sum == 0) & (ctrl_sum > 0)].tolist()

    low_samples = [s for s in biological if sample_totals[s] < args.min_reads]
    kept_samples = [s for s in biological if s not in low_samples]
    kept_asvs = [a for a in counts.index if a not in set(control_exclusive)]

    clean_counts = counts.loc[kept_asvs, kept_samples].copy()
    labels = build_ecology_labels(master, phy).set_index("ASV")
    missing_labels = clean_counts.index.difference(labels.index)
    if len(missing_labels):
        raise RuntimeError(f"{len(missing_labels)} ASVs are missing from the annotation table")

    clean_counts.to_csv(out / "asv_counts_filtered.tsv", sep="\t", index_label="ASV")
    selected_labels = labels.loc[clean_counts.index].copy()
    selected_labels.index.name = "ASV"
    selected_labels.reset_index().to_csv(out / "asv_ecology_labels.tsv", sep="\t", index=False)

    tmp = clean_counts.copy()
    tmp["final_ecology_label"] = labels.loc[tmp.index, "final_ecology_label"].values
    lineage_counts = tmp.groupby("final_ecology_label", sort=False).sum()
    lineage_counts.to_csv(out / "lineage_counts.tsv", sep="\t", index_label="lineage")

    lineage_rel = lineage_counts.div(lineage_counts.sum(axis=0), axis=1) * 100.0
    lineage_rel.to_csv(out / "lineage_relative_abundance_pct.tsv", sep="\t", index_label="lineage")

    sample_info = []
    for sample in kept_samples:
        season, site, profile_id = parse_sample_name(sample)
        sample_info.append({
            "sample_id": sample,
            "season": season,
            "site": site,
            "profile_id": profile_id,
            "library_reads": int(clean_counts[sample].sum()),
        })
    sample_info = pd.DataFrame(sample_info)

    metadata = metadata.copy()
    metadata["sample_id"] = metadata.apply(canonical_metadata_id, axis=1)
    metadata = metadata.dropna(subset=["sample_id"])
    if metadata["sample_id"].duplicated().any():
        dup = metadata.loc[metadata["sample_id"].duplicated(False), "sample_id"].tolist()
        raise RuntimeError(f"Duplicate canonical sample IDs in metadata: {dup}")

    useful_meta = metadata.rename(columns={
        "Depth": "depth_cm",
        "Wetland name": "metadata_site",
        "Methane ": "methane",
        "SO4 (mM)": "sulfate_mM",
        "H2S (µM)": "h2s_uM",
        "Fe (µM)": "fe_uM",
        "DIC (mM)": "dic_mM",
        "PO43- (µM)": "phosphate_uM",
    })

    keep_cols = [
        "sample_id", "SampleID", "Month", "depth_cm", "metadata_site",
        "methane", "sulfate_mM", "h2s_uM", "fe_uM", "dic_mM", "phosphate_uM",
    ]
    useful_meta = useful_meta[[c for c in keep_cols if c in useful_meta.columns]]
    sample_info = sample_info.merge(useful_meta, on="sample_id", how="left")
    sample_info.to_csv(out / "sample_metadata_ecology.tsv", sep="\t", index=False)

    long = lineage_rel.T.reset_index(names="sample_id").melt(
        id_vars="sample_id", var_name="lineage", value_name="relative_abundance_pct"
    )
    long = long.merge(sample_info, on="sample_id", how="left")
    long.to_csv(out / "lineage_relative_abundance_long.tsv", sep="\t", index=False)

    qc = pd.DataFrame([
        ["all_samples", len(counts.columns)],
        ["controls", len(controls)],
        ["biological_before_depth_filter", len(biological)],
        ["biological_below_min_reads", len(low_samples)],
        ["biological_retained", len(kept_samples)],
        ["control_exclusive_asvs_removed", len(control_exclusive)],
        ["asvs_retained", len(kept_asvs)],
        ["metadata_matched_retained_samples", int(sample_info["depth_cm"].notna().sum())],
    ], columns=["metric", "value"])
    qc.to_csv(out / "ecology_qc_summary.tsv", sep="\t", index=False)

    pd.DataFrame({"sample_id": low_samples, "reads": [int(sample_totals[s]) for s in low_samples]}).to_csv(
        out / "excluded_low_depth_samples.tsv", sep="\t", index=False
    )
    pd.DataFrame({"ASV": control_exclusive, "control_reads": [int(ctrl_sum[a]) for a in control_exclusive]}).to_csv(
        out / "excluded_control_exclusive_asvs.tsv", sep="\t", index=False
    )

    print(qc.to_string(index=False))
    print("Wrote prepared ecology tables to", out)


if __name__ == "__main__":
    main()
