#!/usr/bin/env bash
# Copy this file to config/config.sh and edit the paths for your workstation.

export BASE="/media/bioinf/Data12/Maxim/16S/2026/2026_Keren_Julia"
export MCRA_OUT="$BASE/mcrA_analysis"
export MCRA_DB_ROOT="$BASE/update_mcrA_db"
export GTDB_WORK="$MCRA_DB_ROOT/GTDB_R232_mcrA"

export RUN_SEPJAN="$BASE/Julia-Sep-Jan-mcrA"
export RUN_APRJUL="$BASE/Julia-April-July-mcrA"

export ENV_DB_QIIME="$MCRA_DB_ROOT/databases/mcrA_ncbi_nt_cur_db/qiime2"
export GENOME_DB_QIIME="$MCRA_DB_ROOT/databases/mcrA_ncbi_genome_db/qiime2"

export THREADS=24
export MIN_SAMPLE_READS=1000
