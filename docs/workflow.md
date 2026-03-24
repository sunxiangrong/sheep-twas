# Workflow

## 1. Single-tissue TWAS

Run `SPrediXcan` for every `trait × qtl × tissue` combination. Store outputs under:

```text
02.SPrediXcan/results_full_inputs_v2/<trait>/<qtl>.<trait>.<tissue>.csv
```

## 2. All-tissue multi-tissue TWAS

Run `SMulTiXcan` using all available tissues per `trait × qtl`. Store outputs under:

```text
03.SMulTiXcan/results_full_inputs_v2/<trait>/<qtl>.<trait>.SMultixcan.txt
```

## 3. Related-tissue multi-tissue TWAS

Filter single-tissue `SPrediXcan` results to biologically matched tissues, then rerun `SMulTiXcan`.

Use:

```bash
bash scripts/run/run_smultixcan_related.sh <trait> config/twas_config.sh
```

Store outputs under:

```text
03.SMulTiXcan/results_related_v2/<trait>/<qtl>.<trait>.SMultixcan.related.txt
```

## 4. Result Summaries

- `scripts/summary/summarize_twas_results.py`
- `scripts/summary/summarize_twas_single_full.py`
- `scripts/summary/summarize_twas_significance.py`
- `scripts/summary/twas_fair_compare.py`

These scripts generate manuscript-facing summary tables and comparison sheets.

## 5. GWAS-vs-TWAS-vs-COLOC UpSet Plots

Use the final `SPrediXcan`, final all-tissue `SMulTiXcan`, GWAS-QTL overlap tables, and coloc summary tables to build locus-level support tags.

Core script:

```bash
python scripts/plot/plot_twas_coloc_upset.py \
  --spredixcan-root /path/to/twas/02.SPrediXcan/results_full_inputs_v2 \
  --smultixcan-root /path/to/twas/03.SMulTiXcan/results_full_inputs_v2 \
  --overlap-tsv /path/to/gwas_qtl_pairs.tsv /path/to/gwas_qtl_pairs_xinjiang.tsv \
  --coloc-tsv /path/to/coloc_beijing.tsv /path/to/coloc_xinjiang.tsv \
  --output-dir results/upset_final
```

Cluster submission wrapper:

```bash
export TWAS_CONFIG=/path/to/twas_config.sh
bash scripts/plot/submit_plot_twas_coloc_upset.sh
```

Outputs include:

- one overall UpSet figure
- one UpSet figure per trait
- one locus-tag table
- one trait-level summary table
