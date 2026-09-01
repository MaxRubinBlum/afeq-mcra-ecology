# mcrA ecological analysis pipeline

This chapter starts **after** ASV inference, taxonomy, control review, and targeted phylogenetic refinement are complete. It explains how to turn the final mcrA ASV table into reproducible ecological tables, figures, alpha diversity, beta diversity, and metadata-association outputs.

The goal is methodological transparency. This chapter describes **what each analysis does, why it is used, what it requires, and what it writes**. It intentionally does not interpret the biological results.

## 1. Where this stage begins

The ecology layer requires four project outputs from the preceding workflow:

```text
feature-table.tsv
mcrA_ASV_master_annotation.tsv
mcrA_phylogenetic_assignments_287.tsv
corrected metadata workbook (.xlsx)
```

### `feature-table.tsv`

This is the merged ASV feature table exported from QIIME 2. Rows are ASVs and columns are samples. The first line may contain the standard BIOM export comment beginning with `# Constructed from biom file`; script 13 handles this with `skiprows=1`.

### `mcrA_ASV_master_annotation.tsv`

This table contains the abundance-independent annotation evidence for every ASV, including GTDB taxonomy, GTDB best-hit identity, environmental-database taxonomy, environmental best-hit identity, and phylogeny priority.

### `mcrA_phylogenetic_assignments_287.tsv`

This contains conservative phylogenetic assignments for the abundant/divergent ASVs selected for the targeted mcrA tree.

### Corrected metadata workbook

The workbook supplies validated sample identities, month, measured depth, and available geochemistry. Do not substitute an older workbook because sample-to-metadata alignment is part of the analysis provenance.

## 2. Configuration

Copy the configuration template:

```bash
cp config/config.example.sh config/config.sh
```

Edit the local paths. The ecology layer uses these variables:

```bash
export MCRA_FEATURE_TABLE="$MCRA_OUT/merged/export-table/feature-table.tsv"
export MCRA_MASTER_ANNOTATION="$MCRA_OUT/merged/mcrA_ASV_master_annotation.tsv"
export MCRA_PHYLOGENY_ASSIGNMENTS="$MCRA_OUT/merged/phylogeny/mcrA_phylogenetic_assignments_287.tsv"
export METADATA_XLSX="$BASE/Metadata_1st_year (16S).xlsx"
export ECOLOGY_OUT="$MCRA_OUT/ecology"

export RAREFACTION_DEPTH=5000
export SHANNON_ITERATIONS=50
export PERMUTATIONS=999
export RANDOM_SEED=20260901
```

The exact local paths may differ. Do not commit `config/config.sh`; it can contain workstation-specific paths.

## 3. Run the complete ecology stage

From the repository root:

```bash
bash scripts/run_ecology_pipeline.sh config/config.sh
```

The runner executes scripts 13-18 in numerical order and writes each analysis into its own output directory.

Recommended output layout:

```text
ecology/
├── prepared/
├── composition/
├── depth_bubble/
├── shannon/
├── ordination/
└── geochemistry/
```

Generated outputs are intentionally not version-controlled. Commit the scripts and documentation, not private result tables or manuscript figures.

---

# 4. Step 13 — prepare ecology tables

Script: `scripts/13_prepare_ecology_tables.py`

## Purpose

Create a single transparent, reproducible input layer for all later ecological analyses.

## Why this step exists

Statistical and plotting scripts should not independently make different decisions about controls, low-depth samples, or taxonomy labels. Script 13 applies those decisions once and writes standardized tables that every downstream script reads.

## Filtering rules

The script:

1. identifies controls from sample IDs containing `blank` or `NTC`;
2. removes controls from the biological sample matrix;
3. identifies ASVs that occur in controls but have zero reads in all biological samples;
4. removes only those **control-exclusive ASVs**;
5. removes biological libraries below `--min-reads` (default 1,000 reads);
6. keeps the original ASV counts unchanged for all retained ASVs and samples.

It does **not** remove every ASV observed in a blank. Shared biological/control ASVs remain in the table because presence in a blank alone does not establish contamination.

