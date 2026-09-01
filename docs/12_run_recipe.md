# Copy-paste run recipe

This page gives the **order of operations**. Read the corresponding documentation before running a step. Do not run the whole project blindly from top to bottom on the first attempt.

## 0. Configure paths

```bash
cd /path/to/afeq-mcra-ecology
cp config/config.example.sh config/config.sh
nano config/config.sh
source config/config.sh
conda activate qiime2-amplicon-2026.1
```

## 1. Build manifests and process the two sequencing runs

```bash
bash scripts/02_process_qiime.sh
```

**Stop and inspect:**

```text
SepJan/demux-raw.qzv
SepJan/demux-trimmed.qzv
SepJan/dada2-stats.qzv
AprJul/demux-raw.qzv
AprJul/demux-trimmed.qzv
AprJul/dada2-stats.qzv
merged/table.qzv
merged/rep-seqs.qzv
```

Expected broad outcome from the completed run: ~74% non-chimeric retention for Sep/Jan and ~86% for Apr/Jul.

## 2. Environmental mcrA classification

```bash
bash scripts/03_classify_environmental.sh
```

Outputs:

```text
$MCRA_OUT/merged/taxonomy.qza
$MCRA_OUT/merged/vsearch-hits.qza
```

## 3. Build the GTDB R232 mcrA amplicon reference

Download/place locally:

```text
$GTDB_WORK/ar53_taxonomy_r232.tsv.gz
$GTDB_WORK/ar53_metadata_r232.tsv.gz
```

Then map the genome-derived mcrA references:

```bash
python scripts/04_map_gtdb_taxonomy.py \
  --mcra-fasta "$GENOME_DB_QIIME/mcrA_ncbi_genome_db_seqs.fasta" \
  --gtdb-taxonomy "$GTDB_WORK/ar53_taxonomy_r232.tsv.gz" \
  --gtdb-metadata "$GTDB_WORK/ar53_metadata_r232.tsv.gz" \
  --out-prefix "$GTDB_WORK/mcrA_genome_GTDB_R232"
```

Expected from the completed run:

```text
1572 genome-derived mcrA references
1316 GTDB-mapped
256 unmatched
```

Extract the MLf/MLr region:

```bash
bash scripts/05_trim_gtdb_amplicon.sh
```

Expected:

```text
1021 sequences
409-439 bp
median 415 bp
```

If these numbers are radically different, stop and troubleshoot.

## 4. GTDB classification

```bash
bash scripts/06_classify_gtdb.sh
```

## 5. Export merged ASV table and sequences

```bash
mkdir -p "$MCRA_OUT/merged/export-table" "$MCRA_OUT/merged/export-seqs"
qiime tools export --input-path "$MCRA_OUT/merged/table.qza" --output-path "$MCRA_OUT/merged/export-table"
qiime tools export --input-path "$MCRA_OUT/merged/rep-seqs.qza" --output-path "$MCRA_OUT/merged/export-seqs"

biom convert \
  -i "$MCRA_OUT/merged/export-table/feature-table.biom" \
  -o "$MCRA_OUT/merged/export-table/feature-table.tsv" \
  --to-tsv
```

## 6. Control QC

```bash
python scripts/08_control_qc.py \
  "$MCRA_OUT/merged/export-table/feature-table.tsv" \
  --min-sample-reads 1000 \
  --control-exclusive-out "$MCRA_OUT/merged/control_exclusive_asvs.txt" \
  --low-samples-out "$MCRA_OUT/merged/low_depth_samples.tsv"
```

Expected completed-run values:

```text
150 biological samples
10 controls
15,837,298 biological reads
685 control reads
15 ASVs detected in controls
5 control-exclusive ASVs
5 biological samples below 1,000 reads
```

## 7. Build the master ASV annotation

```bash
python scripts/07_build_master_annotation.py \
  --feature-table "$MCRA_OUT/merged/export-table/feature-table.tsv" \
  --env-taxonomy "$MCRA_OUT/merged/export-taxonomy-env/taxonomy.tsv" \
  --env-hits "$MCRA_OUT/merged/export-hits/blast6.tsv" \
  --env-ref-taxonomy "$ENV_DB_QIIME/mcrA_ncbi_nt_cur_db_taxonomy.tsv" \
  --gtdb-taxonomy "$MCRA_OUT/merged/export-taxonomy-GTDB/taxonomy.tsv" \
  --gtdb-hits "$MCRA_OUT/merged/export-hits-GTDB/blast6.tsv" \
  --gtdb-ref-taxonomy "$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr_taxonomy.tsv" \
  --output "$MCRA_OUT/merged/mcrA_ASV_master_annotation.tsv"
```

Expected:

```text
14,260 ASVs
```

## 8. Prepare targeted phylogeny

The environmental reference FASTA is:

```text
$ENV_DB_QIIME/mcrA_ncbi_nt_cur_db_seqs.fasta
```

Run:

```bash
PHYLO="$MCRA_OUT/merged/phylogeny"
mkdir -p "$PHYLO"

python scripts/09_prepare_phylogeny.py \
  --master "$MCRA_OUT/merged/mcrA_ASV_master_annotation.tsv" \
  --asv-fasta "$MCRA_OUT/merged/export-seqs/dna-sequences.fasta" \
  --gtdb-fasta "$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr.fasta" \
  --gtdb-taxonomy "$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr_taxonomy.tsv" \
  --env-fasta "$ENV_DB_QIIME/mcrA_ncbi_nt_cur_db_seqs.fasta" \
  --env-taxonomy "$ENV_DB_QIIME/mcrA_ncbi_nt_cur_db_taxonomy.tsv" \
  --env-hits "$MCRA_OUT/merged/export-hits/blast6.tsv" \
  --outdir "$PHYLO"
```

Expected completed-run tree input:

```text
287 candidate ASVs
1021 GTDB references
383 environmental references
1691 total sequences
```

## 9. Align and infer tree

```bash
bash scripts/10_align_trim_tree.sh "$PHYLO"
```

Expected core alignment is approximately 417 bp.

## 10. Assign the principal phylogenetic clades

Run this in a Python environment containing Biopython:

```bash
conda activate mcra-ecology
python scripts/11_assign_phylogenetic_clades.py \
  --treefile "$PHYLO/mcrA_GTR.treefile" \
  --tree-metadata "$PHYLO/tree_metadata.tsv" \
  --master "$MCRA_OUT/merged/mcrA_ASV_master_annotation.tsv" \
  --output "$MCRA_OUT/merged/mcrA_phylogenetic_assignments.tsv"
```

For manuscript-level interpretation, inspect the local branches in a tree viewer as well. The script is deliberately conservative and the 417-bp tree should not be treated as a deep archaeal species tree.

## 11. Build ecology labels

```bash
python scripts/12_build_ecology_labels.py \
  --master "$MCRA_OUT/merged/mcrA_ASV_master_annotation.tsv" \
  --phylogeny "$MCRA_OUT/merged/mcrA_phylogenetic_assignments.tsv" \
  --output "$MCRA_OUT/merged/mcrA_ecology_labels.tsv"
```

At this point, join the labels to the ASV count table, remove controls/control-exclusive ASVs/low-depth biological libraries, and proceed to ecological statistics.
