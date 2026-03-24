from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from upsetplot import UpSet, from_memberships

sys.path.append(str(Path(__file__).resolve().parents[1]))

from twas_utils import bh_fdr, read_gene_pvalues


def normalize_feature_id(qtl_type: str, value: str) -> str | None:
    """统一不同 QTL 类型的 feature/gene 命名，便于 loci 与 TWAS/COLOC 对齐。"""
    raw = str(value).strip()
    if not raw or raw.lower() == "nan":
        return None
    if qtl_type == "sQTL":
        return raw.split(":")[-1]
    if qtl_type in {"eeQTL", "enQTL", "isoQTL"}:
        return raw.split(":")[0]
    if qtl_type == "3aQTL":
        parts = raw.split("|")
        return parts[1] if len(parts) > 1 else raw
    if qtl_type in {"eQTL", "stQTL"}:
        return raw
    return raw


def extract_trait_name(value: str) -> str:
    """兼容 GWAS overlap 文件里类似 STDERR_BH1 的 trait 写法。"""
    raw = str(value).strip()
    marker = "STDERR_"
    if raw.startswith(marker) and raw.endswith("1"):
        return raw[len(marker) : -1]
    return raw


def read_sig_genes_from_file(path: Path, sep: str, qtl_type: str) -> set[str]:
    """逐文件读取基因和 p 值，按文件内部 BH-FDR < 0.05 取显著基因。"""
    genes, pvals = read_gene_pvalues(path, sep)
    if not genes:
        return set()
    norm_genes = [normalize_feature_id(qtl_type, gene) for gene in genes]
    keep_mask = [gene is not None for gene in norm_genes]
    kept_genes = [gene for gene in norm_genes if gene is not None]
    kept_pvals = pvals.loc[[idx for idx, keep in enumerate(keep_mask) if keep]].reset_index(drop=True)
    if not kept_genes:
        return set()
    fdr = bh_fdr(kept_pvals)
    return {gene for gene, is_sig in zip(kept_genes, (fdr < 0.05).tolist()) if is_sig}


def collect_single_sig_sets(spredixcan_root: Path) -> dict[str, set[str]]:
    trait_to_genes: dict[str, set[str]] = {}
    for path in sorted(spredixcan_root.glob("*/*.csv")):
        parts = path.name.split(".")
        if len(parts) < 4:
            continue
        qtl_type = parts[0]
        trait = ".".join(parts[1:-2])
        sig_genes = read_sig_genes_from_file(path, sep=",", qtl_type=qtl_type)
        if sig_genes:
            trait_to_genes.setdefault(trait, set()).update(sig_genes)
    return trait_to_genes


def collect_multi_sig_sets(smultixcan_root: Path) -> dict[str, set[str]]:
    trait_to_genes: dict[str, set[str]] = {}
    for path in sorted(p for p in smultixcan_root.glob("*/*.txt") if p.name.endswith(".SMultixcan.txt")):
        parts = path.name.split(".")
        if len(parts) < 4:
            continue
        qtl_type = parts[0]
        trait = ".".join(parts[1:-2])
        sig_genes = read_sig_genes_from_file(path, sep="\t", qtl_type=qtl_type)
        if sig_genes:
            trait_to_genes.setdefault(trait, set()).update(sig_genes)
    return trait_to_genes


def load_overlap(paths: list[Path]) -> pd.DataFrame:
    parts = []
    for path in paths:
        df = pd.read_csv(path, sep="\t")
        df["TRAIT"] = df["TRAIT"].map(extract_trait_name)
        df["gene_symbol"] = [
            normalize_feature_id(qtl, feat)
            for qtl, feat in zip(df["QTL_type"], df["phenotype_id"])
        ]
        parts.append(df)
    out = pd.concat(parts, ignore_index=True)
    return out.dropna(subset=["TRAIT", "LEAD_VARIANT", "gene_symbol"])


def load_coloc(paths: list[Path], pph4_cutoff: float) -> pd.DataFrame:
    parts = []
    for path in paths:
        df = pd.read_csv(path, sep="\t")
        df = df[df["PP.H4.abf"] > pph4_cutoff].copy()
        df["gene_symbol"] = [
            normalize_feature_id(qtl, feat)
            for qtl, feat in zip(df["qtl"], df["phenotype"])
        ]
        parts.append(df)
    out = pd.concat(parts, ignore_index=True)
    return out.dropna(subset=["trait", "gene_symbol"])


