# sheep-twas

English | [中文](#中文说明)

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
- `GWAS loci vs S-PrediXcan vs S-MultiXcan vs COLOC` UpSet plotting

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
│   ├── twas_utils.py
│   ├── run/
│   │   └── run_smultixcan_related.sh
│   ├── plot/
│   │   ├── plot_twas_coloc_upset.py
│   │   └── submit_plot_twas_coloc_upset.sh
│   └── summary/
│       ├── summarize_twas_results.py
│       ├── summarize_twas_significance.py
│       ├── summarize_twas_single_full.py
│       └── twas_fair_compare.py
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
python scripts/summary/summarize_twas_results.py \
  --twas-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas \
  --output-xlsx results/twas_result_summary.xlsx \
  --output-dir results/summary
```

Count significant genes:

```bash
python scripts/summary/summarize_twas_significance.py \
  --twas-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas \
  --output-xlsx results/twas_significance.xlsx \
  --output-dir results/significance
```

Run fair comparison:

```bash
python scripts/summary/twas_fair_compare.py \
  --twas-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas \
  --output-xlsx results/twas_fair_compare.xlsx \
  --output-dir results/fair_compare
```

Draw GWAS-vs-TWAS-vs-COLOC UpSet plots:

```bash
python scripts/plot/plot_twas_coloc_upset.py \
  --spredixcan-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas/02.SPrediXcan/results_full_inputs_v2 \
  --smultixcan-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas/03.SMulTiXcan/results_full_inputs_v2 \
  --overlap-tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs.tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs_xinjiang.tsv \
  --coloc-tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_new/GWAS.all.addcol.sig.pph4.new /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_xinjiang/GWAS.all.addcol.sig.pph4 \
  --output-dir results/upset_final
```

Submit the same plotting workflow on a cluster:

```bash
export TWAS_CONFIG=/path/to/twas_config.sh
bash scripts/plot/submit_plot_twas_coloc_upset.sh
```

## What The Scripts Report

### `scripts/summary/summarize_twas_results.py`

- file-level summary for `SPrediXcan`, all-tissue `SMulTiXcan`, and related-tissue `SMulTiXcan`
- top gene and top p-value per file
- all-tissue vs related-tissue comparison

### `scripts/summary/summarize_twas_significance.py`

- per-file counts of nominally significant genes (`p < 0.05`)
- per-file counts of `BH-FDR < 0.05` genes
- aggregation by method, trait, QTL, and tissue

### `scripts/summary/twas_fair_compare.py`

- number of `trait × qtl` combinations with at least one `FDR < 0.05` gene
- deduplicated unique significant genes for each method

### `scripts/plot/plot_twas_coloc_upset.py`

- normalize gene IDs across QTL types
- map `GWAS loci` to candidate genes
- intersect loci with final `S-PrediXcan`, `S-MultiXcan`, and `COLOC` support
- draw one overall UpSet plot and one UpSet plot per trait

## Notes For Public Release

- Replace project-specific absolute paths with your own directory settings.
- Remove private sample metadata, passwords, and cluster-specific secrets before publishing.
- Keep only manuscript-ready summary files under version control; large result matrices should be stored elsewhere.

---

## 中文说明

这是一个用于家畜 post-GWAS 分析的 TWAS 工作流代码仓库。

这个仓库有两个目的：

1. 作为我们绵羊 post-GWAS 项目中 TWAS 流程的可复现备份。
2. 作为论文投稿时配套公开的代码仓库。

当前仓库主要包含：

- `SPrediXcan` 单组织结果整理
- `SMulTiXcan` 全组织多组织结果整理
- `SMulTiXcan` 相关组织重跑脚本
- 基于每个结果文件内部 `BH-FDR` 的显著性统计
- 三类 TWAS 结果的公平比较
- `GWAS loci vs S-PrediXcan vs S-MultiXcan vs COLOC` 的 UpSet 作图

## 仓库结构

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
│   ├── twas_utils.py
│   ├── run/
│   │   └── run_smultixcan_related.sh
│   ├── plot/
│   │   ├── plot_twas_coloc_upset.py
│   │   └── submit_plot_twas_coloc_upset.sh
│   └── summary/
│       ├── summarize_twas_results.py
│       ├── summarize_twas_significance.py
│       ├── summarize_twas_single_full.py
│       └── twas_fair_compare.py
├── .gitignore
└── requirements.txt
```

## 输入目录要求

汇总脚本默认你的 `TWAS` 结果目录结构是：

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

## 快速开始

先建立 Python 环境：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

汇总三类 TWAS 结果：

```bash
python scripts/summary/summarize_twas_results.py \
  --twas-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas \
  --output-xlsx results/twas_result_summary.xlsx \
  --output-dir results/summary
```

统计显著基因：

```bash
python scripts/summary/summarize_twas_significance.py \
  --twas-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas \
  --output-xlsx results/twas_significance.xlsx \
  --output-dir results/significance
```

做三类方法的公平比较：

```bash
python scripts/summary/twas_fair_compare.py \
  --twas-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas \
  --output-xlsx results/twas_fair_compare.xlsx \
  --output-dir results/fair_compare
```

绘制 `GWAS loci vs 单组织 TWAS vs 多组织 TWAS vs COLOC` 的 UpSet 图：

```bash
python scripts/plot/plot_twas_coloc_upset.py \
  --spredixcan-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas/02.SPrediXcan/results_full_inputs_v2 \
  --smultixcan-root /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/twas/03.SMulTiXcan/results_full_inputs_v2 \
  --overlap-tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs.tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs_xinjiang.tsv \
  --coloc-tsv /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_new/GWAS.all.addcol.sig.pph4.new /storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_xinjiang/GWAS.all.addcol.sig.pph4 \
  --output-dir results/upset_final
```

如果要提交到集群跑：

```bash
export TWAS_CONFIG=/path/to/twas_config.sh
bash scripts/plot/submit_plot_twas_coloc_upset.sh
```

## 各脚本输出什么

### `scripts/summary/summarize_twas_results.py`

- `SPrediXcan`、全组织 `SMulTiXcan`、相关组织 `SMulTiXcan` 的逐文件汇总
- 每个结果文件的 top gene 和 top p-value
- 全组织多组织与相关组织多组织的对比结果

### `scripts/summary/summarize_twas_significance.py`

- 每个结果文件中 nominal 显著基因数（`p < 0.05`）
- 每个结果文件中 `BH-FDR < 0.05` 显著基因数
- 按方法、性状、QTL、组织进行聚合统计

### `scripts/summary/twas_fair_compare.py`

- 每种方法中有多少个 `trait × qtl` 至少出现 1 个 `FDR < 0.05` 基因
- 每种方法去重后的显著基因数

### `scripts/plot/plot_twas_coloc_upset.py`

- 统一不同 `QTL_type` 下的基因命名
- 将 `GWAS loci` 映射到候选基因集合
- 用最终版 `TWAS` 结果与 `COLOC` 结果做交集
- 生成总图和每个性状的 UpSet 图

## 公开发布前建议

- 把项目私有绝对路径替换成你自己的分析路径。
- 删除样本隐私信息、密码、集群特定密钥等敏感内容。
- 大型结果矩阵建议不要直接进 Git，代码仓库里保留脚本和投稿级汇总表即可。
