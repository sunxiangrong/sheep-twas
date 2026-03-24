# Inputs And Outputs

## Input File Naming

### SPrediXcan

```text
<qtl>.<trait>.<tissue>.csv
```

Required columns:

- `gene_name`
- `pvalue`

Optional columns:

- `gene`
- `zscore`

### SMulTiXcan

```text
<qtl>.<trait>.SMultixcan.txt
<qtl>.<trait>.SMultixcan.related.txt
```

Required columns:

- `gene_name`
- `pvalue`

Optional columns:

- `gene`
- `t_i_best`
- `t_i_worst`
- `n`
- `n_indep`

## Output Tables

### `summary/`

- overall file-level summary
- top hits
- all-tissue vs related-tissue comparison

### `significance/`

- nominal and `BH-FDR` significant gene counts
- grouped by method, trait, QTL, tissue

### `fair_compare/`

- `trait × qtl` combinations with at least one `FDR < 0.05` gene
- deduplicated unique `FDR < 0.05` genes per method

### `upset_final/`

- overall `GWAS vs S-PrediXcan vs S-MultiXcan vs COLOC` UpSet figure
- per-trait UpSet figures
- `gwas_twas_coloc_locus_tags.tsv`
- `trait_upset_summary.tsv`

## Additional Inputs For UpSet Plot

The UpSet plotting script needs two extra input groups beyond TWAS result folders.

### GWAS-QTL overlap tables

These tables should contain at least:

- `TRAIT`
- `LEAD_VARIANT`
- `QTL_type`
- `phenotype_id`

Example files:

```text
/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs.tsv
/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/gwas_qtl_pairs_xinjiang.tsv
```

### COLOC summary tables

These tables should contain at least:

- `trait`
- `qtl`
- `phenotype`
- `PP.H4.abf`

Only rows with `PP.H4.abf > cutoff` are treated as coloc-supported genes.

Example files:

```text
/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_new/GWAS.all.addcol.sig.pph4.new
/storage/public/home/2020060185/00.sheep_goatGTEx/01.sheepGTEx/04.gwas_coloc/coloc_xinjiang/GWAS.all.addcol.sig.pph4
```
