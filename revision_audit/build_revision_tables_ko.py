"""Korean bodies of the seven version-2.0 tables, derived from the English bodies.

The English table bodies in paper_en/tables/ are written by build_revision_tables.py and
publication_upgrade/build_matched_menu_table.py. This script copies them to paper_ko/tables/ and replaces
only the row label (the first cell of each row) with its Korean translation, so every number in the Korean
tables is identical to the English one by construction. It fails if a row label has no translation or if
anything other than the label differs.

Run after the English table builders (run_revision.sh does this):
    python revision_audit/build_revision_tables_ko.py
    python revision_audit/build_revision_tables_ko.py --check   # compare with the files on disk, write nothing
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "paper_en" / "tables"
KO = ROOT / "paper_ko" / "tables"

GROUPS = {"High income": "고소득국", "Upper-middle income": "상위중소득국",
          "Lower-middle income": "하위중소득국", "Low income": "저소득국"}
LABELS = {
    "tab_burden_compact.tex": GROUPS,
    "tab_quintile.tex": GROUPS,
    "tab_500_scenario.tex": GROUPS,
    # cutoffs are numbers and stay as they are
    "tab_thresholds.tex": {"1\\%": "1\\%", "2\\%": "2\\%", "5\\%": "5\\%", "10\\%": "10\\%"},
    "tab_price_revision.tex": {"ChatGPT Go": "ChatGPT Go", "ChatGPT Plus": "ChatGPT Plus",
                               "Claude Pro": "Claude Pro", "Google AI Pro": "Google AI Pro",
                               "Go / Plus ratio": "Go/Plus 가격비"},
    "tab_matched_menu_sensitivity.tex": {"All matched storefronts": "짝지은 스토어 전체",
                                         "USD only": "달러 표시 스토어만",
                                         "Exclude USD": "달러 표시 제외",
                                         "Exclude USD and EUR": "달러·유로 표시 제외"},
    "tab_gap_revision.tex": {"Baseline": "기준", "2025 GNI only": "2025년 GNI만",
                             "Non-high-income": "비고소득국", "Region fixed effects": "지역 고정효과",
                             "Internet, education, urbanisation": "인터넷·교육·도시화 통제",
                             "Population weighted": "인구 가중"},
}


def translate(name):
    out = []
    for line in (EN / name).read_text(encoding="utf-8").split("\n"):
        if " & " not in line:          # blank lines and the like are kept as they are
            out.append(line)
            continue
        label, rest = line.split(" & ", 1)
        if label not in LABELS[name]:
            raise SystemExit(f"{name}: no Korean label for row '{label}'")
        out.append(LABELS[name][label] + " & " + rest)
    text = "\n".join(out)
    # everything after the first cell must be unchanged
    for a, b in zip((EN / name).read_text(encoding="utf-8").split("\n"), text.split("\n")):
        if " & " in a and a.split(" & ", 1)[1] != b.split(" & ", 1)[1]:
            raise SystemExit(f"{name}: a cell other than the row label changed")
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    KO.mkdir(parents=True, exist_ok=True)
    bad = []
    for name in LABELS:
        text = translate(name)
        target = KO / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                bad.append(name)
        else:
            target.write_text(text, encoding="utf-8")
    if bad:
        raise SystemExit("Korean table bodies differ from the English-derived versions: " + ", ".join(bad))
    print(("checked " if args.check else "wrote ") + f"{len(LABELS)} Korean table bodies in paper_ko/tables")


if __name__ == "__main__":
    sys.exit(main())
