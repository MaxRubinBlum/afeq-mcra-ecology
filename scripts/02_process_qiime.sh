#!/usr/bin/env bash
set -euo pipefail

: "${RUN_SEPJAN:?source config/config.sh first}"
: "${RUN_APRJUL:?source config/config.sh first}"
: "${MCRA_OUT:?source config/config.sh first}"
THREADS=${THREADS:-24}

MLF='GGTGGTGTMGGATTCACACARTAYGCWACAGC'
MLR='TTCATTGCRTAGTTWGGRTAGTT'

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$MCRA_OUT"/{manifests,SepJan,AprJul,merged,export}
qiime info | tee "$MCRA_OUT/qiime-info.txt"

python "$SCRIPT_DIR/01_make_manifests.py" \
  --sepjan "$RUN_SEPJAN" --aprjul "$RUN_APRJUL" --outdir "$MCRA_OUT/manifests"

run_one () {
  local label="$1"; local manifest="$2"; local d="$MCRA_OUT/$label"

  qiime tools import \
    --type 'SampleData[PairedEndSequencesWithQuality]' \
    --input-path "$manifest" \
    --input-format PairedEndFastqManifestPhred33V2 \
    --output-path "$d/demux-raw.qza"

  qiime demux summarize --i-data "$d/demux-raw.qza" --o-visualization "$d/demux-raw.qzv"

  qiime cutadapt trim-paired \
    --i-demultiplexed-sequences "$d/demux-raw.qza" \
    --p-front-f "$MLF" --p-front-r "$MLR" \
    --p-error-rate 0.10 --p-overlap 15 --p-discard-untrimmed --p-cores "$THREADS" \
    --o-trimmed-sequences "$d/demux-trimmed.qza" --o-stats "$d/cutadapt-stats.qza"

  qiime demux summarize --i-data "$d/demux-trimmed.qza" --o-visualization "$d/demux-trimmed.qzv"
  qiime metadata tabulate --m-input-file "$d/cutadapt-stats.qza" --o-visualization "$d/cutadapt-stats.qzv"

  qiime dada2 denoise-paired \
    --i-demultiplexed-seqs "$d/demux-trimmed.qza" \
    --p-trim-left-f 0 --p-trim-left-r 0 --p-trunc-len-f 0 --p-trunc-len-r 0 \
    --p-max-ee-f 2 --p-max-ee-r 2 --p-min-overlap 12 \
    --p-pooling-method pseudo --p-chimera-method consensus --p-n-threads "$THREADS" \
    --o-table "$d/table.qza" --o-representative-sequences "$d/rep-seqs.qza" \
    --o-denoising-stats "$d/dada2-stats.qza" --o-base-transition-stats "$d/base-transition-stats.qza"

  qiime metadata tabulate --m-input-file "$d/dada2-stats.qza" --o-visualization "$d/dada2-stats.qzv"
  qiime feature-table summarize --i-table "$d/table.qza" --o-summary "$d/table.qzv" \
    --o-feature-frequencies "$d/feature-frequencies.qza" --o-sample-frequencies "$d/sample-frequencies.qza"
  qiime feature-table tabulate-seqs --i-data "$d/rep-seqs.qza" --o-visualization "$d/rep-seqs.qzv"
}

run_one SepJan "$MCRA_OUT/manifests/manifest_SepJan.tsv"
run_one AprJul "$MCRA_OUT/manifests/manifest_AprJul.tsv"

qiime feature-table merge --i-tables "$MCRA_OUT/SepJan/table.qza" "$MCRA_OUT/AprJul/table.qza" \
  --o-merged-table "$MCRA_OUT/merged/table.qza"
qiime feature-table merge-seqs --i-data "$MCRA_OUT/SepJan/rep-seqs.qza" "$MCRA_OUT/AprJul/rep-seqs.qza" \
  --o-merged-data "$MCRA_OUT/merged/rep-seqs.qza"
qiime feature-table summarize --i-table "$MCRA_OUT/merged/table.qza" --o-summary "$MCRA_OUT/merged/table.qzv" \
  --o-feature-frequencies "$MCRA_OUT/merged/feature-frequencies.qza" \
  --o-sample-frequencies "$MCRA_OUT/merged/sample-frequencies.qza"
qiime feature-table tabulate-seqs --i-data "$MCRA_OUT/merged/rep-seqs.qza" --o-visualization "$MCRA_OUT/merged/rep-seqs.qzv"

echo 'QIIME processing complete. Inspect QZV files before continuing.'
