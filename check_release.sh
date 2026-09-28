#!/usr/bin/env bash
# Pre-release gate. Fails if a manuscript PDF was not rebuilt after its sources changed,
# or if the README points to a bundled file that does not exist.
set -uo pipefail
cd "$(dirname "$0")"
fail=0

for d in paper_en paper_ko; do
  m="$d/main.pdf.sources.sha256"
  if [ ! -f "$m" ]; then echo "FAIL $d: no build record; run build_papers.sh"; fail=1; continue; fi
  (cd "$d" && shasum -a 256 -c --quiet main.pdf.sources.sha256) \
    || { echo "FAIL $d: main.pdf is stale (sources changed after the last build); run build_papers.sh"; fail=1; }
  for f in $(cd "$d" && ls main.tex references.bib tables/*.tex figures/*.pdf); do
    grep -q "  $f\$" "$m" || { echo "FAIL $d: $f is not covered by the build record; run build_papers.sh"; fail=1; }
  done
done

# files the README tells readers to open or run
for f in run_all.sh build_papers.sh check_release.sh requirements.txt LICENSE.txt verification/README.md; do
  [ -e "$f" ] || { echo "FAIL README refers to missing $f"; fail=1; }
done
for f in $(grep -o '`code/[A-Za-z0-9_.]*`' README.md | tr -d '`' | sort -u); do
  [ -e "$f" ] || { echo "FAIL README refers to missing $f"; fail=1; }
done

[ "$fail" -eq 0 ] && echo "release check passed"
exit "$fail"
