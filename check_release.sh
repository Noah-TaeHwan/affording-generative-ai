#!/usr/bin/env bash
# Pre-release gate. Fails if a manuscript PDF was not rebuilt after its sources changed,
# if the anonymised review copy carries identifying strings, if the README points to a bundled file that
# does not exist, or (when the separately distributed submission/ folder is present) if it is incomplete or stale.
set -uo pipefail
cd "$(dirname "$0")"
fail=0

for d in paper_en paper_ko; do
  m="$d/main.pdf.sources.sha256"
  if [ ! -f "$m" ]; then echo "FAIL $d: no build record; run build_papers.sh"; fail=1; continue; fi
  (cd "$d" && shasum -a 256 -c --quiet main.pdf.sources.sha256) \
    || { echo "FAIL $d: PDFs are stale (sources changed after the last build); run build_papers.sh"; fail=1; }
  if [ "$d" = paper_en ]; then
    files=$(cd "$d" && ls main.tex titlepage.tex references.bib apalike-doi.bst tables/*.tex figures/*.pdf main_anon.pdf titlepage.pdf)
  else
    files=$(cd "$d" && ls main.tex references.bib tables/*.tex figures/*.pdf)
  fi
  for f in $files; do
    grep -q "  $f\$" "$m" || { echo "FAIL $d: $f is not covered by the build record; run build_papers.sh"; fail=1; }
  done
done

# the anonymised copy must not identify the author
if command -v pdftotext >/dev/null 2>&1; then
  pdftotext paper_en/main_anon.pdf - | grep -q -i -E 'taehwan|orcid|noah\.taehwan|zenodo|paju' \
    && { echo "FAIL paper_en: identifying string found in main_anon.pdf"; fail=1; }
fi

# files the README tells readers to open or run
for f in run_all.sh run_revision.sh build_papers.sh check_release.sh requirements.txt LICENSE.txt \
         paper_en/main.pdf paper_en/main_anon.pdf paper_en/titlepage.pdf paper_ko/main.pdf \
         revision_audit/requirements_revision.txt verification/README.md verification/prose_number_audit.py \
         code/53_flatten_submission.py; do
  [ -e "$f" ] || { echo "FAIL README refers to missing $f"; fail=1; }
done

# the submission folder is distributed separately from the deposited package; when present it must be complete
# and its PDFs must be the ones in paper_en
if [ -d submission ]; then
  for f in Manuscript_anonymised.pdf Manuscript_identified.pdf Title_Page.pdf Title_Page.tex Highlights.txt \
           Cover_Letter.md Declarations.md README.md latex_source_anonymised/manuscript_anonymised.tex \
           latex_source_identified/manuscript_identified.tex; do
    [ -e "submission/$f" ] || { echo "FAIL submission/$f missing; run code/53_flatten_submission.py"; fail=1; }
  done
  cmp -s paper_en/main_anon.pdf submission/Manuscript_anonymised.pdf || { echo "FAIL submission/Manuscript_anonymised.pdf differs from paper_en/main_anon.pdf"; fail=1; }
  cmp -s paper_en/main.pdf submission/Manuscript_identified.pdf || { echo "FAIL submission/Manuscript_identified.pdf differs from paper_en/main.pdf"; fail=1; }
  cmp -s paper_en/titlepage.pdf submission/Title_Page.pdf || { echo "FAIL submission/Title_Page.pdf differs from paper_en/titlepage.pdf"; fail=1; }
  if [ -f submission/Highlights.txt ]; then
    awk 'length($0) > 87 { bad=1 } END { exit bad }' submission/Highlights.txt \
      || { echo "FAIL submission/Highlights.txt: a bullet exceeds 85 characters"; fail=1; }
  fi
fi
for f in $(grep -o '`code/[A-Za-z0-9_.]*`' README.md | tr -d '`' | sort -u); do
  [ -e "$f" ] || { echo "FAIL README refers to missing $f"; fail=1; }
done

[ "$fail" -eq 0 ] && echo "release check passed"
exit "$fail"
