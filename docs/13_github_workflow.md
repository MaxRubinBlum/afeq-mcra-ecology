# GitHub workflow for this project

## Repository visibility

Keep the repository **private** during active unpublished analysis. A public release can be made later after data/publication decisions are explicit.

## What belongs in GitHub

Good to commit:

- scripts;
- documentation;
- configuration templates;
- small aggregate QC summaries;
- manuscript-independent plotting/statistics code;
- tests.

Do not commit by default:

- raw FASTQ files;
- full unpublished metadata workbooks;
- full ASV feature tables with sample-level unpublished data;
- GTDB/reference databases;
- QIIME artifacts/visualizations;
- large alignments/trees.

## Simple student workflow

```bash
git pull
git checkout -b descriptive-ecology
# edit scripts/docs
git status
git diff
python tests/test_manifest_parser.py
git add scripts docs results
git commit -m "Add descriptive mcrA ecology workflow"
git push -u origin descriptive-ecology
```

Then open a pull request. Even in a small lab project, pull requests create a useful record of why an analysis changed.

## Reproducible changes

If a filtering threshold changes, update:

1. the script/config value;
2. the QC documentation;
3. any result summary affected by the change.

Do not overwrite a result manually and leave the generating code unchanged.
