from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from twas_utils import add_common_args, bh_fdr, build_paths, parse_spredixcan_name, parse_smultixcan_name, read_gene_pvalues


def process_file(path: Path, method: str) -> tuple[dict[str, str], bool, set[str]]:
    if method == "single_tissue":
        meta = parse_spredixcan_name(path)
        genes, pvals = read_gene_pvalues(path, ",")
    elif method == "full_multi_tissue":
        meta = parse_smultixcan_name(path, related=False)
        genes, pvals = read_gene_pvalues(path, "\t")
    else:
        meta = parse_smultixcan_name(path, related=True)
        genes, pvals = read_gene_pvalues(path, "\t")

    fdr = bh_fdr(pvals)
    sig_mask = fdr < 0.05
    sig_genes = {gene for gene, is_sig in zip(genes, sig_mask.tolist()) if is_sig}
    return meta, bool(sig_mask.any()), sig_genes


def main() -> int:
    parser = add_common_args(argparse.ArgumentParser())
    args = parser.parse_args()
    paths = build_paths(args.twas_root)

    specs = [
        ("single_tissue", sorted(paths["spredixcan"].glob("*/*.csv"))),
        ("full_multi_tissue", sorted(p for p in paths["smulti_full"].glob("*/*.txt") if p.name.endswith(".SMultixcan.txt"))),
        ("related_multi_tissue", sorted(p for p in paths["smulti_related"].glob("*/*.txt") if p.name.endswith(".SMultixcan.related.txt"))),
    ]

    trait_qtl_seen: dict[str, dict[tuple[str, str], bool]] = {}
    unique_sig_genes: dict[str, set[str]] = {}
    file_rows: list[dict[str, object]] = []

    for method, result_paths in specs:
        tq: dict[tuple[str, str], bool] = {}
        unique_sig_genes[method] = set()
        for path in result_paths:
            meta, has_sig, sig_genes = process_file(path, method)
            key = (meta["trait"], meta["qtl_type"])
            tq[key] = tq.get(key, False) or has_sig
            unique_sig_genes[method].update(sig_genes)
            file_rows.append(
                {
                    "method": method,
                    "trait": meta["trait"],
                    "qtl_type": meta["qtl_type"],
                    "file": str(path),
                    "has_fdr_sig_gene": has_sig,
                    "sig_fdr_gene_count_in_file": len(sig_genes),
                }
            )
        trait_qtl_seen[method] = tq

    overview_df = pd.DataFrame(
        [
            {
                "method": method,
                "trait_qtl_total": len(tq),
                "trait_qtl_with_fdr_sig_gene": int(sum(tq.values())),
                "trait_qtl_without_fdr_sig_gene": int(len(tq) - sum(tq.values())),
                "unique_fdr_sig_genes": len(unique_sig_genes[method]),
            }
            for method, tq in trait_qtl_seen.items()
        ]
    )
    trait_qtl_df = pd.DataFrame(
        [
            {"method": method, "trait": trait, "qtl_type": qtl, "has_fdr_sig_gene": has_sig}
            for method, tq in trait_qtl_seen.items()
            for (trait, qtl), has_sig in sorted(tq.items())
        ]
    )
    file_df = pd.DataFrame(file_rows)
    unique_gene_df = pd.DataFrame(
        [{"method": method, "gene_name": gene} for method, genes in unique_sig_genes.items() for gene in sorted(genes)]
    )

    out = Path(args.output_xlsx)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        overview_df.to_excel(writer, sheet_name="Overview", index=False)
        trait_qtl_df.to_excel(writer, sheet_name="Trait_QTL", index=False)
        file_df.to_excel(writer, sheet_name="By_File", index=False)
        unique_gene_df.to_excel(writer, sheet_name="Unique_Genes", index=False)

    if args.output_dir:
        outdir = Path(args.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        overview_df.to_csv(outdir / "overview.tsv", sep="\t", index=False)
        trait_qtl_df.to_csv(outdir / "trait_qtl.tsv", sep="\t", index=False)
        file_df.to_csv(outdir / "by_file.tsv", sep="\t", index=False)
        unique_gene_df.to_csv(outdir / "unique_genes.tsv", sep="\t", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
