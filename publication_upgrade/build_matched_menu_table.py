#!/usr/bin/env python3
"""Rebuild/check the publication's matched-menu table from audit output.

Run price_reliability.py first. Every row uses HC3 SE and a normal 95% interval;
the separate revision-audit table retains currency-clustered CR1 inference.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
CSV = HERE / "results/matched_menu_currency_sensitivity.csv"
TABLE = HERE.parent / "paper_en/tables/tab_matched_menu_sensitivity.tex"
KEEP = ["All matched storefronts", "USD only", "Exclude USD", "Exclude USD and EUR"]


def construct():
    with CSV.open(newline="") as f:
        records = {r["specification"]:r for r in csv.DictReader(f)}
    rows = []
    for name in KEEP:
        r = records[name]
        row = [name, f"{float(r['slope']):.3f}", f"{float(r['se_HC3']):.3f}",
               f"[{float(r['hc3_ci_low']):.3f}, {float(r['hc3_ci_high']):.3f}]",
               str(int(r["n"]))]
        rows.append(" & ".join(row) + r" \\")
    return ("\n".join(rows)+"\n").encode("utf-8")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without modifying the LaTeX table.")
    args=parser.parse_args()
    expected=construct()
    before=TABLE.read_bytes() if TABLE.exists() else None
    match=before==expected
    generated=HERE/"results/tab_matched_menu_sensitivity.tex"
    generated.write_bytes(expected)
    if not args.check:
        TABLE.write_bytes(expected)
    report=dict(mode="check" if args.check else "write", source=str(CSV.relative_to(HERE)),
                table=str(TABLE.relative_to(HERE.parent)), byte_identical_before_write=match,
                sha256=hashlib.sha256(expected).hexdigest(),
                convention="HC3 SE and normal 95% interval for all four rows")
    (HERE/"results/matched_menu_table_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return 0 if match or not args.check else 1


if __name__ == "__main__":
    raise SystemExit(main())
