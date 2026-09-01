# Results directory

Only small, non-sensitive QC/provenance summaries belong here.

Do not commit the complete feature table, complete unpublished metadata, large alignments, QIIME artifacts, raw sequencing data, or generated ecological result tables/figures.

Recommended local outputs include:

```text
mcrA_ASV_master_annotation.tsv
mcrA_phylogenetic_assignments_287.tsv
mcrA_phylogeny_summary.tsv
mcrA_GTR.contree
```

These should normally remain in the analysis workspace rather than GitHub.

## Ecology outputs

The scripts in `scripts/13_*` through `scripts/18_*` generate ecology tables and figures under the directory configured as `ECOLOGY_OUT`. These generated outputs are not committed by default. See `docs/14_ecology_analysis_pipeline.md` for the exact output tree and file definitions.
