# Student guide: how to use this project

## First: what is mcrA?

`mcrA` encodes the alpha subunit of methyl-coenzyme M reductase, a key enzyme associated with methane metabolism in methanogenic and anaerobic methane-oxidizing archaea. In this project, mcrA amplicon sequencing is used as a targeted marker for methane-cycling archaeal communities.

An **ASV** (amplicon sequence variant) is an exact biological sequence inferred after denoising. DADA2 estimates ASVs by modelling sequencing errors rather than clustering reads at a fixed similarity threshold.

## What you are expected to understand before running anything

You do not need to be a bioinformatician, but you should be able to answer these questions:

1. Which sample does each FASTQ file represent?
2. Which files are biological samples and which are blanks/NTCs?
3. Which sequencing batch produced each sample?
4. Which primers were used?
5. What output should a successful step produce?
6. What QC result would make you stop rather than continue?

If any of these are unclear, resolve them **before** starting a long analysis.

## Recommended working habits

- Never modify raw FASTQ files.
- Never rename raw files without recording the original name.
- Keep biological sample IDs short and stable, e.g. `Jan25-EA1-4`.
- Do not use sequencing numeric IDs as biological sample IDs.
- Save commands in scripts rather than relying on shell history.
- Run each major step only after checking the previous step.
- Treat blanks as information, not as nuisance samples to delete immediately.
- Keep the original taxonomy and the evidence supporting it (identity, reference, tree placement).

## Workflow in plain language

### Step 1 — identify samples

The two mcrA sequencing deliveries use different filename formats. `scripts/01_make_manifests.py` converts them into canonical sample IDs and QIIME manifests.

### Step 2 — remove primers

We use QIIME cutadapt to find MLf in the forward read and MLr in the reverse read. Reads lacking the expected biological primer are discarded.

### Step 3 — denoise each sequencing run independently

The September/January batch and April/July batch were generated in separate sequencing runs. DADA2 learns an error model from each run, so the batches are denoised separately and merged only after ASV inference.

### Step 4 — examine controls

Blanks and NTCs stay in the analysis through DADA2. In this dataset, contamination was extremely low. A shared ASV should not be removed simply because a few reads occurred in a blank; a highly abundant environmental ASV can appear in a blank through low-level carryover/index leakage.

### Step 5 — classify with two complementary databases

The broad environmental mcrA database has excellent environmental coverage but often poor labels such as `uncultured archaeon`.

The GTDB genome-derived reference set gives much cleaner taxonomy but represents fewer environmental lineages.

We therefore keep both sources of evidence.

### Step 6 — use phylogeny where nearest-hit classification is weak

For abundant ASVs with low GTDB identity, a nearest genome name can be misleading. A targeted mcrA tree places those ASVs relative to GTDB and environmental references. This was especially important for ANME-related lineages.

### Step 7 — only then perform ecology

Once taxonomy has been reconciled, generate sample × lineage abundance tables and integrate them with site, depth, season, methane, sulfate, sulfide, and other metadata.

## Where to stop and ask for help

Stop if:

- many sample IDs do not match the metadata;
- primer trimming removes most reads unexpectedly;
- DADA2 retention collapses in an entire sequencing batch;
- control libraries contain substantial numbers of reads relative to samples;
- ASV lengths do not resemble the expected mcrA amplicon;
- taxonomy is being interpreted more specifically than the sequence identity/tree supports;
- a statistical result depends strongly on a few low-depth libraries.
