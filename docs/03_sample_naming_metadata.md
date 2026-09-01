# Sample naming and metadata validation

## Why sample naming matters

Most downstream failures in amplicon projects are not sophisticated bioinformatics failures; they are sample identity failures. A perfect ASV table linked to the wrong sample metadata is worse than no analysis.

## Canonical mcrA IDs

Canonical IDs are derived from the biological information encoded in the FASTQ filenames, not from transient numeric sequencing IDs.

Examples:

```text
Sep24-EA1-7
Jan25-EA4-2
Apr25-P3-5
Jul25-EA1-4
```

The numeric IDs supplied by the sequencing facility remain in the provenance/sample map but are not part of the biological sample ID.

## Corrected July mapping

Examples confirmed after the metadata correction include:

```text
637 -> EA1-3
639 -> EA1-5
641 -> EA1-7
643 -> EA1-9
655 -> EA1-2
658 -> EA1-4
659 -> EA1-6
661 -> EA1-8
664 -> EA2-1
```

## Validation checklist

Before ecological analysis, confirm:

- no duplicate canonical sample IDs;
- no duplicate biological `SampleID` values;
- month in the canonical ID agrees with the metadata date/month;
- EA/P site code agrees between sample name and metadata;
- mcrA samples not present in the 16S metadata are recognized as intentional rather than silently dropped;
- controls do not join to biological metadata.

Use `scripts/00_validate_metadata.py` as a structural check. Because project workbooks can change column names, inspect the workbook once and adapt the column arguments explicitly rather than guessing.
