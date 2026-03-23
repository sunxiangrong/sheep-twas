from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from twas_utils import add_common_args, build_paths, parse_spredixcan_name, parse_smultixcan_name, safe_neglog10


def summarize_spredixcan(path: Path) -> dict[str, object]:
    meta = parse_spredixcan_name(path)
    df = pd.read_csv(path).sort_values("pvalue", kind="stable")
    top = df.iloc[0]
    return {
        "analysis": "single_tissue",
        "trait": meta["trait"],
        "qtl_type": meta["qtl_type"],
        "tissue": meta["tissue"],
        "file": str(path),
        "gene_count": int(len(df)),
        "top_gene": top.get("gene_name", top.get("gene")),
        "top_pvalue": float(top["pvalue"]),
        "top_neglog10p": safe_neglog10(float(top["pvalue"])),
        "nominal_p_lt_0_05": int((df["pvalue"] < 0.05).sum()),
    }


def summarize_smultixcan(path: Path) -> dict[str, object]:
    meta = parse_smultixcan_name(path, related=False)
    df = pd.read_table(path).sort_values("pvalue", kind="stable")
    top = df.iloc[0]
    return {
        "analysis": "full_multi_tissue",
        "trait": meta["trait"],
        "qtl_type": meta["qtl_type"],
        "file": str(path),
        "gene_count": int(len(df)),
        "top_gene": top.get("gene_name", top.get("gene")),
        "top_pvalue": float(top["pvalue"]),
        "top_neglog10p": safe_neglog10(float(top["pvalue"])),
        "top_tissue_best": top.get("t_i_best"),
        "n_tissues_used": float(top["n"]) if "n" in df.columns else None,
    }


def main() -> int:
    parser = add_common_args(argparse.ArgumentParser())
    args = parser.parse_args()
    paths = build_paths(args.twas_root)

    single_df = pd.DataFrame(summarize_spredixcan(p) for p in sorted(paths["spredixcan"].glob("*/*.csv")))
    full_df = pd.DataFrame(
        summarize_smultixcan(p)
        for p in sorted(p for p in paths["smulti_full"].glob("*/*.txt") if p.name.endswith(".SMultixcan.txt"))
    )

    single_best = (
        single_df.sort_values("top_pvalue", kind="stable")
        .groupby(["trait", "qtl_type"], as_index=False)
        .first()[["trait", "qtl_type", "tissue", "top_gene", "top_pvalue"]]
        .rename(columns={"tissue": "single_best_tissue", "top_gene": "single_best_gene", "top_pvalue": "single_best_pvalue"})
    )
    full_best = full_df.rename(
        columns={"top_tissue_best": "multi_best_tissue", "top_gene": "multi_best_gene", "top_pvalue": "multi_best_pvalue"}
    )[["trait", "qtl_type", "multi_best_tissue", "multi_best_gene", "multi_best_pvalue"]]
    trait_qtl_df = single_best.merge(full_best, on=["trait", "qtl_type"], how="outer")
    trait_qtl_df["multi_better_than_single"] = trait_qtl_df["multi_best_pvalue"] < trait_qtl_df["single_best_pvalue"]

    overview_df = pd.DataFrame(
        [
            {"analysis": "single_tissue", "file_count": int(len(single_df)), "trait_count": int(single_df["trait"].nunique()), "qtl_count": int(single_df["qtl_type"].nunique())},
            {"analysis": "full_multi_tissue", "file_count": int(len(full_df)), "trait_count": int(full_df["trait"].nunique()), "qtl_count": int(full_df["qtl_type"].nunique())},
        ]
    )

    top_hits_df = pd.concat(
        [
            single_df.sort_values("top_pvalue", kind="stable").head(50).assign(analysis_group="single_tissue"),
            full_df.sort_values("top_pvalue", kind="stable").head(50).assign(analysis_group="full_multi_tissue"),
        ],
        ignore_index=True,
    )

    out = Path(args.output_xlsx)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        overview_df.to_excel(writer, sheet_name="Overview", index=False)
        trait_qtl_df.to_excel(writer, sheet_name="Trait_QTL_Summary", index=False)
        single_df.to_excel(writer, sheet_name="SPrediXcan", index=False)
        full_df.to_excel(writer, sheet_name="SMulti_Full", index=False)
        top_hits_df.to_excel(writer, sheet_name="TopHits", index=False)

    if args.output_dir:
        outdir = Path(args.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        overview_df.to_csv(outdir / "overview.tsv", sep="\t", index=False)
        trait_qtl_df.to_csv(outdir / "trait_qtl_summary.tsv", sep="\t", index=False)
        single_df.to_csv(outdir / "spredixcan_summary.tsv", sep="\t", index=False)
        full_df.to_csv(outdir / "smultixcan_full_summary.tsv", sep="\t", index=False)
        top_hits_df.to_csv(outdir / "top_hits.tsv", sep="\t", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

