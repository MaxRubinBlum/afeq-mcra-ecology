# Building the GTDB R232 mcrA reference set

## Goal

Assign current GTDB taxonomy to genome-derived mcrA sequences, then extract only the region that would be amplified by MLf/MLr.

## Inputs

GTDB R232 archaeal files:

```text
ar53_taxonomy_r232.tsv.gz
ar53_metadata_r232.tsv.gz
```

Genome-derived mcrA reference FASTA from the mcrA database repository:

```text
mcrA_ncbi_genome_db_seqs.fasta
```

## Mapping strategy

Genome accessions may differ in several harmless ways:

- `GB_` or `RS_` prefixes in GTDB;
- GenBank vs RefSeq aliases;
- accession version differences;
- multiple mcrA copies from one assembly, represented by suffixes such as `_1` or `_2`.

`scripts/04_map_gtdb_taxonomy.py` therefore:

1. extracts the assembly accession from each mcrA reference ID;
2. builds aliases from GTDB taxonomy and metadata;
3. attempts exact alias matching first;
4. uses a version-relaxed fallback only if exact matching fails;
5. records the mapping method;
6. leaves unmatched references documented rather than silently discarding the evidence.

Observed mapping:

```text
exact:            1315
version-relaxed:     1
not in GTDB:       256
```

## In-silico MLf/MLr extraction

The reverse-complement of the biological reverse primer is:

```text
AACTAYCCWAACTAYGCAATGAA
```

The completed analysis used cutadapt linked-adapter matching with 15% error tolerance:

```bash
cutadapt \
  -g "GGTGGTGTMGGATTCACACARTAYGCWACAGC...AACTAYCCWAACTAYGCAATGAA" \
  -e 0.15 \
  --discard-untrimmed \
  --minimum-length 350 \
  --maximum-length 500 \
  -o mcrA_genome_GTDB_R232_MLf_MLr.fasta \
  mcrA_genome_GTDB_R232_full.fasta
```

Result:

```text
1021 / 1316 GTDB-mapped mcrA references retained
```

The 77.6% retention is plausible because primer mismatch varies across mcrA diversity. References that cannot be recognized by the primer pair are less relevant to the actual amplicon dataset.