## Ecology-label harmonization

The script builds a project-specific `final_ecology_label` from the GTDB and phylogenetic annotations.

The rule is:

- use GTDB taxonomy as the general taxonomic backbone;
- let targeted phylogeny override the label for explicitly resolved AOM clades and unresolved environmental lineages;
- do not split conventional methanogen groups into artificial categories such as `Methanoregula` and `Methanoregula-related` when the evidence supports the same ecological category.

The original GTDB and environmental annotations remain in the output, so the harmonized label never replaces the underlying evidence.

## Command

```bash
python scripts/13_prepare_ecology_tables.py \
  --feature-table "$MCRA_FEATURE_TABLE" \
  --master "$MCRA_MASTER_ANNOTATION" \
  --phylogeny "$MCRA_PHYLOGENY_ASSIGNMENTS" \
  --metadata-xlsx "$METADATA_XLSX" \
  --min-reads 1000 \
  --output-dir "$ECOLOGY_OUT/prepared"
```

## Outputs

```text
asv_counts_filtered.tsv
asv_ecology_labels.tsv
lineage_counts.tsv
lineage_relative_abundance_pct.tsv
lineage_relative_abundance_long.tsv
sample_metadata_ecology.tsv
ecology_qc_summary.tsv
excluded_low_depth_samples.tsv
excluded_control_exclusive_asvs.tsv
```

`asv_counts_filtered.tsv` is the ASV × sample raw-count table after approved filtering. `asv_ecology_labels.tsv` stores one ecology label per retained ASV plus source annotation evidence. `lineage_counts.tsv` and `lineage_relative_abundance_pct.tsv` are lineage-level matrices. `lineage_relative_abundance_long.tsv` is a plotting/statistics table. `sample_metadata_ecology.tsv` stores one row per retained biological library. The remaining files record QC and exclusions.

## Checkpoint before continuing

Confirm that sample IDs and ASV IDs are unique, retained sample columns match `sample_metadata_ecology.tsv`, lineage relative abundances sum to approximately 100% per sample, and all ASVs in the count table have an ecology label.

---

# 5. Step 14 — composition summaries and focused depth profiles

Script: `scripts/14_composition_profiles.py`

## Purpose

Generate basic descriptive tables and figures before formal multivariate analysis.

## Inputs

From `prepared/`:

```text
lineage_relative_abundance_long.tsv
sample_metadata_ecology.tsv
lineage_counts.tsv
```

## Main operations

### Site × season composition

The script selects globally abundant lineage categories and groups remaining categories as `Other mcrA` for plotting. Categories are first summed **within each sample**, and only then averaged across samples in a site × season group. This guarantees that plotting categories retain the correct compositional total before group means are calculated.

### EA1 ANME-2d depth profile

The script extracts measured depths and ANME-2d relative abundance for EA1 and writes both a table and a simple depth-profile figure. This is a focused visualization step; it does not perform a statistical test.

### ANME-2d site × season summary

The script reports count, mean, median, and maximum relative abundance for each site × season combination.

## Command

```bash
python scripts/14_composition_profiles.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/composition"
```

## Outputs

```text
site_season_mean_composition.tsv
composition_site_season.png
EA1_ANME2d_profile.tsv
EA1_ANME2d_vertical_profile.png
ANME2d_site_season_summary.tsv
```

These outputs are descriptive and are not inferential tests.

---

# 6. Step 15 — depth-resolved bubble plot

Script: `scripts/15_depth_bubble_plot.py`

## Purpose

Show lineage composition and sediment depth simultaneously while preserving individual sample observations.

## Why a bubble plot

A stacked bar plot summarizes composition efficiently but does not naturally preserve depth. The bubble plot adds measured depth as a continuous axis while retaining lineage identity and relative abundance.

## Visual encoding

```text
facet row      = site
facet column   = sampling month
x position     = lineage
y position     = measured depth (cm)
bubble area    = relative abundance (%)
```

Depth increases downward in every panel and every panel uses the same depth scale.

## Lineage selection

