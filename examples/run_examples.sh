#!/usr/bin/env bash
set -euo pipefail

TWAS_ROOT="/path/to/twas"
OUT_ROOT="./results"

python scripts/summarize_twas_results.py \
  --twas-root "$TWAS_ROOT" \
  --output-xlsx "$OUT_ROOT/summary/twas_result_summary.xlsx" \
  --output-dir "$OUT_ROOT/summary"

python scripts/summarize_twas_single_full.py \
  --twas-root "$TWAS_ROOT" \
  --output-xlsx "$OUT_ROOT/summary_single_full/twas_single_full_summary.xlsx" \
  --output-dir "$OUT_ROOT/summary_single_full"

python scripts/summarize_twas_significance.py \
  --twas-root "$TWAS_ROOT" \
  --output-xlsx "$OUT_ROOT/significance/twas_significance.xlsx" \
  --output-dir "$OUT_ROOT/significance"

python scripts/twas_fair_compare.py \
  --twas-root "$TWAS_ROOT" \
  --output-xlsx "$OUT_ROOT/fair_compare/twas_fair_compare.xlsx" \
  --output-dir "$OUT_ROOT/fair_compare"

