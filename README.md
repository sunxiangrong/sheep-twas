# sheep-twas

Reusable TWAS workflow utilities for livestock post-GWAS analysis.

This repository is designed for two purposes:

1. As a reproducible backup of the TWAS workflow used in our sheep post-GWAS project.
2. As a public code repository accompanying manuscript submission.

The current scaffold covers:

- `SPrediXcan` result summarization
- `SMulTiXcan` all-tissue result summarization
- `SMulTiXcan` related-tissue rerun
- significance counting with per-file `BH-FDR`
- fair comparison across three TWAS result types

## Repository Layout

```text
sheep-twas/
├── config/
│   └── twas_config.example.sh
├── docs/
│   ├── inputs_and_outputs.md
│   └── workflow.md
├── examples/
│   └── run_examples.sh
├── scripts/
│   ├── run_smultixcan_related.sh
│   ├── summarize_twas_results.py
│   ├── summarize_twas_significance.py
│   ├── summarize_twas_single_full.py
│   ├── twas_fair_compare.py
│   └── twas_utils.py
├── .gitignore
└── requirements.txt
```

## Expected Input Layout

The summary scripts assume the following result layout:

```text
TWAS_ROOT/
├── 02.SPrediXcan/
│   └── results_full_inputs_v2/
│       └── <trait>/
│           └── <qtl>.<trait>.<tissue>.csv
└── 03.SMulTiXcan/
    ├── results_full_inputs_v2/
    │   └── <trait>/
    │       └── <qtl>.<trait>.SMultixcan.txt
    └── results_related_v2/
        └── <trait>/
            └── <qtl>.<trait>.SMultixcan.related.txt
```

## Quick Start

Create an environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Summarize all three TWAS result types:

```bash
python scripts/summarize_twas_results.py \
  --twas-root /path/to/twas \
  --output-xlsx results/twas_result_summary.xlsx \
  --output-dir results/summary
```

Count significant genes:

```bash
python scripts/summarize_twas_significance.py \
  --twas-root /path/to/twas \
  --output-xlsx results/twas_significance.xlsx \
  --output-dir results/significance
```

Run fair comparison:

```bash
python scripts/twas_fair_compare.py \
  --twas-root /path/to/twas \
  --output-xlsx results/twas_fair_compare.xlsx \
  --output-dir results/fair_compare
```

## What The Scripts Report

### `summarize_twas_results.py`

- file-level summary for `SPrediXcan`, all-tissue `SMulTiXcan`, and related-tissue `SMulTiXcan`
- top gene and top p-value per file
- all-tissue vs related-tissue comparison

### `summarize_twas_significance.py`

- per-file counts of nominally significant genes (`p < 0.05`)
- per-file counts of `BH-FDR < 0.05` genes
- aggregation by method, trait, QTL, and tissue

### `twas_fair_compare.py`

- number of `trait × qtl` combinations with at least one `FDR < 0.05` gene
- deduplicated unique significant genes for each method

## Notes For Public Release

- Replace project-specific absolute paths with your own directory settings.
- Remove private sample metadata, passwords, and cluster-specific secrets before publishing.
- Keep only manuscript-ready summary files under version control; large result matrices should be stored elsewhere.

