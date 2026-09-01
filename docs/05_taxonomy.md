# Taxonomy strategy: why two databases are used

## Problem

mcrA taxonomy is difficult because environmental diversity extends far beyond cultivated/genome-represented lineages. A single database does not optimize both coverage and naming quality.

## Database 1 — broad environmental mcrA reference

Project database:

```text
update_mcrA_db/databases/mcrA_ncbi_nt_cur_db/qiime2/
```

Files:

```text
mcrA_ncbi_nt_cur_db_seqs.fasta
mcrA_ncbi_nt_cur_db_taxonomy.tsv
```

This curated database contains about 27,942 environmental mcrA references and gives broad sequence coverage.

### Strength

Very high probability of finding an environmentally close sequence.

### Weakness

Many reference labels are taxonomically coarse, e.g. `uncultured archaeon`, so a high sequence identity may still yield an uninformative name.

## Database 2 — GTDB R232 genome-derived mcrA

A second reference set was constructed from genome-derived mcrA sequences and current GTDB R232 archaeal taxonomy.

After mapping the original genome-derived mcrA references to GTDB:

```text
mcrA references: 1572
matched to GTDB R232 taxonomy: 1316
unmatched: 256
```

After in-silico MLf/MLr amplicon extraction:

```text
GTDB-mapped full references: 1316
MLf/MLr-compatible references: 1021
```

Amplicon lengths:

```text
minimum: 409 bp
median:  415 bp
maximum: 439 bp
```

This closely matched the observed ASV length distribution.

### Strength

Much cleaner current genome taxonomy.

### Weakness

Lower environmental breadth and sometimes low identity to environmentally abundant ASVs.

## VSEARCH settings used for both classifications

```text
minimum identity: 0.80
minimum query coverage: 0.80
max accepts: 10
max rejects: all
minimum consensus: 0.51
threads: 24
```

`Consensus` in QIIME's taxonomy output is **agreement among accepted reference taxonomies**, not sequence identity.

## Why no arbitrary 95% mcrA filter is applied

mcrA lineages can be deeply divergent. Filtering all ASVs below 90–95% identity would preferentially delete biologically interesting environmental lineages. Identity is treated as evidence/confidence, not as a universal validity cutoff.

## Observed GTDB performance

In the completed master table:

```text
14,260 ASVs
15,837,298 biological reads
```

Best-hit identity categories:

```text
>=95%:   4,616 ASVs; 5,090,006 reads
90-95%:  5,456 ASVs; 8,437,163 reads
80-90%:  4,188 ASVs; 2,310,129 reads
```

GTDB greatly improved names, but the abundant <90% fraction motivated targeted phylogenetic placement.
