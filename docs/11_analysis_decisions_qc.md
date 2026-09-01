# Analysis decisions and current QC snapshot

This document records decisions from the completed analysis so a future student can distinguish deliberate choices from accidental defaults.

## Data processing decisions

| Decision | Choice | Reason |
|---|---|---|
| Raw mcrA data type | paired-end reads | Files contained R1/R2 pairs; not PacBio CCS |
| Primer trimming | biological MLf/MLr only | Robust to upstream sequencing tails |
| DADA2 runs | Sep/Jan and Apr/Jul separately | Separate sequencing-run error models |
| DADA2 truncation | none (`0/0`) | Quality/merging were acceptable |
| DADA2 pooling | pseudo | Improve inference of lower-abundance variants |
| Chimera handling | consensus | Standard robust DADA2 approach |
| Merge point | after DADA2 | Preserve run-specific error modelling |
| Blanks/NTCs | retained through classification | Needed to assess contamination |
| Sample ecology cutoff | 1,000 reads | Remove five clearly undersequenced biological libraries |
| Environmental DB identity floor | 80% | Broad mcrA target check |
| GTDB identity floor | 80% | Same broad comparison framework |
| VSEARCH max accepts | 10 | Performance/consensus tradeoff |
| Automatic 90/95% ASV filter | no | Would discard divergent genuine mcrA lineages |
| Phylogeny set | <90% GTDB identity and >=1,000 reads | Focus tree on abundant uncertain ASVs |
| Tree model | GTR+F+G4 | Avoid slow ModelFinder; sufficient for local placement |

## Merged dataset

```text
160 libraries total
150 biological libraries
10 controls
14,260 ASVs
15,837,298 reads in biological libraries
685 reads in controls
```

## Control QC

```text
5/10 controls had zero reads
15 ASVs occurred in any control
5 ASVs were control-exclusive
482 reads belonged to those control-exclusive ASVs
```

## Low-depth biological samples excluded from ecology

```text
Sep24-EA3-TD    12
Jul25-EA3-1     89
Jan25-EA3-3    208
Sep24-EA3-5    804
Jul25-EA4-6    859
```

After this filter: 145 biological samples.

## GTDB mapping and classification

```text
1572 original genome-derived mcrA references
1316 mapped to GTDB R232 taxonomy
1021 retained after MLf/MLr in-silico extraction
```

Master annotation GTDB best-hit bins:

```text
>=95%   4616 ASVs   5,090,006 reads
90-95%  5456 ASVs   8,437,163 reads
80-90%  4188 ASVs   2,310,129 reads
```

## Targeted phylogeny

```text
287 candidate ASVs
1021 GTDB references
383 environmental references
1691 sequences
417 alignment columns in final trimmed alignment
GTR+F+G4
1000 UFBoot
1000 SH-aLRT
```

## Current ANME-related result

In the 287 targeted ASVs:

```text
ANME-2d / Methanoperedenaceae-related  107 ASVs  613,317 reads
ANME-3 / Methanovorans-related           3 ASVs   11,083 reads
ANME-2a-related / Methanocomedens        1 ASV     4,763 reads
```

The ANME-2d local clade had strong support (99.8 SH-aLRT / 97 UFBoot).

## Metadata decision

Use the corrected metadata workbook, not the earlier July version in which the name column was misaligned with `SampleID` and associated metadata.
