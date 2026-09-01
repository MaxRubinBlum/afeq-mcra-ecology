# Project and data structure

## Original project location used for this analysis

The workstation project directory was:

```text
/media/bioinf/Data12/Maxim/16S/2026/2026_Keren_Julia
```

Do not hard-code this path into reusable scripts. Put workstation-specific paths in `config/config.sh`.

## Raw mcrA sequencing batches

Two paired-end sequencing batches were analysed:

```text
Julia-Sep-Jan-mcrA/
Julia-April-July-mcrA/
```

Although the broader project also contains PacBio/Kinnex 16S data, the mcrA libraries analysed here are paired-end Illumina-style FASTQ files. Therefore the mcrA workflow uses `dada2 denoise-paired`, not PacBio CCS denoising.

## Canonical sample IDs

Biological sample IDs use:

```text
<Month>-<SiteSample>
```

Examples:

```text
Sep24-EA1-1
Jan25-EA3-4
Apr25-P1-3
Jul25-EA2-8
```

Controls use explicit run-specific names:

```text
SepJan-blank1a
AprJul-Blank1
AprJul-NTC1
```

This prevents a control from being mistaken for a biological sample.

## Sampling periods represented in the corrected 16S/metadata workbook

The corrected biological metadata contains 107 16S rows across four sampling periods:

```text
September 2024: 24
January 2025:   28
April 2025:     28
July 2025:      27
```

The mcrA sequencing dataset is not identical to the 16S sampling set. It contains additional P samples and does not contain every April EA sample. Never assume that absence from mcrA means a metadata error.

## Important metadata history

An earlier July workbook had a column-alignment problem: the first/name column had apparently been sorted independently of `SampleID` and the associated metadata. The corrected workbook was validated against the sample ID/site/month structure and the July sequencing filenames.

**Lesson:** never trust spreadsheet row alignment just because the workbook opens cleanly. Validate sample identifiers programmatically.
