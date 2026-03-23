#!/usr/bin/env bash

# Example configuration for related-tissue SMulTiXcan reruns.

export TWAS_ROOT="/path/to/twas"
export GWAS_INPUT_TABLE="/path/to/gwas_input_sources.tsv"
export SPREDIXCAN_RESULTS_DIR="${TWAS_ROOT}/02.SPrediXcan/results_full_inputs_v2"
export SMULTIXCAN_RESULTS_DIR="${TWAS_ROOT}/03.SMulTiXcan/results_full_inputs_v2"
export MODEL_DBS_DIR="/path/to/model_dbs"
export SMULTIXCAN_COV_DIR="/path/to/smultixcan_covariance"
export SMULTIXCAN_SCRIPT="/path/to/SMulTiXcan.py"
export METAXCAN_PYTHON="python"

# Example regex matching a subset of biologically related tissues.
export TISSUE_REGEX="Abomasum|Adipose|Brain|Cerebellum|Cervix|Corpus-uteri|Oviduct|Ovary"

# Comma-separated QTL types used in the project.
export QTL_TYPES="eQTL,eeQTL,sQTL,isoQTL,3aQTL,enQTL,stQTL"

