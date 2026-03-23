#!/usr/bin/env bash
set -euo pipefail

trait="${1:-}"
config_file="${2:-}"

if [[ -z "$trait" || -z "$config_file" ]]; then
  echo "Usage: $0 <trait> <config.sh>" >&2
  exit 1
fi

source "$config_file"

for var in \
  GWAS_INPUT_TABLE \
  SPREDIXCAN_RESULTS_DIR \
  SMULTIXCAN_RESULTS_DIR \
  MODEL_DBS_DIR \
  SMULTIXCAN_COV_DIR \
  SMULTIXCAN_SCRIPT \
  METAXCAN_PYTHON \
  TISSUE_REGEX \
  QTL_TYPES; do
  [[ -n "${!var:-}" ]] || { echo "Missing required config variable: $var" >&2; exit 1; }
done

related_root="${SMULTIXCAN_RESULTS_DIR%results_*}results_related_v2"
mkdir -p "$related_root/$trait" "$related_root/_filtered_metaxcan/$trait"

IFS=',' read -r -a qtl_types <<< "$QTL_TYPES"

gwas_input="$(awk -F '\t' -v t="$trait" '$1==t{print $2; exit}' "$GWAS_INPUT_TABLE")"
[[ -n "$gwas_input" ]] || { echo "GWAS input missing for trait: $trait" >&2; exit 1; }

for qtl_type in "${qtl_types[@]}"; do
  cov="$SMULTIXCAN_COV_DIR/${qtl_type}.smultixcan_covariances.txt.gz"
  [[ -f "$cov" ]] || continue

  filtered_dir="$related_root/_filtered_metaxcan/$trait/$qtl_type"
  mkdir -p "$filtered_dir"
  find "$filtered_dir" -mindepth 1 -maxdepth 1 -exec rm -f {} +

  find "$SPREDIXCAN_RESULTS_DIR/$trait" -maxdepth 1 -type f -name "${qtl_type}.${trait}.*.csv" | while IFS= read -r f; do
    base="$(basename "$f")"
    if [[ "$base" =~ $TISSUE_REGEX ]]; then
      ln -sfn "$f" "$filtered_dir/$base"
    fi
  done

  if [[ -z "$(find -L "$filtered_dir" -maxdepth 1 -type f -print -quit)" ]]; then
    echo "No related tissues matched for $trait / $qtl_type" >&2
    continue
  fi

  "$METAXCAN_PYTHON" "$SMULTIXCAN_SCRIPT" \
    --models_folder "$MODEL_DBS_DIR" \
    --models_name_filter "sheepgtex_(.*)_${qtl_type}_models_filtered_signif.db" \
    --models_name_pattern "sheepgtex_(.*)_${qtl_type}_models_filtered_signif.db" \
    --snp_covariance "$cov" \
    --metaxcan_folder "$filtered_dir/" \
    --metaxcan_filter "${qtl_type}.${trait}.(.*).csv" \
    --metaxcan_file_name_parse_pattern "${qtl_type}.${trait}.(.*).csv" \
    --gwas_file "$gwas_input" \
    --snp_column SNP \
    --effect_allele_column A1 \
    --non_effect_allele_column A2 \
    --beta_column b \
    --pvalue_column p \
    --keep_non_rsid \
    --model_db_snp_key varID \
    --cutoff_condition_number 30 \
    --verbosity 7 \
    --throw \
    --output "$related_root/$trait/${qtl_type}.${trait}.SMultixcan.related.txt"
done
