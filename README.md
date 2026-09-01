# Afeq mcrA amplicon ecology

Reproducible workflow for the Afeq wetland **mcrA** amplicon project.

This repository documents the analysis from raw paired-end FASTQ files to ASVs, taxonomy, targeted phylogenetic refinement, and ecology-ready tables. It is written for a student who is comfortable with basic biology but may be new to command-line bioinformatics.

> **Important:** raw FASTQ files, unpublished sample metadata, QIIME artifacts, and large reference databases are intentionally not stored in GitHub. The repository contains the workflow, small summary tables, templates, and reproducible scripts.

## What this workflow does

1. Read the two sequencing batches and construct QIIME 2 manifests.
2. Remove the biological MLf/MLr primers.
3. Infer ASVs with DADA2 **separately for each sequencing batch**.
4. Merge the independently denoised batches.
5. Assess blanks and NTCs without blindly deleting shared biological ASVs.
6. Classify ASVs against a broad environmental mcrA database.
7. Build a GTDB R232 genome-derived mcrA amplicon reference set.
8. Classify the ASVs against the GTDB reference set.
9. Combine abundance, controls, sequence identity, and both taxonomic systems.
10. Select abundant/divergent ASVs for targeted phylogenetic placement.
11. Refine important lineages, including ANME-related mcrA clades.
12. Produce ecology-ready lineage tables for site, depth, season, and geochemical analysis.

## Start here

If you are new to bioinformatics, read these in order:

1. [Student guide](docs/00_student_guide.md)
2. [Project and data structure](docs/01_project_and_data.md)
3. [Environment setup](docs/02_environment_setup.md)
4. [Sample naming and metadata](docs/03_sample_naming_metadata.md)
5. [QIIME processing and DADA2](docs/04_qiime_dada2.md)
6. [Taxonomy strategy](docs/05_taxonomy.md)
7. [GTDB R232 reference construction](docs/06_gtdb_reference.md)
8. [Controls and master annotation](docs/07_controls_master_annotation.md)
9. [Phylogenetic refinement](docs/08_phylogeny.md)
10. [Ecology-ready tables](docs/09_ecology.md)
11. [Troubleshooting](docs/10_troubleshooting.md)
12. [Analysis decisions and current QC](docs/11_analysis_decisions_qc.md)
13. [Copy-paste run recipe](docs/12_run_recipe.md)
14. [GitHub workflow](docs/13_github_workflow.md)

## Main software

The completed analysis used:

- QIIME 2 amplicon **2026.1**
- q2-cutadapt
- q2-dada2
- q2-feature-table
- q2-feature-classifier
- cutadapt
- MAFFT
- IQ-TREE 2
- Python 3

The QIIME environment used on the workstation was named:

```text
qiime2-amplicon-2026.1
```

## Primers

Biological mcrA primers:

```text
MLf  GGTGGTGTMGGATTCACACARTAYGCWACAGC
MLr  TTCATTGCRTAGTTWGGRTAGTT
```

The library oligos also contained upstream sequencing tails. We trim the **biological primers**, not hard-coded complete sequencing oligos. See [docs/04_qiime_dada2.md](docs/04_qiime_dada2.md).

## Repository layout

```text
afeq-mcra-ecology/
├── README.md
├── config/
│   └── config.example.sh
├── docs/
├── metadata/
│   └── metadata_template.tsv
├── results/
│   ├── current_findings.md
│   ├── qc_summary.tsv
│   └── README.md
├── scripts/
├── tests/
└── .gitignore
```

## Reproducibility principle

Do not edit analysis outputs manually. If a rule changes, change the script/configuration and regenerate the output. Keep the original QIIME artifacts because QIIME provenance records the commands and environment used to create them.

## Data policy

This project is unpublished. Keep the GitHub repository **private** unless the PI explicitly decides to make the analysis public. Do not commit:

- raw FASTQ files;
- personally identifying sample information;
- unpublished full metadata workbooks;
- `.qza`/`.qzv` files unless there is a deliberate reason;
- large GTDB or mcrA reference FASTA files;
- generated alignments and large trees.

The `.gitignore` supplied here prevents most accidental additions.

## Project management

- [Current project status](PROJECT_STATUS.md)
- [Contributing/version-control habits](CONTRIBUTING.md)
