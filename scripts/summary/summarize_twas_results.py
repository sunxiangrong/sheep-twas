from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from twas_utils import (
    add_common_args,
    build_paths,
    parse_spredixcan_name,
    parse_smultixcan_name,
    safe_neglog10,
)


def summarize_spredixcan(path: Path) -> dict[str, object]:
    meta = parse_spredixcan_name(path)
    df = pd.read_csv(path)
    df = df.sort_values("pvalue", kind="stable")
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
        "top_zscore": float(top["zscore"]) if "zscore" in df.columns else None,
        "nominal_p_lt_0_05": int((df["pvalue"] < 0.05).sum()),
    }


def summarize_smultixcan(path: Path, related: bool) -> dict[str, object]:
    meta = parse_smultixcan_name(path, related=related)
    df = pd.read_table(path)
    df = df.sort_values("pvalue", kind="stable")
    top = df.iloc[0]
    return {
        "analysis": "related_multi_tissue" if related else "full_multi_tissue",
        "trait": meta["trait"],
        "qtl_type": meta["qtl_type"],
        "file": str(path),
        "gene_count": int(len(df)),
        "top_gene": top.get("gene_name", top.get("gene")),
        "top_pvalue": float(top["pvalue"]),
        "top_neglog10p": safe_neglog10(float(top["pvalue"])),
        "top_tissue_best": top.get("t_i_best"),
        "top_tissue_worst": top.get("t_i_worst"),
        "n_tissues_used": float(top["n"]) if "n" in df.columns else None,
        "n_tissues_indep": float(top["n_indep"]) if "n_indep" in df.columns else None,
    }


def build_sheet(paths: list[Path], kind: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(paths):
        if kind == "spredixcan":
            rows.append(summarize_spredixcan(path))
        elif kind == "smulti_full":
            rows.append(summarize_smultixcan(path, related=False))
        elif kind == "smulti_related":
            rows.append(summarize_smultixcan(path, related=True))
        else:
            raise ValueError(kind)
    return pd.DataFrame(rows)


def build_overview(single_df: pd.DataFrame, full_df: pd.DataFrame, related_df: pd.DataFrame, paths: dict[str, Path]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "analysis": "single_tissue",
                "source_dir": str(paths["spredixcan"]),
                "file_count": int(len(single_df)),
                "trait_count": int(single_df["trait"].nunique()) if not single_df.empty else 0,
                "qtl_count": int(single_df["qtl_type"].nunique()) if not single_df.empty else 0,
            },
            {
                "analysis": "full_multi_tissue",
                "source_dir": str(paths["smulti_full"]),
                "file_count": int(len(full_df)),
                "trait_count": int(full_df["trait"].nunique()) if not full_df.empty else 0,
                "qtl_count": int(full_df["qtl_type"].nunique()) if not full_df.empty else 0,
            },
            {
                "analysis": "related_multi_tissue",
                "source_dir": str(paths["smulti_related"]),
                "file_count": int(len(related_df)),
                "trait_count": int(related_df["trait"].nunique()) if not related_df.empty else 0,
                "qtl_count": int(related_df["qtl_type"].nunique()) if not related_df.empty else 0,
            },
        ]
    )


def build_comparison(full_df: pd.DataFrame, related_df: pd.DataFrame) -> pd.DataFrame:
    if full_df.empty or related_df.empty:
        return pd.DataFrame()
    cols = ["trait", "qtl_type", "gene_count", "top_gene", "top_pvalue", "top_neglog10p", "top_tissue_best", "n_tissues_used"]
    merged = full_df[cols].merge(related_df[cols], on=["trait", "qtl_type"], suffixes=("_full", "_related"))
    merged["related_better_top_p"] = merged["top_pvalue_related"] < merged["top_pvalue_full"]
    merged["same_top_gene"] = merged["top_gene_related"] == merged["top_gene_full"]
    return merged.sort_values(["related_better_top_p", "top_pvalue_related"], ascending=[False, True], kind="stable")


def build_top_hits(single_df: pd.DataFrame, full_df: pd.DataFrame, related_df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for df, label in [(single_df, "single_tissue"), (full_df, "full_multi_tissue"), (related_df, "related_multi_tissue")]:
        if df.empty:
            continue
        ranked = df.sort_values("top_pvalue", kind="stable").head(30).copy()
        ranked.insert(0, "analysis_group", label)
        frames.append(ranked)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> int:
    parser = add_common_args(argparse.ArgumentParser())
    args = parser.parse_args()
    paths = build_paths(args.twas_root)

    single_paths = list(paths["spredixcan"].glob("*/*.csv"))
    full_paths = [p for p in paths["smulti_full"].glob("*/*.txt") if p.name.endswith(".SMultixcan.txt")]
    related_paths = [p for p in paths["smulti_related"].glob("*/*.txt") if p.name.endswith(".SMultixcan.related.txt")]

    single_df = build_sheet(single_paths, "spredixcan")
    full_df = build_sheet(full_paths, "smulti_full")
    related_df = build_sheet(related_paths, "smulti_related")
    overview_df = build_overview(single_df, full_df, related_df, paths)
    comparison_df = build_comparison(full_df, related_df)
    top_hits_df = build_top_hits(single_df, full_df, related_df)

    out = Path(args.output_xlsx)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        overview_df.to_excel(writer, sheet_name="Overview", index=False)
        single_df.to_excel(writer, sheet_name="SPrediXcan", index=False)
        full_df.to_excel(writer, sheet_name="SMulti_Full", index=False)
        related_df.to_excel(writer, sheet_name="SMulti_Related", index=False)
        comparison_df.to_excel(writer, sheet_name="Full_vs_Related", index=False)
        top_hits_df.to_excel(writer, sheet_name="TopHits", index=False)

    if args.output_dir:
        outdir = Path(args.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        overview_df.to_csv(outdir / "overview.tsv", sep="\t", index=False)
        single_df.to_csv(outdir / "spredixcan_summary.tsv", sep="\t", index=False)
        full_df.to_csv(outdir / "smultixcan_full_summary.tsv", sep="\t", index=False)
        related_df.to_csv(outdir / "smultixcan_related_summary.tsv", sep="\t", index=False)
        comparison_df.to_csv(outdir / "smultixcan_full_vs_related.tsv", sep="\t", index=False)
        top_hits_df.to_csv(outdir / "top_hits.tsv", sep="\t", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
