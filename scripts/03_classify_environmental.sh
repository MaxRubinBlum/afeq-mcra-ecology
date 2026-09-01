#!/usr/bin/env bash
set -euo pipefail
: "${MCRA_OUT:?source config/config.sh first}"
: "${ENV_DB_QIIME:?source config/config.sh first}"
THREADS=${THREADS:-24}
REFSEQ="$ENV_DB_QIIME/mcrA_ncbi_nt_cur_db_seqs.fasta"
REFTAX="$ENV_DB_QIIME/mcrA_ncbi_nt_cur_db_taxonomy.tsv"
mkdir -p "$MCRA_OUT/db" "$MCRA_OUT/merged/export-taxonomy-env" "$MCRA_OUT/merged/export-hits"

qiime tools import --type 'FeatureData[Sequence]' --input-path "$REFSEQ" --output-path "$MCRA_OUT/db/mcrA-env-seqs.qza"
qiime tools import --type 'FeatureData[Taxonomy]' --input-format HeaderlessTSVTaxonomyFormat \
  --input-path "$REFTAX" --output-path "$MCRA_OUT/db/mcrA-env-taxonomy.qza"

qiime feature-classifier classify-consensus-vsearch \
  --i-query "$MCRA_OUT/merged/rep-seqs.qza" \
  --i-reference-reads "$MCRA_OUT/db/mcrA-env-seqs.qza" \
  --i-reference-taxonomy "$MCRA_OUT/db/mcrA-env-taxonomy.qza" \
  --p-perc-identity 0.80 --p-query-cov 0.80 --p-maxaccepts 10 --p-maxrejects all \
  --p-min-consensus 0.51 --p-threads "$THREADS" \
  --o-classification "$MCRA_OUT/merged/taxonomy.qza" --o-search-results "$MCRA_OUT/merged/vsearch-hits.qza"

qiime metadata tabulate --m-input-file "$MCRA_OUT/merged/taxonomy.qza" --o-visualization "$MCRA_OUT/merged/taxonomy.qzv"
qiime tools export --input-path "$MCRA_OUT/merged/taxonomy.qza" --output-path "$MCRA_OUT/merged/export-taxonomy-env"
qiime tools export --input-path "$MCRA_OUT/merged/vsearch-hits.qza" --output-path "$MCRA_OUT/merged/export-hits"
