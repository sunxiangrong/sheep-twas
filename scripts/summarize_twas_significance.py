from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from twas_utils import add_common_args, bh_fdr, build_paths, parse_spredixcan_name, parse_smultixcan_name


def count_file(path: Path, method: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    if method == "single_tissue":
        meta = parse_spredixcan_name(path)
        df = pd.read_csv(path, usecols=["gene_name", "pvalue"])
        df["tissue"] = meta["tissue"]
    elif method == "full_multi_tissue":
        meta = parse_smultixcan_name(path, related=False)
        df = pd.read_table(path, usecols=lambda c: c in {"gene_name", "pvalue", "t_i_best"})
    else:
        meta = parse_smultixcan_name(path, related=True)
        df = pd.read_table(path, usecols=lambda c: c in {"gene_name", "pvalue", "t_i_best"})

    df["fdr_bh"] = bh_fdr(df["pvalue"])
    df["sig_raw"] = df["pvalue"] < 0.05
    df["sig_fdr"] = df["fdr_bh"] < 0.05
    top = df.sort_values("pvalue", kind="stable").iloc[0]

    row = {
        "method": method,
        "trait": meta["trait"],
        "qtl_type": meta["qtl_type"],
        "tissue": meta.get("tissue"),
        "file": str(path),
        "gene_total": int(len(df)),
        "sig_raw_count": int(df["sig_raw"].sum()),
        "sig_fdr_count": int(df["sig_fdr"].sum()),
        "top_gene": top["gene_name"],
        "top_pvalue": float(top["pvalue"]),
    }
    if "t_i_best" in df.columns:
        row["top_tissue_best"] = top.get("t_i_best")

    tissue_rows: list[dict[str, object]] = []
    if method == "single_tissue":
        grouped = df.groupby("tissue", dropna=False).agg(sig_raw_gene_hits=("sig_raw", "sum"), sig_fdr_gene_hits=("sig_fdr", "sum")).reset_index()
        grouped.insert(0, "method", method)
        grouped.insert(1, "trait", meta["trait"])
        grouped.insert(2, "qtl_type", meta["qtl_type"])
        tissue_rows = grouped.to_dict("records")
    return row, tissue_rows


def aggregate_counts(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        df.groupby(group_cols, dropna=False)
        .agg(file_count=("file", "nunique"), gene_total=("gene_total", "sum"), sig_raw_count=("sig_raw_count", "sum"), sig_fdr_count=("sig_fdr_count", "sum"))
        .reset_index()
        .sort_values(group_cols, kind="stable")
    )


def main() -> int:
    parser = add_common_args(argparse.ArgumentParser())
    args = parser.parse_args()
    paths = build_paths(args.twas_root)

    specs = [
        ("single_tissue", sorted(paths["spredixcan"].glob("*/*.csv"))),
        ("full_multi_tissue", sorted(p for p in paths["smulti_full"].glob("*/*.txt") if p.name.endswith(".SMultixcan.txt"))),
        ("related_multi_tissue", sorted(p for p in paths["smulti_related"].glob("*/*.txt") if p.name.endswith(".SMultixcan.related.txt"))),
    ]

    file_rows: list[dict[str, object]] = []
    tissue_rows: list[dict[str, object]] = []
    for method, result_paths in specs:
        for path in result_paths:
            row, per_tissue = count_file(path, method)
            file_rows.append(row)
            tissue_rows.extend(per_tissue)

    file_df = pd.DataFrame(file_rows)
    tissue_df = pd.DataFrame(tissue_rows)
    overview_df = (
        file_df.groupby("method")
        .agg(file_count=("file", "count"), trait_count=("trait", "nunique"), qtl_count=("qtl_type", "nunique"), gene_total=("gene_total", "sum"), sig_raw_count=("sig_raw_count", "sum"), sig_fdr_count=("sig_fdr_count", "sum"))
        .reset_index()
    )
    qtl_df = aggregate_counts(file_df, ["method", "qtl_type"])
    trait_df = aggregate_counts(file_df, ["method", "trait"])
    trait_qtl_df = aggregate_counts(file_df, ["method", "trait", "qtl_type"])
    single_tissue_df = aggregate_counts(file_df[file_df["method"] == "single_tissue"], ["method", "tissue"])

    out = Path(args.output_xlsx)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        overview_df.to_excel(writer, sheet_name="Overview", index=False)
        qtl_df.to_excel(writer, sheet_name="By_QTL", index=False)
        trait_df.to_excel(writer, sheet_name="By_Trait", index=False)
        trait_qtl_df.to_excel(writer, sheet_name="By_Trait_QTL", index=False)
        single_tissue_df.to_excel(writer, sheet_name="Single_By_Tissue", index=False)
        tissue_df.to_excel(writer, sheet_name="Sig_Gene_TissueHits", index=False)
        file_df.to_excel(writer, sheet_name="By_File", index=False)

    if args.output_dir:
        outdir = Path(args.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        overview_df.to_csv(outdir / "overview.tsv", sep="\t", index=False)
        qtl_df.to_csv(outdir / "by_qtl.tsv", sep="\t", index=False)
        trait_df.to_csv(outdir / "by_trait.tsv", sep="\t", index=False)
        trait_qtl_df.to_csv(outdir / "by_trait_qtl.tsv", sep="\t", index=False)
        single_tissue_df.to_csv(outdir / "single_by_tissue.tsv", sep="\t", index=False)
        tissue_df.to_csv(outdir / "sig_gene_tissue_hits.tsv", sep="\t", index=False)
        file_df.to_csv(outdir / "by_file.tsv", sep="\t", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

