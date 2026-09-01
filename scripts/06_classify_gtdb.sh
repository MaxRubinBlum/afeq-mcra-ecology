#!/usr/bin/env bash
set -euo pipefail
: "${GTDB_WORK:?source config/config.sh first}"
: "${MCRA_OUT:?source config/config.sh first}"
THREADS=${THREADS:-24}
FA="$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr.fasta"
TX="$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr_taxonomy.tsv"

qiime tools import --type 'FeatureData[Sequence]' --input-path "$FA" --output-path "$GTDB_WORK/mcrA-GTDB-R232-seqs.qza"
qiime tools import --type 'FeatureData[Taxonomy]' --input-format HeaderlessTSVTaxonomyFormat \
  --input-path "$TX" --output-path "$GTDB_WORK/mcrA-GTDB-R232-taxonomy.qza"
qiime feature-classifier classify-consensus-vsearch \
  --i-query "$MCRA_OUT/merged/rep-seqs.qza" \
  --i-reference-reads "$GTDB_WORK/mcrA-GTDB-R232-seqs.qza" \
  --i-reference-taxonomy "$GTDB_WORK/mcrA-GTDB-R232-taxonomy.qza" \
  --p-perc-identity 0.80 --p-query-cov 0.80 --p-maxaccepts 10 --p-maxrejects all \
  --p-min-consensus 0.51 --p-threads "$THREADS" \
  --o-classification "$MCRA_OUT/merged/taxonomy-GTDB-R232.qza" \
  --o-search-results "$MCRA_OUT/merged/vsearch-hits-GTDB-R232.qza"
qiime metadata tabulate --m-input-file "$MCRA_OUT/merged/taxonomy-GTDB-R232.qza" \
  --o-visualization "$MCRA_OUT/merged/taxonomy-GTDB-R232.qzv"
mkdir -p "$MCRA_OUT/merged/export-taxonomy-GTDB" "$MCRA_OUT/merged/export-hits-GTDB"
qiime tools export --input-path "$MCRA_OUT/merged/taxonomy-GTDB-R232.qza" --output-path "$MCRA_OUT/merged/export-taxonomy-GTDB"
qiime tools export --input-path "$MCRA_OUT/merged/vsearch-hits-GTDB-R232.qza" --output-path "$MCRA_OUT/merged/export-hits-GTDB"
