#!/usr/bin/env bash
# Compile the manuscripts and record which sources each PDF was built from (checked by check_release.sh).
# Needs TeX Live: pdflatex (English), xelatex (Korean; fonts Liberation Serif and Noto Serif/Sans CJK KR), bibtex.
#
# paper_en: main.pdf (identified manuscript), main_anon.pdf (anonymised review copy, built from the same
#           main.tex with the \ifanon switch set) and titlepage.pdf (separate title page for double-anonymised review).
# paper_ko: main.pdf (Korean edition: translation of the English version 2.0 manuscript, same tables and figures).
# In the anonymised copy of the package (supplied for peer review) main.tex is already the anonymised version (no \ifanon
# switch left) and there is no title page or Korean edition: main.pdf is built and copied to main_anon.pdf, and the
# identifying-string check is skipped because verification/identifying_strings.txt is not part of that copy.
set -euo pipefail
cd "$(dirname "$0")"
# fixed timestamps make rebuilds byte-identical (override SOURCE_DATE_EPOCH for a new version)
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1790726400}" FORCE_SOURCE_DATE=1

# strings that must not occur in the anonymised copy: verification/identifying_strings.txt, one per line (case-insensitive);
# turned into a grep -E alternation with the regular-expression metacharacters escaped
ID_FILE="$PWD/verification/identifying_strings.txt"
id_pattern() {
  tr -d '\r' < "$ID_FILE" | sed -e '/^[[:space:]]*$/d' -e 's/[].[\*^$+?(){}|]/\\&/g' | paste -sd'|' -
}

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
  if grep -q -F '\ifanon' main.tex; then
    compile pdflatex main_anon '\newif\ifanon\anontrue\input{main.tex}'
  else
    cp main.pdf main_anon.pdf  # main.tex is already the anonymised version (switch resolved)
  fi
  tp_src=(); tp_pdf=()
  if [ -f titlepage.tex ]; then
    tp_src=(titlepage.tex); tp_pdf=(titlepage.pdf)
    pdflatex -interaction=nonstopmode -halt-on-error titlepage.tex >/dev/null || { tail -40 titlepage.log >&2; exit 1; }
    pdflatex -interaction=nonstopmode -halt-on-error titlepage.tex >/dev/null
  fi
  # the anonymised copy must not carry the author's name, contact details or repository links
  if [ -f "$ID_FILE" ]; then
    pattern=$(id_pattern)
    [ -n "$pattern" ] || { echo "paper_en: verification/identifying_strings.txt is empty" >&2; exit 1; }
    anon_text=$(pdftotext main_anon.pdf -)
    if grep -q -i -E "$pattern" <<<"$anon_text"; then
      echo "paper_en: identifying string found in main_anon.pdf" >&2; exit 1
    fi
  else
    echo "paper_en: verification/identifying_strings.txt not found (anonymised package); identifying-string check skipped"
  fi
  shasum -a 256 main.tex ${tp_src[@]+"${tp_src[@]}"} references.bib apalike-doi.bst tables/*.tex figures/*.pdf main.pdf main_anon.pdf ${tp_pdf[@]+"${tp_pdf[@]}"} > main.pdf.sources.sha256
  rm -f main.aux main.log main.out main.blg main.toc main_anon.aux main_anon.log main_anon.out main_anon.blg titlepage.aux titlepage.log titlepage.out
  if [ -f titlepage.tex ]; then
    echo "paper_en: main.pdf, main_anon.pdf and titlepage.pdf built"
  else
    echo "paper_en: main.pdf built (main_anon.pdf is a copy; anonymised package without title page)"
  fi
)

if [ -f paper_ko/main.tex ]; then
(
  cd paper_ko
  compile xelatex main main.tex
  shasum -a 256 main.tex references.bib apalike-doi.bst tables/*.tex figures/*.pdf main.pdf > main.pdf.sources.sha256
  rm -f main.aux main.log main.out main.blg main.toc
  echo "paper_ko: main.pdf built"
)
else
  echo "paper_ko: no Korean edition in this package; skipped"
fi