By default the script displays the nine most abundant lineages in the retained dataset, plus ANME-2d and the unresolved environmental mcrA lineage if either is not already included. This makes selection reproducible while retaining a visible category for poorly classified environmental sequences.

## Small-value threshold

Values below `--min-percent` are not drawn, but they remain in the exact figure-data table. The default is 0.25%.

## Command

```bash
python scripts/15_depth_bubble_plot.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/depth_bubble" \
  --top-n 9 \
  --min-percent 0.25 \
  --max-depth 40
```

## Outputs

```text
mcrA_depth_bubble.png
mcrA_depth_bubble.pdf
mcrA_depth_bubble.svg
mcrA_depth_bubble_data.tsv
mcrA_depth_bubble_lineages.tsv
```

The TSV files are the provenance layer for the figure and allow every plotted point to be traced to a sample and value.

---

# 7. Step 16 — Shannon alpha diversity

Script: `scripts/16_shannon_alpha.py`

## Purpose

Calculate Shannon diversity from the **ASV count table** and compare depth-resolved samples at standardized sequencing effort.

## Why ASV counts, not lineage counts

Shannon alpha diversity measures diversity among observed ASVs. Taxonomic aggregation would merge distinct ASVs and change the quantity being measured.

## Why standardize sequencing depth

Alpha-diversity estimates can change with library size because deeper sequencing detects more low-abundance ASVs. The pipeline therefore uses repeated rarefaction to a common read count before calculating Shannon.

The default settings are:

```text
rarefaction depth = 5,000 reads
iterations        = 50
random seed       = 20260901
```

A sample with fewer reads than the rarefaction depth cannot be subsampled to that target and is marked `included=False` in the output table.

## Repeated rarefaction procedure

For each eligible sample:

1. draw exactly 5,000 reads without replacement using a multivariate hypergeometric sampler;
2. calculate Shannon diversity;
3. repeat 50 times;
4. report the mean Shannon value;
5. report the standard deviation among rarefaction iterations.

The fixed seed makes the analysis reproducible.

## Library-depth diagnostic

The script also calculates unrarefied Shannon and writes a Spearman correlation between library reads and unrarefied Shannon. This is a methodological diagnostic and not an ecological hypothesis test.

## Command

```bash
python scripts/16_shannon_alpha.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/shannon" \
  --rarefaction-depth 5000 \
  --iterations 50 \
  --seed 20260901
```

## Outputs

```text
shannon_depth_data.tsv
shannon_library_depth_diagnostic.tsv
shannon_site_month_summary.tsv
shannon_depth.png
shannon_depth.pdf
shannon_depth.svg
```

The plot uses a 2 × 2 site grid. Within each site, month-specific Shannon profiles are plotted against measured sediment depth. Horizontal error bars are the standard deviation across rarefaction iterations. A cross marks the depth of a library that did not meet the rarefaction threshold.

---

# 8. Step 17 — Bray-Curtis PCoA, PERMANOVA, and PERMDISP

Script: `scripts/17_bray_pcoa_permanova.py`

## Purpose

Quantify differences in ASV community composition among samples and provide transparent one-factor multivariate tests.

## Input matrix

The analysis uses `prepared/asv_counts_filtered.tsv`. Rows are transposed internally to samples × ASVs.

## Transformation

For each sample:

```text
relative abundance = ASV count / sample total
transformed value  = sqrt(relative abundance)
```

This square-root relative-abundance transformation reduces the leverage of the most abundant ASVs while preserving all retained ASVs.

## Bray-Curtis distance and PCoA

The script calculates pairwise Bray-Curtis dissimilarity on the transformed sample × ASV matrix. Principal Coordinates Analysis is calculated directly from the distance matrix by eigendecomposition of the double-centered squared-distance matrix.

The script writes PCoA sample coordinates, eigenvalues, a Bray-Curtis distance matrix, and a site-colored PCoA figure.

## PERMANOVA design

The implementation is intentionally limited to one factor at a time. This keeps the code transparent and prevents a simple script from silently fitting an inappropriate multifactor design.

