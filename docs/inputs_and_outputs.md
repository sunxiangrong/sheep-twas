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

