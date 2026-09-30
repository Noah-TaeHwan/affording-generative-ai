#!/usr/bin/env bash
# Compile the manuscripts and record which sources each PDF was built from (checked by check_release.sh).
# Needs TeX Live: pdflatex (English), xelatex (Korean; fonts Liberation Serif and Noto Serif/Sans CJK KR), bibtex.
#
# paper_en: main.pdf (identified manuscript), main_anon.pdf (anonymised review copy, built from the same
#           main.tex with the \ifanon switch set) and titlepage.pdf (separate title page for double-anonymised review).
# paper_ko: main.pdf (Korean edition: translation of the English version 2.0 manuscript, same tables and figures).
set -euo pipefail
cd "$(dirname "$0")"
# fixed timestamps make rebuilds byte-identical (override SOURCE_DATE_EPOCH for a new version)
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1790726400}" FORCE_SOURCE_DATE=1

check_log() {  # $1 = log file, $2 = label
  if grep -q 'Rerun to get\|There were undefined references' "$1"; then
    echo "$2: unresolved references" >&2; exit 1
  fi
  # lines sticking into the margin by more than 5pt are errors, not warnings
  wide=$(grep -o 'Overfull \\hbox ([0-9.]*pt too wide) in paragraph' "$1" | awk -F'[(p]' '$2+0 > 5' || true)
  [ -z "$wide" ] || { echo "$2: text runs into the margin:" >&2; grep -A2 'Overfull \\hbox' "$1" >&2; exit 1; }
}

compile() {  # $1 = engine, $2 = jobname, $3 = argument passed to the engine (file name or TeX code)
  local engine=$1 job=$2 arg=$3
  run() { "$engine" -interaction=nonstopmode -halt-on-error -jobname="$job" "$arg" >/dev/null || { tail -40 "$job.log" >&2; exit 1; }; }
  run; bibtex "$job" >/dev/null; run; run; run
  check_log "$job.log" "$job"
}

(
  cd paper_en
  compile pdflatex main main.tex
  compile pdflatex main_anon '\newif\ifanon\anontrue\input{main.tex}'
  pdflatex -interaction=nonstopmode -halt-on-error titlepage.tex >/dev/null || { tail -40 titlepage.log >&2; exit 1; }
  pdflatex -interaction=nonstopmode -halt-on-error titlepage.tex >/dev/null
  # the anonymised copy must not carry the author's name, contact details or repository links
  if pdftotext main_anon.pdf - | grep -q -i -E 'taehwan|orcid|noah\.taehwan|zenodo|paju'; then
    echo "paper_en: identifying string found in main_anon.pdf" >&2; exit 1
  fi
  shasum -a 256 main.tex titlepage.tex references.bib apalike-doi.bst tables/*.tex figures/*.pdf main.pdf main_anon.pdf titlepage.pdf > main.pdf.sources.sha256
  rm -f main.aux main.log main.out main.blg main.toc main_anon.aux main_anon.log main_anon.out main_anon.blg titlepage.aux titlepage.log titlepage.out
  echo "paper_en: main.pdf, main_anon.pdf and titlepage.pdf built"
)

(
  cd paper_ko
  compile xelatex main main.tex
  shasum -a 256 main.tex references.bib apalike-doi.bst tables/*.tex figures/*.pdf main.pdf > main.pdf.sources.sha256
  rm -f main.aux main.log main.out main.blg main.toc
  echo "paper_ko: main.pdf built"
)