The standard tests are:

```text
site within September
site within January
site within April
site within July
season within EA1
season within EA2
all-sample site test (descriptive design check)
```

Groups represented by fewer than two samples in a seasonal site test are omitted from that test.

## PERMDISP

Every PERMANOVA test is accompanied by a permutation test of multivariate dispersion. PERMANOVA and PERMDISP answer different questions and should be retained together in the output.

## Reproducibility

Permutation count and random seed are command-line arguments. The default runner uses 999 permutations and seed 20260901.

## Command

```bash
python scripts/17_bray_pcoa_permanova.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/ordination" \
  --permutations 999 \
  --seed 20260901
```

## Outputs

```text
bray_curtis_distance.tsv
bray_pcoa_coordinates.tsv
pcoa_eigenvalues.tsv
bray_pcoa_by_site.png
permanova_permdisp_tests.tsv
```

`permanova_permdisp_tests.tsv` contains sample count, number of groups, pseudo-F, R², PERMANOVA p-value, dispersion F, and PERMDISP p-value for each predefined test.

---

# 9. Step 18 — lineage/geochemistry associations

Script: `scripts/18_geochemistry_associations.py`

## Purpose

Create transparent exploratory rank-correlation tables between lineage relative abundance and available metadata variables.

This stage uses lineage-level relative abundance because the input question concerns broad mcrA lineage composition rather than individual ASVs.

## Metadata variables

The current script checks available columns among:

```text
depth_cm
methane
sulfate_mM
h2s_uM
fe_uM
dic_mM
phosphate_uM
```

## Lineage selection

The script selects the globally dominant lineages and explicitly retains resolved AOM categories if present.

## Why Spearman correlation

Relative-abundance variables are bounded and frequently contain zeros. Spearman rank correlation does not require a linear relationship or normally distributed variables.

## Pooled and site-stratified tables

The script calculates pooled EA correlations and site-specific correlations where sample size is at least `--min-n`. Both are written to the same results table with a `scope` column.

## Multiple testing

Benjamini-Hochberg FDR adjustment is calculated **separately within each scope**.

## Command

```bash
python scripts/18_geochemistry_associations.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/geochemistry" \
  --top-lineages 10 \
  --min-n 8
```

## Outputs

```text
metadata_lineage_joined.tsv
lineage_geochemistry_spearman.tsv
ANME2d_geochemistry_samples.tsv
```

`metadata_lineage_joined.tsv` is the exact sample-level table used for correlation calculations. `lineage_geochemistry_spearman.tsv` contains one row per scope × lineage × metadata-variable test with `scope`, `lineage`, `variable`, `n`, `spearman_rho`, `p_value`, `nonzero_lineage_samples`, and `fdr_bh`. `ANME2d_geochemistry_samples.tsv` is a convenience table for focused plotting or later modeling and is not a separate statistical test.

---

# 10. Reproducibility checklist

Before using an output in a report, thesis, or manuscript, record:

```text
Git commit SHA
metadata workbook version/date
QIIME artifact provenance or source export
minimum library-read threshold
rarefaction depth and iteration count
permutation count
random seed
script command
```

Do not edit result TSV files manually. If a threshold, lineage-selection rule, or statistical design changes, rerun the relevant script and keep the command used.

## Recommended student habit

For each analysis directory, create a small plain-text `RUN.txt` containing the exact command and date. Example:

```text
2026-09-01
python scripts/16_shannon_alpha.py \
  --prepared-dir results/ecology/prepared \
  --output-dir results/ecology/shannon \
  --rarefaction-depth 5000 \
  --iterations 50 \
  --seed 20260901
```

This makes it possible to reconstruct a figure or table months later without relying on memory.

# 11. What this pipeline does not do

The current ecology layer intentionally does not:

```text
infer metabolic rates from relative abundance
fit causal models
perform multifactor PERMANOVA with interactions
model nonlinear depth profiles
apply one universal compositional-data correction
combine 16S and mcrA data
```

Those require separate analysis decisions and should be added as new scripts rather than hidden inside the existing workflow.
