# Project status

## Completed

- paired-end mcrA sample parsing and canonical IDs;
- primer trimming;
- independent DADA2 runs for Sep/Jan and Apr/Jul;
- merged ASV table;
- blank/NTC assessment;
- environmental mcrA classification;
- GTDB R232 genome-derived mcrA reference construction;
- GTDB classification;
- master ASV annotation;
- targeted phylogenetic refinement of 287 abundant/divergent ASVs;
- principal ANME clade assignments;
- corrected metadata validation;
- ecology-ready ASV/lineage table preparation;
- descriptive composition and depth-profile scripts;
- depth-resolved bubble-plot script;
- repeated-rarefaction Shannon diversity script;
- Bray-Curtis PCoA + one-factor PERMANOVA/PERMDISP script;
- lineage/geochemistry Spearman + BH-FDR script.

## Current analysis dataset QC

```text
14,260 ASVs before ecology filtering
150 biological mcrA libraries before depth filtering
10 controls
145 biological libraries retained for ecology after <1,000-read filtering
```

## Analysis documentation

The complete post-taxonomy ecology workflow is documented in `docs/14_ecology_analysis_pipeline.md`. Generated ecological result tables and figures should remain outside Git unless deliberately selected for release.
