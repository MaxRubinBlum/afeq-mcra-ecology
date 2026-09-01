#!/usr/bin/env bash
set -euo pipefail

# Run the complete post-taxonomy mcrA ecology workflow.
#
# Usage:
#   cp config/config.example.sh config/config.sh
#   edit config/config.sh
#   bash scripts/run_ecology_pipeline.sh [config/config.sh]
#
# The runner creates outputs under $ECOLOGY_OUT. It does not modify raw data,
# QIIME artifacts, taxonomy databases, or the source metadata workbook.

CONFIG=${1:-config/config.sh}
if [[ ! -f "$CONFIG" ]]; then
  echo "Config file not found: $CONFIG" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$CONFIG"

: "${MCRA_FEATURE_TABLE:?Set MCRA_FEATURE_TABLE in config.sh}"
: "${MCRA_MASTER_ANNOTATION:?Set MCRA_MASTER_ANNOTATION in config.sh}"
: "${MCRA_PHYLOGENY_ASSIGNMENTS:?Set MCRA_PHYLOGENY_ASSIGNMENTS in config.sh}"
: "${METADATA_XLSX:?Set METADATA_XLSX in config.sh}"
: "${ECOLOGY_OUT:?Set ECOLOGY_OUT in config.sh}"

MIN_SAMPLE_READS=${MIN_SAMPLE_READS:-1000}
RAREFACTION_DEPTH=${RAREFACTION_DEPTH:-5000}
SHANNON_ITERATIONS=${SHANNON_ITERATIONS:-50}
PERMUTATIONS=${PERMUTATIONS:-999}
RANDOM_SEED=${RANDOM_SEED:-20260901}

mkdir -p "$ECOLOGY_OUT"

python scripts/13_prepare_ecology_tables.py \
  --feature-table "$MCRA_FEATURE_TABLE" \
  --master "$MCRA_MASTER_ANNOTATION" \
  --phylogeny "$MCRA_PHYLOGENY_ASSIGNMENTS" \
  --metadata-xlsx "$METADATA_XLSX" \
  --min-reads "$MIN_SAMPLE_READS" \
  --output-dir "$ECOLOGY_OUT/prepared"

python scripts/14_composition_profiles.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/composition"

python scripts/15_depth_bubble_plot.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/depth_bubble"

python scripts/16_shannon_alpha.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/shannon" \
  --rarefaction-depth "$RAREFACTION_DEPTH" \
  --iterations "$SHANNON_ITERATIONS" \
  --seed "$RANDOM_SEED"

python scripts/17_bray_pcoa_permanova.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/ordination" \
  --permutations "$PERMUTATIONS" \
  --seed "$RANDOM_SEED"

python scripts/18_geochemistry_associations.py \
  --prepared-dir "$ECOLOGY_OUT/prepared" \
  --output-dir "$ECOLOGY_OUT/geochemistry"

echo "Ecology workflow complete: $ECOLOGY_OUT"
