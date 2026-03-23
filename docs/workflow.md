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
bash scripts/run_smultixcan_related.sh <trait> config/twas_config.sh
```

Store outputs under:

```text
03.SMulTiXcan/results_related_v2/<trait>/<qtl>.<trait>.SMultixcan.related.txt
```

## 4. Result Summaries

- `summarize_twas_results.py`
- `summarize_twas_single_full.py`
- `summarize_twas_significance.py`
- `twas_fair_compare.py`

These scripts generate manuscript-facing summary tables and comparison sheets.

