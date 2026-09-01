# From ASVs to ecology-ready data

This chapter defines the transition from taxonomic/phylogenetic annotation to the ecological analysis layer. It describes data structure and analysis rules only; interpretation belongs in reports and manuscripts, not in the pipeline documentation.

## Keep annotation evidence separate from ecology labels

Before ecological analysis, propagate the targeted phylogenetic refinements into one harmonized ecology label per ASV. Keep the original GTDB and environmental annotations as separate columns so the source evidence is never lost.

Recommended columns:

```text
ASV
final_ecology_label
label_source
label_confidence
GTDB_taxonomy
GTDB_best_identity
environmental_taxonomy
environmental_best_identity
```

Do not force every rare or divergent ASV to genus level.

## Sample filtering before ecology

The project-specific rules implemented in `13_prepare_ecology_tables.py` are:

```text
remove controls from biological analyses
remove only ASVs that are exclusive to controls
remove biological libraries with <1,000 reads
retain raw ASV counts for all remaining samples and ASVs
```

Do not remove every ASV that occurs in a blank. An ASV shared between a blank and biological libraries remains in the biological table unless a separate contamination analysis justifies another rule.

## Relative abundance

For descriptive lineage plots:

```text
relative abundance (%) = lineage reads / total retained reads in that sample × 100
```

Always retain the corresponding raw ASV count table. Alpha diversity and any method requiring counts must use counts rather than lineage percentages.

## Analysis layers

The ecology pipeline separates five tasks:

1. preparation and label harmonization;
2. descriptive lineage composition and depth profiles;
3. Shannon alpha diversity from ASV counts;
4. Bray-Curtis beta diversity with PCoA, PERMANOVA, and PERMDISP;
5. exploratory lineage/geochemistry association tables.

The complete implementation, reasoning, inputs, outputs, and commands are documented in [14_ecology_analysis_pipeline.md](14_ecology_analysis_pipeline.md).

## Reproducibility rule

Do not edit ecological outputs manually. If a filtering threshold, lineage rule, rarefaction depth, or statistical design changes, change the script/configuration and regenerate the output.
