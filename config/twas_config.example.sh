#!/usr/bin/env bash

# 示例配置文件。
# 这里使用的是项目中的完整绝对路径示例；
# 公开使用时，请按自己的服务器目录替换。

export TWAS_ROOT="/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas"
export GWAS_INPUT_TABLE="/storage/public/home/2020060185/GWAS/gwas_input_sources.tsv"
export SPREDIXCAN_RESULTS_DIR="${TWAS_ROOT}/02.SPrediXcan/results_full_inputs_v2"
export SMULTIXCAN_RESULTS_DIR="${TWAS_ROOT}/03.SMulTiXcan/results_full_inputs_v2"
export SMULTIXCAN_RELATED_RESULTS_DIR="${TWAS_ROOT}/03.SMulTiXcan/results_related_v2"
export MODEL_DBS_DIR="/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas/02.makeTrainingData/02.output_db"
export SMULTIXCAN_COV_DIR="/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas/03.SMulTiXcan/covariance_full_inputs_v2"
export SMULTIXCAN_SCRIPT="/storage/public/home/2020060185/anaconda3/envs/MetaXcan/share/MetaXcan/software/SMulTiXcan.py"
export METAXCAN_PYTHON="python"

# Example regex matching a subset of biologically related tissues.
export TISSUE_REGEX="Abomasum|Adipose|Brain|Cerebellum|Cervix|Corpus-uteri|Oviduct|Ovary"

# Comma-separated QTL types used in the project.
export QTL_TYPES="eQTL,eeQTL,sQTL,isoQTL,3aQTL,enQTL,stQTL"

# GWAS loci vs TWAS vs COLOC UpSet 作图输入。
# submit_plot_twas_coloc_upset.sh 支持空格分隔的多个完整路径。
export GWAS_OVERLAP_TABLES="/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs.tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs_xinjiang.tsv"
export COLOC_RESULT_TABLES="/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_new/GWAS.all.addcol.sig.pph4.new /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_xinjiang/GWAS.all.addcol.sig.pph4"
export COLOC_PPH4_CUTOFF="0.8"
export UPSET_OUTPUT_DIR="/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/plot/upset_final"
export UPSET_JOB_QUEUE="normal"
export UPSET_JOB_MEM_MB="24000"
