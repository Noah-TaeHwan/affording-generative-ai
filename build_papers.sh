#!/usr/bin/env bash
# Compile both manuscripts and record which sources each PDF was built from (checked by check_release.sh).
# Needs TeX Live: pdflatex (English), xelatex (Korean; fonts Liberation Serif and Noto Serif/Sans CJK KR), bibtex.
set -euo pipefail
cd "$(dirname "$0")"
# fixed timestamps make rebuilds byte-identical (override SOURCE_DATE_EPOCH for a new version)
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1790553600}" FORCE_SOURCE_DATE=1

build() {  # $1 = folder, $2 = engine
  (
    cd "$1"
    engine=$2
    run() { "$engine" -interaction=nonstopmode -halt-on-error main.tex >/dev/null || { tail -40 main.log >&2; exit 1; }; }
    run; bibtex main >/dev/null; run; run; run
    if grep -q 'Rerun to get\|There were undefined references' main.log; then
      echo "$1: unresolved references" >&2; exit 1
    fi
    # lines sticking into the margin by more than 5pt are errors, not warnings
    wide=$(grep -o 'Overfull \\hbox ([0-9.]*pt too wide) in paragraph' main.log | awk -F'[(p]' '$2+0 > 5' || true)
    [ -z "$wide" ] || { echo "$1: text runs into the margin:" >&2; grep -A2 'Overfull \\hbox' main.log >&2; exit 1; }
    shasum -a 256 main.tex references.bib tables/*.tex figures/*.pdf main.pdf > main.pdf.sources.sha256
    rm -f main.aux main.log main.out main.blg main.toc
    echo "$1: main.pdf built"
  )
}

build paper_en pdflatex
build paper_ko xelatex
