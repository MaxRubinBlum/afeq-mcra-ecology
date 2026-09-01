# Troubleshooting

## `ModuleNotFoundError: No module named 'Bio'`

The QIIME environment used here did not contain Biopython. The workflow scripts avoid requiring it. For simple FASTA length checks, use the supplied standard-library scripts rather than installing packages into the QIIME environment mid-analysis.

## `qiime feature-table summarize` rejects `--o-visualization`

QIIME 2 2026.1 uses:

```bash
--o-summary table.qzv
--o-feature-frequencies feature-frequencies.qza
--o-sample-frequencies sample-frequencies.qza
```

## DADA2 asks for `--o-base-transition-stats`

This is expected in QIIME 2 amplicon 2026.1. Save the output and optionally visualize it with `qiime dada2 plot-base-transitions`.

## GTDB in-silico PCR yields very few sequences

Check:

1. primer orientation;
2. use of the **reverse complement** of MLr on the reference sequence;
3. linked-adapter syntax;
4. whether the mcrA reference sequences include the primer-binding region;
5. error tolerance.

In the completed run, 1,021 of 1,316 GTDB-mapped references survived and had 409–439 bp amplicons. A result near zero would indicate a workflow problem.

## MAFFT alignment begins with many gaps

This can be normal when some environmental references have longer terminal regions. Check alignment length, leading/trailing gaps, and ungapped sequence lengths. In this project the common region was ~415 bp but the first alignment expanded to 526 columns because of terminal overhangs.

## IQ-TREE ModelFinder is taking too long

For the targeted amplicon tree, use the documented fixed model:

```text
GTR+F+G4
```

The goal is local clade placement, not exhaustive nucleotide model comparison.

## IQ-TREE says fewer taxa during bootstrap calculation

IQ-TREE can collapse identical sequences internally for efficiency. Check the final tree and log before concluding that sequences were lost.

## Taxonomy says `Consensus = 1.0`; is that 100% identity?

No. QIIME consensus is taxonomic agreement among accepted hits. Sequence identity is stored in the VSEARCH `blast6.tsv` output and should be considered separately.

## A biological ASV appears in a blank

Do not automatically delete it. Compare blank abundance with biological abundance and prevalence. Tiny blank counts for a massively abundant biological ASV are consistent with carryover/index leakage.
