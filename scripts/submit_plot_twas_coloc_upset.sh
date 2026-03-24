#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   1. 先修改或复制 config/twas_config.example.sh
#   2. export TWAS_CONFIG=/path/to/your_config.sh
#   3. bash scripts/submit_plot_twas_coloc_upset.sh
#
# 这个脚本会优先尝试用 jsub 提交到计算节点；
# 如果当前环境没有 jsub，则直接在当前节点运行。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -z "${TWAS_CONFIG:-}" ]]; then
  echo "ERROR: Please export TWAS_CONFIG=/path/to/twas_config.sh first." >&2
  exit 1
fi

source "${TWAS_CONFIG}"

: "${SPREDIXCAN_RESULTS_DIR:?Need SPREDIXCAN_RESULTS_DIR in config}"
: "${SMULTIXCAN_RESULTS_DIR:?Need SMULTIXCAN_RESULTS_DIR in config}"
: "${GWAS_OVERLAP_TABLES:?Need GWAS_OVERLAP_TABLES in config}"
: "${COLOC_RESULT_TABLES:?Need COLOC_RESULT_TABLES in config}"
: "${UPSET_OUTPUT_DIR:?Need UPSET_OUTPUT_DIR in config}"

mkdir -p "${UPSET_OUTPUT_DIR}/logs"

cmd=(
  python "${REPO_ROOT}/scripts/plot_twas_coloc_upset.py"
  --spredixcan-root "${SPREDIXCAN_RESULTS_DIR}"
  --smultixcan-root "${SMULTIXCAN_RESULTS_DIR}"
  --output-dir "${UPSET_OUTPUT_DIR}"
)

for path in ${GWAS_OVERLAP_TABLES}; do
  cmd+=(--overlap-tsv "${path}")
done

for path in ${COLOC_RESULT_TABLES}; do
  cmd+=(--coloc-tsv "${path}")
done

if [[ -n "${COLOC_PPH4_CUTOFF:-}" ]]; then
  cmd+=(--pph4-cutoff "${COLOC_PPH4_CUTOFF}")
fi

echo "Running command:"
printf ' %q' "${cmd[@]}"
echo

if command -v jsub >/dev/null 2>&1; then
  mem="${UPSET_JOB_MEM_MB:-24000}"
  queue="${UPSET_JOB_QUEUE:-normal}"
  /bin/bash -lc "jsub -q ${queue} -n 1 -M ${mem} -o ${UPSET_OUTPUT_DIR}/logs/plot_twas_upset.%J.log ${cmd[*]}"
else
  echo "jsub not found; running locally."
  "${cmd[@]}" 2>&1 | tee "${UPSET_OUTPUT_DIR}/logs/plot_twas_upset.local.log"
fi
