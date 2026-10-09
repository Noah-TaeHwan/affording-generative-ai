#!/usr/bin/env bash
# Pre-release gate. Fails if a manuscript PDF was not rebuilt after its sources changed,
# if the anonymised review copy carries identifying strings, if the README points to a bundled file that
# does not exist, or (when the separately distributed submission/ folder is present) if it is incomplete or stale:
# figure files under their ordered names, the anonymised replication package (code/54_anonymised_package.py), the
# hand-written files, and identifying strings in the anonymised PDF, LaTeX source and package.
# The strings are listed in verification/identifying_strings.txt (one per line, case-insensitive). When submission/ is present,
# the deposited package must also be free of the journal names and submission history listed in submission/journal_strings.txt.
set -uo pipefail
cd "$(dirname "$0")"
fail=0

ID_FILE=verification/identifying_strings.txt
id_pattern() {  # grep -E alternation of the strings in $ID_FILE, regular-expression metacharacters escaped
  tr -d '\r' < "$ID_FILE" | sed -e '/^[[:space:]]*$/d' -e 's/[].[\*^$+?(){}|]/\\&/g' | paste -sd'|' -
}
pattern=""
if [ -f "$ID_FILE" ]; then
  pattern=$(id_pattern)
fi
if [ -z "$pattern" ]; then
  echo "FAIL $ID_FILE is missing or empty"; fail=1
fi

