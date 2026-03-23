from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

import pandas as pd


def build_paths(twas_root: str | Path) -> dict[str, Path]:
    root = Path(twas_root)
    return {
        "root": root,
        "spredixcan": root / "02.SPrediXcan" / "results_full_inputs_v2",
        "smulti_full": root / "03.SMulTiXcan" / "results_full_inputs_v2",
        "smulti_related": root / "03.SMulTiXcan" / "results_related_v2",
    }


def add_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--twas-root", required=True, help="Root TWAS directory")
    parser.add_argument("--output-xlsx", required=True, help="Output Excel file")
    parser.add_argument("--output-dir", help="Optional TSV output directory")
    return parser


def parse_spredixcan_name(path: Path) -> dict[str, str]:
    m = re.match(r"(?P<qtl_type>[^.]+)\.(?P<trait>.+)\.(?P<tissue>[^.]+)\.csv$", path.name)
    if not m:
        raise ValueError(f"Unexpected SPrediXcan filename: {path.name}")
    return m.groupdict()


def parse_smultixcan_name(path: Path, related: bool) -> dict[str, str]:
    pattern = (
        r"(?P<qtl_type>[^.]+)\.(?P<trait>.+)\.SMultixcan\.related\.txt$"
        if related
        else r"(?P<qtl_type>[^.]+)\.(?P<trait>.+)\.SMultixcan\.txt$"
    )
    m = re.match(pattern, path.name)
    if not m:
        raise ValueError(f"Unexpected SMulTiXcan filename: {path.name}")
    return m.groupdict()


def safe_neglog10(p: float) -> float | None:
    if pd.isna(p) or p <= 0:
        return None
    return -math.log10(p)


def bh_fdr(pvals: pd.Series) -> pd.Series:
    s = pvals.astype(float)
    n = len(s)
    if n == 0:
        return pd.Series(dtype=float)
    order = s.sort_values(kind="stable").index
    ranked = s.loc[order]
    q = ranked * n / pd.Series(range(1, n + 1), index=order, dtype=float)
    q = q[::-1].cummin()[::-1].clip(upper=1.0)
    out = pd.Series(index=s.index, dtype=float)
    out.loc[order] = q
    return out


def read_gene_pvalues(path: Path, sep: str) -> tuple[list[str], pd.Series]:
    genes: list[str] = []
    pvals: list[float] = []
    with path.open("r", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=sep)
        for row in reader:
            gene = str(row.get("gene_name", "")).strip()
            raw_p = str(row.get("pvalue", "")).strip()
            if not gene or not raw_p:
                continue
            try:
                p = float(raw_p)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(p):
                continue
            genes.append(gene)
            pvals.append(p)
    return genes, pd.Series(pvals, dtype=float)