def build_locus_table(
    overlap_df: pd.DataFrame,
    single_sig: dict[str, set[str]],
    multi_sig: dict[str, set[str]],
    coloc_df: pd.DataFrame,
) -> pd.DataFrame:
    coloc_trait_sets = coloc_df.groupby("trait")["gene_symbol"].apply(set).to_dict()
    rows: list[dict[str, object]] = []
    for trait, trait_df in overlap_df.groupby("TRAIT", sort=True):
        single_genes = single_sig.get(trait, set())
        multi_genes = multi_sig.get(trait, set())
        coloc_genes = coloc_trait_sets.get(trait, set())
        loci = (
            trait_df.groupby("LEAD_VARIANT")["gene_symbol"]
            .apply(lambda x: sorted(set(v for v in x if pd.notna(v))))
            .to_dict()
        )
        for lead_variant, genes in loci.items():
            gene_set = set(genes)
            tags = {"GWAS"}
            if gene_set & single_genes:
                tags.add("S-PrediXcan")
            if gene_set & multi_genes:
                tags.add("S-MultiXcan")
            if gene_set & coloc_genes:
                tags.add("COLOC")
            rows.append(
                {
                    "trait": trait,
                    "lead_variant": lead_variant,
                    "genes": ";".join(genes),
                    "tags": "|".join(sorted(tags)),
                    "membership": tuple(sorted(tags)),
                }
            )
    return pd.DataFrame(rows).sort_values(["trait", "lead_variant"], kind="stable")


def plot_upset(df: pd.DataFrame, title: str, out_prefix: Path) -> None:
    memberships = [tuple(v) for v in df["membership"].tolist()]
    upset_data = from_memberships(memberships)
    fig = plt.figure(figsize=(12, 7))
    upset = UpSet(upset_data, show_counts=True, subset_size="count", sort_by="cardinality")
    upset.plot(fig=fig)
    fig.suptitle(title, fontsize=14)
    fig.tight_layout()
    fig.savefig(out_prefix.with_suffix(".pdf"), dpi=300, bbox_inches="tight")
    fig.savefig(out_prefix.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw GWAS vs S-PrediXcan vs S-MultiXcan vs COLOC UpSet plots."
    )
    parser.add_argument(
        "--spredixcan-root",
        required=True,
        help="02.SPrediXcan/results_full_inputs_v2 directory",
    )
    parser.add_argument(
        "--smultixcan-root",
        required=True,
        help="03.SMulTiXcan/results_full_inputs_v2 directory",
    )
    parser.add_argument(
        "--overlap-tsv",
        required=True,
        nargs="+",
        help="One or more GWAS-QTL overlap TSV files, e.g. gwas_qtl_pairs.tsv",
    )
    parser.add_argument(
        "--coloc-tsv",
        required=True,
        nargs="+",
        help="One or more coloc result TSV files",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for plots and tables",
    )
    parser.add_argument(
        "--pph4-cutoff",
        type=float,
        default=0.8,
        help="PP.H4.abf cutoff for coloc support",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    trait_dir = output_dir / "by_trait"
    output_dir.mkdir(parents=True, exist_ok=True)
    trait_dir.mkdir(parents=True, exist_ok=True)

    overlap_df = load_overlap([Path(p) for p in args.overlap_tsv])
    coloc_df = load_coloc([Path(p) for p in args.coloc_tsv], args.pph4_cutoff)
    single_sig = collect_single_sig_sets(Path(args.spredixcan_root))
    multi_sig = collect_multi_sig_sets(Path(args.smultixcan_root))
    locus_df = build_locus_table(overlap_df, single_sig, multi_sig, coloc_df)
    locus_df.to_csv(output_dir / "gwas_twas_coloc_locus_tags.tsv", sep="\t", index=False)

    summary_rows = []
    for trait, trait_df in locus_df.groupby("trait", sort=True):
        summary_rows.append(
            {
                "trait": trait,
                "n_loci": len(trait_df),
                "with_spredixcan": int(trait_df["tags"].str.contains("S-PrediXcan").sum()),
                "with_smultixcan": int(trait_df["tags"].str.contains("S-MultiXcan").sum()),
                "with_coloc": int(trait_df["tags"].str.contains("COLOC").sum()),
                "all_four": int(
                    trait_df["tags"].eq("COLOC|GWAS|S-MultiXcan|S-PrediXcan").sum()
                ),
                "tag_pattern_count": int(trait_df["tags"].nunique()),
            }
        )
        if trait_df["membership"].nunique() > 1:
            plot_upset(
                trait_df,
                f"GWAS vs S-PrediXcan vs S-MultiXcan vs COLOC: {trait}",
                trait_dir / f"{trait}_upset_final",
            )

    summary_df = pd.DataFrame(summary_rows).sort_values("trait", kind="stable")
    summary_df.to_csv(output_dir / "trait_upset_summary.tsv", sep="\t", index=False)
    plot_upset(
        locus_df,
        "GWAS vs S-PrediXcan vs S-MultiXcan vs COLOC Across All Traits",
        output_dir / "all_traits_upset_final",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