for d in paper_en paper_ko; do
  m="$d/main.pdf.sources.sha256"
  if [ ! -f "$m" ]; then echo "FAIL $d: no build record; run build_papers.sh"; fail=1; continue; fi
  (cd "$d" && shasum -a 256 -c --quiet main.pdf.sources.sha256) \
    || { echo "FAIL $d: PDFs are stale (sources changed after the last build); run build_papers.sh"; fail=1; }
  if [ "$d" = paper_en ]; then
    files=$(cd "$d" && ls main.tex titlepage.tex references.bib apalike-doi.bst tables/*.tex figures/*.pdf main_anon.pdf titlepage.pdf)
  else
    files=$(cd "$d" && ls main.tex references.bib apalike-doi.bst tables/*.tex figures/*.pdf)
  fi
  for f in $files; do
    grep -q "  $f\$" "$m" || { echo "FAIL $d: $f is not covered by the build record; run build_papers.sh"; fail=1; }
  done
done

# the anonymised copy must not identify the author
if command -v pdftotext >/dev/null 2>&1 && [ -n "$pattern" ]; then
  anon_text=$(pdftotext paper_en/main_anon.pdf - 2>/dev/null || true)
  if grep -q -i -E "$pattern" <<<"$anon_text"; then
    echo "FAIL paper_en: identifying string found in main_anon.pdf"; fail=1
  fi
fi

# files the README tells readers to open or run
for f in run_all.sh run_revision.sh build_papers.sh check_release.sh requirements.txt LICENSE.txt \
         paper_en/main.pdf paper_en/main_anon.pdf paper_en/titlepage.pdf paper_ko/main.pdf \
         extensions/requirements_revision.txt verification/README.md verification/prose_number_audit.py \
         verification/en_ko_number_check.py verification/identifying_strings.txt \
         code/53_flatten_submission.py code/54_anonymised_package.py; do
  [ -e "$f" ] || { echo "FAIL README refers to missing $f"; fail=1; }
done

# the submission folder is distributed separately from the deposited package; when present it must be complete
# and its PDFs must be the ones in paper_en
if [ -d submission ]; then
  for f in Manuscript_anonymised.pdf Manuscript_identified.pdf Title_Page.pdf Title_Page.tex Highlights.txt \
           Cover_Letter.md Cover_Letter.docx Vitae_draft.docx Declarations.md README.md \
           latex_source_anonymised/manuscript_anonymised.tex latex_source_identified/manuscript_identified.tex; do
    [ -e "submission/$f" ] || { echo "FAIL submission/$f missing; run code/53_flatten_submission.py (hand-written files: add them)"; fail=1; }
  done
  cmp -s paper_en/main_anon.pdf submission/Manuscript_anonymised.pdf || { echo "FAIL submission/Manuscript_anonymised.pdf differs from paper_en/main_anon.pdf"; fail=1; }
  cmp -s paper_en/main.pdf submission/Manuscript_identified.pdf || { echo "FAIL submission/Manuscript_identified.pdf differs from paper_en/main.pdf"; fail=1; }
  # the title page of the submission is paper_en/titlepage.tex with the full postal address (submission/postal_address.txt) inserted
  python3 code/53_flatten_submission.py --check-titlepage || fail=1
  if [ -f submission/postal_address.txt ]; then
    addr=$(head -n 1 submission/postal_address.txt | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    key=${addr:0:20}  # the address must not be in the deposited package: it is looked for by its first 20 characters
    if [ -z "$key" ]; then
      echo "FAIL submission/postal_address.txt is empty"; fail=1
    else
      if command -v pdftotext >/dev/null 2>&1; then
        pdftotext submission/Title_Page.pdf - 2>/dev/null | grep -q "Postal address" \
          || { echo "FAIL submission/Title_Page.pdf does not contain \"Postal address\""; fail=1; }
        for pdf in paper_en/*.pdf; do
          if pdftotext "$pdf" - 2>/dev/null | tr -s '[:space:]' ' ' | grep -q -F -- "$key"; then
            echo "FAIL $pdf contains the postal address (the deposited package carries the city only)"; fail=1
          fi
        done
      fi
      leaks=$(grep -rlF -- "$key" paper_en code data output extensions checks verification README.md LICENSE.txt CITATION.cff paper_ko 2>/dev/null || true)
      [ -z "$leaks" ] || { echo "FAIL the postal address is in the deposited package: $leaks"; fail=1; }
    fi
  fi
  if [ -f submission/Highlights.txt ]; then
    awk 'length($0) > 87 { bad=1 } END { exit bad }' submission/Highlights.txt \
      || { echo "FAIL submission/Highlights.txt: a bullet exceeds 85 characters"; fail=1; }
  fi
  # the deposited package (everything outside submission/) names no journal and carries no submission history: the
  # journal names, special-issue labels and manuscript-number prefixes are listed in submission/journal_strings.txt
  if [ -f submission/journal_strings.txt ]; then
    jpattern=$(tr -d '\r' < submission/journal_strings.txt | sed -e '/^[[:space:]]*$/d' -e 's/[].[\*^$+?(){}|]/\\&/g' | paste -sd'|' -)
    if [ -n "$jpattern" ]; then
      jleaks=$(grep -rIl -i -E --exclude-dir=submission --exclude-dir=__pycache__ -- "$jpattern" . 2>/dev/null | sed 's#^\./##' || true)
      [ -z "$jleaks" ] || { echo "FAIL journal names or submission history in the deposited package: $(echo $jleaks)"; fail=1; }
      if command -v pdftotext >/dev/null 2>&1; then
        for pdf in $(find . -name '*.pdf' -not -path './submission/*'); do
          if pdftotext "$pdf" - 2>/dev/null | grep -q -i -E -- "$jpattern"; then
            echo "FAIL journal names or submission history in the text of $pdf"; fail=1
          fi
        done
      fi
    fi
  fi

  # figure files under ordered names (Figure_1.pdf ... Figure_N.pdf, Figure_C1.pdf) and their index
  for f in figures/Figure_1.pdf figures/FIGURE_INDEX.txt; do
    [ -e "submission/$f" ] || { echo "FAIL submission/$f missing; run code/53_flatten_submission.py"; fail=1; }
  done
  python3 code/53_flatten_submission.py --check-figures || fail=1

  # the anonymised replication package: complete, nothing excluded inside, no identifying string in any text file, current
  if [ -e submission/Replication_package_anonymised.zip ]; then
    python3 code/54_anonymised_package.py --check submission/Replication_package_anonymised.zip || { echo "FAIL submission/Replication_package_anonymised.zip (see above); run code/54_anonymised_package.py"; fail=1; }
  else
    echo "FAIL submission/Replication_package_anonymised.zip missing; run code/54_anonymised_package.py"; fail=1
  fi

  # the anonymised files uploaded for review must not identify the author
  if [ -n "$pattern" ]; then
    if command -v pdftotext >/dev/null 2>&1 && [ -f submission/Manuscript_anonymised.pdf ]; then
      sub_text=$(pdftotext submission/Manuscript_anonymised.pdf - 2>/dev/null || true)
      if grep -q -i -E "$pattern" <<<"$sub_text"; then
        echo "FAIL submission/Manuscript_anonymised.pdf: identifying string found"; fail=1
      fi
    fi
    if [ -f submission/latex_source_anonymised/manuscript_anonymised.tex ] \
       && grep -q -i -E "$pattern" submission/latex_source_anonymised/manuscript_anonymised.tex; then
      echo "FAIL submission/latex_source_anonymised/manuscript_anonymised.tex: identifying string found"; fail=1
    fi
  fi
fi
for f in $(grep -o '`code/[A-Za-z0-9_.]*`' README.md | tr -d '`' | sort -u); do
  [ -e "$f" ] || { echo "FAIL README refers to missing $f"; fail=1; }
done

[ "$fail" -eq 0 ] && echo "release check passed"
exit "$fail"
