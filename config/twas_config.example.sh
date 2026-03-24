#!/usr/bin/env bash

# Example configuration for related-tissue SMulTiXcan reruns.

export TWAS_ROOT="/path/to/twas"
export GWAS_INPUT_TABLE="/path/to/gwas_input_sources.tsv"
export SPREDIXCAN_RESULTS_DIR="${TWAS_ROOT}/02.SPrediXcan/results_full_inputs_v2"
export SMULTIXCAN_RESULTS_DIR="${TWAS_ROOT}/03.SMulTiXcan/results_full_inputs_v2"
export SMULTIXCAN_RELATED_RESULTS_DIR="${TWAS_ROOT}/03.SMulTiXcan/results_related_v2"
export MODEL_DBS_DIR="/path/to/model_dbs"
export SMULTIXCAN_COV_DIR="/path/to/smultixcan_covariance"
export SMULTIXCAN_SCRIPT="/path/to/SMulTiXcan.py"
export METAXCAN_PYTHON="python"

# Example regex matching a subset of biologically related tissues.
export TISSUE_REGEX="Abomasum|Adipose|Brain|Cerebellum|Cervix|Corpus-uteri|Oviduct|Ovary"

# Comma-separated QTL types used in the project.
export QTL_TYPES="eQTL,eeQTL,sQTL,isoQTL,3aQTL,enQTL,stQTL"

# Example inputs for GWAS loci vs TWAS vs COLOC UpSet plots.
# Space-separated paths are accepted by submit_plot_twas_coloc_upset.sh
export GWAS_OVERLAP_TABLES="/path/to/gwas_qtl_pairs.tsv /path/to/gwas_qtl_pairs_xinjiang.tsv"
export COLOC_RESULT_TABLES="/path/to/coloc_beijing.tsv /path/to/coloc_xinjiang.tsv"
export COLOC_PPH4_CUTOFF="0.8"
export UPSET_OUTPUT_DIR="/path/to/output/upset_final"
export UPSET_JOB_QUEUE="normal"
export UPSET_JOB_MEM_MB="24000"
