# Contributing and version-control habits

This is a research analysis repository. Reproducibility is more important than clever code.

## For the student

1. Create a branch for a real analysis change.
2. Change scripts/configuration, not generated output by hand.
3. Run the relevant QC check before committing.
4. Write commit messages that explain the scientific change, e.g. `Refine ANME-2d ecology labels`, not `updates`.
5. Do not commit raw data, private metadata, large databases, or local absolute-path configuration.
6. Keep small summary tables in `results/` only when they can be regenerated and do not expose unpublished sample-level metadata.

## Suggested branch names

```text
metadata-validation
community-composition
anme-depth-profiles
multivariate-statistics
figures
```

## Before merging a change

- scripts pass syntax/tests;
- sample counts are unchanged unless the change intentionally alters filtering;
- taxonomic changes are documented;
- output differences are understood;
- the relevant documentation is updated.
