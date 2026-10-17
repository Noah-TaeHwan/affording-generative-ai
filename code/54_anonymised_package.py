"""
54_anonymised_package.py -- anonymised copy of the replication package for peer review (kept as a clean spare).

Builds submission/Replication_package_anonymised.zip (or the path given as the first argument) from the working
copy: a reproduction package that a reader can run (bash run_all.sh, then bash build_papers.sh) without learning who
the author is. Files at the package root of the zip (no enclosing folder).

Included : run_all.sh, run_revision.sh, build_papers.sh, requirements.txt, LICENSE.txt (author's name replaced),
           code/ (except this script), data/, output/, extensions/ (except zenodo_record.json), checks/,
           verification/prose_number_audit.py and verification/README.md, paper_en/ (main.tex with the \\ifanon switch
           resolved to the anonymised branch, tables/, figures/, references.bib, apalike-doi.bst), and a generated
           README_anonymised.md.
Excluded : paper_ko/, CITATION.cff, README.md, README_v1_8.md, check_release.sh, submission/, research/,
           verification/identifying_strings.txt (it carries the strings), extensions/zenodo_record.json, manuscript PDFs
           (main.pdf, main_anon.pdf, titlepage.pdf), titlepage.tex, .bbl files, build records, __pycache__, .DS_Store,
           and the files of the translated edition (*_ko.* figures and table bodies, *_ko.py, en_ko_number_check.py).
           This script is not shipped either: its redaction map carries the strings it removes.

Redaction. verification/identifying_strings.txt lists the strings (one per line, case-insensitive) that must not occur in
any text file of the zip. A file that decodes as UTF-8 and contains one of them is passed through the redaction map below
(author's name -> "the author", e-mail -> author@example.org, ORCID iD removed, archive DOI/URL and record number ->
placeholder, preprint number -> placeholder, city -> "Republic of Korea", earlier working title -> placeholder) and is
checked again; the Zenodo deposit's size and checksum are redacted as well. The script FAILS (exit 1, file and string listed)
if a listed string survives in any text file, or if any text file of the zip matches one of the forbidden patterns
(FORBIDDEN_WORDING: the author's surname in citation form, author-location phrases including the collection time zone,
review-history wording, the publisher's name). Independently of the listed strings, every text file passes through the
rewording map REWORD (the collection time zone "(UTC+9)" -> "(local time)") and the two web-store extracts of data/raw/web/
lose their local-time column (fetch_kst; fetch_utc stays), with the data README adjusted. Binary files are also searched
byte-wise; a hit there is reported as a warning.

Usage: python code/54_anonymised_package.py [out.zip]
       python code/54_anonymised_package.py --check [out.zip]   verify an existing zip (required members, no excluded
                                                                 member, no listed string in any text member, zip equal to
                                                                 a fresh build from the working copy); exit 1 on failure
Run build_papers.sh first (the zip carries no PDFs, but its sources must be the ones the PDFs were built from).
"""
import importlib.util
import os
import re
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDFILE = ROOT / "verification" / "identifying_strings.txt"
EXTRAFILE = ROOT / "submission" / "journal_strings.txt"  # journal names and manuscript-number prefixes; submission/ only
DEFAULT_OUT = ROOT / "submission" / "Replication_package_anonymised.zip"
THIS = Path(__file__).resolve()

TOP_FILES = ["run_all.sh", "run_revision.sh", "build_papers.sh", "requirements.txt", "LICENSE.txt"]
TREES = ["code", "data", "output", "extensions", "checks"]
VERIFICATION_FILES = ["prose_number_audit.py", "README.md"]
EXCLUDE_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints"}
EXCLUDE_NAMES = {".DS_Store", "zenodo_record.json", "main.pdf", "main_anon.pdf", "titlepage.pdf",
                 "main.pdf.sources.sha256"}
EXCLUDE_SUFFIXES = {".pyc", ".bbl"}
# members that must never appear in the zip (checked by --check)
FORBIDDEN = ["paper_ko/", "submission/", "research/", "CITATION.cff", "README.md", "README_v1_8.md", "check_release.sh",
             "extensions/zenodo_record.json", "verification/identifying_strings.txt", "code/54_anonymised_package.py",
             "paper_en/titlepage.tex", "paper_en/main.pdf", "paper_en/main_anon.pdf", "paper_en/titlepage.pdf",
             "paper_en/main.pdf.sources.sha256"]
REQUIRED = ["run_all.sh", "run_revision.sh", "build_papers.sh", "requirements.txt", "extensions/requirements_revision.txt",
            "LICENSE.txt", "README_anonymised.md", "code/20_analysis.py", "data/processed/country_panel.csv",
            "output/results.json", "extensions/AUDIT_REPORT.md", "checks/price_reliability.py",
            "verification/prose_number_audit.py", "verification/README.md", "paper_en/main.tex",
            "paper_en/references.bib", "paper_en/apalike-doi.bst"]

# --------------------------------------------------------------------------------------------- redaction map
PLACE_DOI = "[public archive DOI withheld for review]"
PLACE_REC = "[public archive record withheld for review]"
PLACE_PRE = "[preprint withheld for review]"
PLACE_TITLE = "[earlier working title withheld for review]"
CURRENT_TITLE = "Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced Across Countries"
# (label, regular expression, replacement, restricted to these paths / suffixes or None); applied in this order, case-insensitively
RULES = [
    # adaptations of single files
    ("licence: current title", r'"Affording Generative AI:[^"]*"', '"' + CURRENT_TITLE + '"', ("LICENSE.txt",)),
    ("manuscript header comment", r"(?m)^% Affording Generative AI -- ", "% ", ("paper_en/main.tex",)),
    ("licence: English edition only", r"English and Korean manuscript", "manuscript", ("LICENSE.txt",)),
    ("licence: English edition only", r" and paper_ko/", "", ("LICENSE.txt",)),
    ("verification record: list of strings", r"none of the strings `taehwan`, `orcid`, `noah\.taehwan`, `zenodo`, `paju`",
     "none of the author's identifying strings (name, ORCID iD, e-mail address, archive DOI, place of residence)",
     ("verification/README.md",)),
    # contact details and identifiers
    ("e-mail address", r"[A-Za-z0-9._%+\-]*(?:noah|taehwan)[A-Za-z0-9._%+\-]*@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
     "author@example.org", None),
    ("ORCID iD", r"(?:ORCID(?:\s+iD)?:?\s*)?(?:https?://)?(?:www\.)?orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]", "", None),
    ("ORCID iD", r"(?:ORCID(?:\s+iD)?:?\s*)?\b0009-0004-4111-4802\b", "", None),
    ("repository profile", r"(?:https?://)?(?:www\.)?github\.com/Noah-TaeHwan\S*", "[repository link withheld for review]", None),
    ("Zenodo DOI", r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?10\.5281/zenodo\.\d+", PLACE_DOI, None),
    ("Zenodo URL", r"(?:https?://)?(?:www\.)?zenodo\.org/\S*?(?=[.,;:)\]]*(?:\s|$))", PLACE_DOI, None),
    ("Zenodo record number", r"(zenodo_record['\"]?\s*:\s*)2300636\d", r"\1None", (".py",)),
    ("Zenodo record number", r"(zenodo_record['\"]?\s*:\s*)2300636\d", r"\1null", (".json",)),
    ("Zenodo record number", r"\b2300636[56]\b", PLACE_REC, None),
    ("Zenodo record number", r"\b23428432\b", PLACE_REC, None),
    ("Zenodo deposit size", r"(package_size_bytes['\"]?\s*:\s*)4449098", r"\1None", (".py",)),
    ("Zenodo deposit size", r"(package_size_bytes['\"]?\s*:\s*)4449098", r"\1null", (".json",)),
    ("Zenodo deposit size", r"4,449,098-byte file", "archive file", None),
    ("Zenodo deposit checksum", r"399295b8c6aefc9a4c2bea8790893872", "[checksum withheld for review]", None),
    ("preprint number", r"SSRN\s+(?:working\s+paper\s+)?7535900", PLACE_PRE, None),
    ("preprint number", r"(?:https?://)?(?:papers\.)?ssrn\.com/\S*7535900\S*", PLACE_PRE, None),
    ("preprint number", r"\b7535900\b", PLACE_PRE, None),
    ("earlier working title", r"Affording Generative AI(?: Across Countries)?(?::\s*Uniform Prices, Unequal Burdens"
     r"(?:, and the Two Margins of AI Diffusion)?)?", PLACE_TITLE, None),
    ("earlier working title", r"Affording_Generative_AI", "Manuscript", None),
    ("earlier project name", r"affording-genai(?:-replication)?", "replication", None),
    # names and places
    ("author name", r"Oh,\s*TaeHwan", "the author", None),
    ("author name", r"TaeHwan\s+Oh\b", "the author", None),
    ("author name", r"Noah-TaeHwan", "the author", None),
    ("author name", r"TaeHwan", "the author", None),
    ("author name", r"\bNoah\b", "the author", None),
    ("city", r"Paju(?:,\s*Gyeonggi-do)?(?:,\s*(?:South\s+Korea|Republic\s+of\s+Korea))?", "Republic of Korea", None),
]
COMPILED = [(lab, re.compile(pat, re.I), rep, only) for lab, pat, rep, only in RULES]
# patterns that must not survive in any text file of the zip, whether or not the file carries a listed string: the author's
# surname in citation form, author-location phrases and review-history wording (case-insensitive extended regular expressions)
# (the words are written with a bracketed letter so that this file does not itself match the patterns)
FORBIDDEN_WORDING = [("author surname in citation form", r"\bOh \(20"), ("author location", r"\bKST\b"), ("author location", r"Korea t[i]me"),
                     ("author location", r"Korean I[P]"), ("author location", r"Korea Standard T[i]me"), ("author location", r"UTC\+[9]"),
                     ("review history", r"ref[e]ree"),
                     ("review history", r"revision req[u]est"), ("review history", r"revision mat[r]ix"), ("review history", r"\bDR[0-9]{2}\b"),
                     ("review history", r"Second r[o]und"), ("review history", r"independent r[e]adings"), ("publisher", r"Elsev[i]er")]
FORBIDDEN_C = [(lab, re.compile(pat, re.I)) for lab, pat in FORBIDDEN_WORDING]
# rewording applied to EVERY text file (not only those with a listed string): the collection time zone of the audit notes
REWORD = [("collection time zone", re.compile(r"\((\d{4}-\d{2}-\d{2}), UTC\+9\)"), r"(\1, local time)"),
          ("collection time zone", re.compile(r" \(UTC\+9\)"), " (local time)"),
          ("collection time zone", re.compile(r"clock times are Korea Standard Time, UTC\+9"), "clock times are local time")]
LOCAL_TIME_CSV = {"data/raw/web/ms365_web_prices.csv", "data/raw/web/play_iap_ranges.csv"}   # lose their fetch_kst column
LOCAL_TIME_README = ("data/raw/web/README.md",
                     "| `fetch_utc`, `fetch_kst` | Time of the request (UTC, and the local time of the collection, UTC+9) |",
                     "| `fetch_utc` | Time of the request (UTC); the local-time column of the public extract is omitted in this copy |")


def reword(arcname, text):
    """Rewording and column removal that apply to every text file; returns (new text, [(label, count)])."""
    log = []
    if arcname in LOCAL_TIME_CSV:
        import csv, io
        rows = list(csv.reader(io.StringIO(text, newline="")))
        if rows and "fetch_kst" in rows[0]:
            j = rows[0].index("fetch_kst")
            out = io.StringIO()
            w = csv.writer(out, lineterminator="\r\n" if "\r\n" in text else "\n")
            for r in rows:
                w.writerow(r[:j] + r[j + 1:])
            text = out.getvalue()
            log.append(("local-time column removed", 1))
    if arcname == LOCAL_TIME_README[0] and LOCAL_TIME_README[1] in text:
        text = text.replace(LOCAL_TIME_README[1], LOCAL_TIME_README[2])
        text = text.replace("`fetch_utc`, `fetch_kst`, `archive_path`", "`fetch_utc`, `archive_path`")
        log.append(("local-time column removed", 1))
    for label, rx, rep in REWORD:
        text, n = rx.subn(rep, text)
        if n:
            log.append((label, n))
    return text, log


def applies(only, arcname):
    return only is None or any(arcname == o or arcname.endswith(o) for o in only)


def identifying_strings():
    if not IDFILE.exists():
        raise SystemExit(f"{IDFILE.relative_to(ROOT)} is missing: it lists the strings the package must not contain")
    out = [l.strip() for l in IDFILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not out:
        raise SystemExit(f"{IDFILE.relative_to(ROOT)} is empty")
    if EXTRAFILE.exists():  # the submission-only list of journal strings is scanned as well (never shipped)
        out += [l.strip() for l in EXTRAFILE.read_text(encoding="utf-8").splitlines() if l.strip() and l.strip() not in out]
    return out


def occurrences(text, strings):
    low = text.lower()
    return [s for s in strings if s.lower() in low]


def redact(arcname, text, strings):
    """Apply the redaction map to a text file that contains a listed string; returns (new text, [(label, count)])."""
    log = []
    for label, rx, rep, only in COMPILED:
        if not applies(only, arcname):
            continue
        text, n = rx.subn(rep, text)
        if n:
            log.append((label, n))
    return text, log


# --------------------------------------------------------------------------------------------- selection
def load_53():
    spec = importlib.util.spec_from_file_location("flatten_submission", ROOT / "code" / "53_flatten_submission.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def skip(path):
    return (path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES or korean_file(path)
            or any(part in EXCLUDE_DIRS for part in path.parts))


def korean_file(path):
    """Files that exist only for the translated edition (figures and table bodies with translated labels, the translation
    checks): they are not needed to reproduce the manuscript and would hint at the author's language."""
    return path.stem.endswith("_ko") or path.name == "en_ko_number_check.py" or path.name == "build_revision_tables_ko.py"


def walk(rel):
    base = ROOT / rel
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if p.is_file() and not p.is_symlink() and not skip(p.relative_to(ROOT)):
                yield p.relative_to(ROOT).as_posix(), p


def collect():
    """{arcname: bytes} of the files that go into the zip, before redaction (README_anonymised.md and main.tex included)."""
    files = {}
    for name in TOP_FILES:
        files[name] = (ROOT / name).read_bytes()
    for tree in TREES:
        for arc, p in walk(tree):
            if p.resolve() == THIS:
                continue
            files[arc] = p.read_bytes()
    for name in VERIFICATION_FILES:
        files["verification/" + name] = (ROOT / "verification" / name).read_bytes()
    for sub in ["tables", "figures"]:
        for arc, p in walk("paper_en/" + sub):
            files[arc] = p.read_bytes()
    for name in ["references.bib", "apalike-doi.bst"]:
        files["paper_en/" + name] = (ROOT / "paper_en" / name).read_bytes()
    main = (ROOT / "paper_en" / "main.tex").read_text(encoding="utf-8")
    files["paper_en/main.tex"] = load_53().resolve_ifanon(main, True).encode("utf-8")
    files["README_anonymised.md"] = README.encode("utf-8")
    return files


def decode_text(data):
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def process(files, strings):
    """Redact; returns (final files, redaction log {arcname: [(label, n)]}, binary warnings, number of text files)."""
    final, log, warnings, n_text, failures = {}, {}, [], 0, []
    low = [s.lower().encode("utf-8") for s in strings]
    for arc in sorted(files):
        data = files[arc]
        text = decode_text(data)
        if text is None:
            # binary files (PDF, PNG, zip): strings of three characters or fewer are not looked for, because compressed
            # data matches them by chance (the check of the text files below applies every string)
            hit = [s for s, b in zip(strings, low) if len(b) >= 4 and b in data.lower()]
            if hit:
                warnings.append((arc, hit))
            final[arc] = data
            continue
        n_text += 1
        changed = False
        text, rlog = reword(arc, text)
        if rlog:
            log[arc] = rlog
            changed = True
        if occurrences(text, strings):
            text, more = redact(arc, text, strings)
            log[arc] = log.get(arc, []) + more
            left = occurrences(text, strings)
            if left:
                failures.append((arc, left))
            changed = True
        if changed:
            data = text.encode("utf-8")
        final[arc] = data
    if failures:
        lines = [f"  {arc}: {', '.join(left)}" for arc, left in failures]
        raise SystemExit("identifying string(s) survive the redaction map:\n" + "\n".join(lines))
    forbidden = []
    for arc, data in final.items():
        text = decode_text(data)
        if text is None:
            continue
        hits = [f"{lab} ({pat.pattern})" for lab, pat in FORBIDDEN_C if pat.search(text)]
        if hits:
            forbidden.append((arc, hits))
    if forbidden:
        lines = [f"  {arc}: {'; '.join(h)}" for arc, h in forbidden]
        raise SystemExit("forbidden wording in the anonymised package (reword the source file):\n" + "\n".join(lines))
    return final, log, warnings, n_text


def zip_date_time():
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "1792108800"))
    return time.gmtime(max(epoch, 315532800))[:6]


def write_zip(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    dt = zip_date_time()
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc in sorted(files):
            info = zipfile.ZipInfo(arc, dt)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100755 if arc.endswith(".sh") else 0o100644) << 16
            z.writestr(info, files[arc], compresslevel=9)
    tmp.replace(path)


def build(out):
    strings = identifying_strings()
    files, log, warnings, n_text = process(collect(), strings)
    write_zip(out, files)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB): {len(files)} files, {n_text} text files scanned against "
          f"{len(strings)} identifying strings, 0 occurrences left")
    for arc in sorted(log):
        print(f"  redacted {arc}: " + "; ".join(f"{lab} x{n}" for lab, n in log[arc]))
    for arc, hit in warnings:
        print(f"  WARNING binary file {arc} contains byte sequence(s): {', '.join(hit)}", file=sys.stderr)
    return files


# --------------------------------------------------------------------------------------------- check
def check(zpath, fresh=True):
    problems = []
    strings = identifying_strings()
    with zipfile.ZipFile(zpath) as z:
        bad = z.testzip()
        if bad:
            problems.append(f"corrupt member {bad}")
        names = z.namelist()
        members = {n: z.read(n) for n in names if not n.endswith("/")}
    for f in FORBIDDEN:
        hits = [n for n in names if (n.startswith(f) if f.endswith("/") else n == f)]
        problems += [f"excluded member present: {n}" for n in hits]
    problems += [f"manuscript PDF or cache present: {n}" for n in names
                 if Path(n).name in EXCLUDE_NAMES - {"zenodo_record.json"} or Path(n).suffix in EXCLUDE_SUFFIXES
                 or "__pycache__" in n]
    problems += [f"file of the translated edition present: {n}" for n in names if korean_file(Path(n))]
    problems += [f"required member missing: {r}" for r in REQUIRED if r not in members]
    n_text = 0
    for n, data in members.items():
        text = decode_text(data)
        if text is None:
            continue
        n_text += 1
        left = occurrences(text, strings)
        if left:
            problems.append(f"{n}: contains {', '.join(left)}")
        hits = [lab for lab, pat in FORBIDDEN_C if pat.search(text)]
        if hits:
            problems.append(f"{n}: forbidden wording ({', '.join(sorted(set(hits)))})")
    if fresh:
        files, _, _, _ = process(collect(), strings)
        if set(files) != set(members):
            diff = sorted(set(files) ^ set(members))
            problems.append("stale: member list differs from a fresh build (" + ", ".join(diff[:8]) + (" ..." if len(diff) > 8 else "") + ")")
        else:
            changed = sorted(n for n in files if files[n] != members[n])
            if changed:
                problems.append("stale: differs from a fresh build: " + ", ".join(changed[:8]) + (" ..." if len(changed) > 8 else ""))
    if problems:
        print("anonymised package check FAILED:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    print(f"anonymised package check passed: {len(members)} files, {n_text} text files contain none of the "
          f"{len(strings)} identifying strings or of the {len(FORBIDDEN_C)} forbidden patterns" + ("; equal to a fresh build" if fresh else ""))
    return 0


# --------------------------------------------------------------------------------------------- README of the zip
README = """# Anonymised replication package

This archive is an anonymised copy of the replication package for the manuscript *Localised Entry, Global Frontier:
How Generative-AI Subscriptions Are Priced Across Countries*, supplied for peer review. It reproduces every table, figure
and in-text number of the manuscript from the frozen data extracts it contains. Names, contact details, persistent
identifiers, repository links and DOIs of the author were removed or replaced by neutral text, and the manuscript source
in `paper_en/main.tex` is the anonymised version (the switch that distinguishes the anonymised from the identified copy has
been resolved). The public, identified archive of the package is cited on the title page that accompanies the submission
and will be cited in the published version.

## How to run

Requirements: Python 3.11 and the packages in `requirements.txt`; for the manuscript, TeX Live with `pdflatex` and `bibtex`
(packages geometry, mathptmx, amsmath/amsthm, booktabs, threeparttable, tabularx, multirow, natbib, tikz, enumitem,
hyperref, xurl). No network access is needed: every script reads the frozen files in `data/`.

```bash
pip install -r requirements.txt
bash run_all.sh          # processed data, results, figures, table bodies, additional analyses and the prose-number audit
bash build_papers.sh     # compiles the anonymised manuscript (needs TeX Live): paper_en/main.pdf
```

`extensions/requirements_revision.txt` lists a second, also validated set of package versions (Python 3.12); install either
`requirements.txt` or that file, not both. `run_all.sh` takes a little over two minutes (the 300 split-half draws of `code/14_default_validation.py` are about 70 s of that) and `build_papers.sh` about one minute.
`build_papers.sh` stops if references are unresolved or a line runs into the margin by more than 5pt. Because
`paper_en/main.tex` is already anonymised, `paper_en/main_anon.pdf` is a copy of `paper_en/main.pdf`.

After the two commands, the regenerated `data/processed/`, `output/results.json`, `output/tables/`, `extensions/audit_output/`,
`checks/results/` and `paper_en/tables/` can be compared with the files shipped in this archive; they are byte-identical on
the platform used to prepare it. On other operating systems the CSV outputs can differ in the last printed digit
(floating-point formatting); `output/results.json` and the LaTeX tables, which are rounded, are unaffected. The figures use
the fonts Liberation Sans (English labels); where they are missing the scripts fall back to other fonts and the PDFs then look
slightly different. Randomness: the bootstrap in `code/20_analysis.py` (seed 20260927), the currency-block resampling in
`checks/price_reliability.py` (seed 20260930), the randomisation inference of `code/13_relative_prices.py` and the split-half
draws of `code/14_default_validation.py` (seed 20261016) and the permutation tests of `extensions/go_rollout_analysis.py` are seeded.

## What is in the archive

| Folder / file | Contents |
|---|---|
| `run_all.sh`, `run_revision.sh`, `build_papers.sh` | The pipeline: `run_all.sh` runs the baseline programs and then `run_revision.sh --analysis-only`; `build_papers.sh` compiles the manuscript |
| `requirements.txt`, `extensions/requirements_revision.txt` | Package versions used to produce the results |
| `code/` | Programs. Reproduction uses `09_appstore_prices.py`, `10_build_dataset.py`, `11_data_dictionary.py`, `20_analysis.py`, `30_figures.py`, `40_tables_tex.py`, the second-wave programs `09b_wave2_items.py` (item prices, the annual-as-monthly guard, de-duplication, item slopes, stability), `12_default_panel.py` (the platform's estimated price schedule and the deviations from it), `13_relative_prices.py` (within-firm relative prices, stacked regressions, cross-vendor references, the increment test), `14_default_validation.py`, `15_vintage_test.py`, `16_cross_channel.py`, `31_figures_wave2.py`, `41_tables_wave2.py` and `42_tables_relative.py` (with `wave2_common.py`). The download and scraping programs (`00_download_sources.sh`, `01`-`03`, `05`, `02b_scrape_wave2.py`) document how the frozen extracts in `data/raw/` were obtained and, like the reference check `06_verify_references.py`, are not run by the pipeline; `50_make_docx.py` writes an optional Word version of the manuscript; `53_flatten_submission.py` assembles the journal upload files from the public package and cannot run here |
| `data/raw/`, `data/processed/` | Frozen source extracts (World Bank indicators, Microsoft AI Diffusion data, Anthropic Economic Index country files, Google ATLAS, ITU price baskets, both App Store audit waves with the 30-app default panel (`appstore/`, `appstore_wave2/`), the Google Play and Microsoft web-store extracts (`web/`), exchange rates and six historical exchange-rate snapshots (`fx/`, `fx_hist/`), the dated ChatGPT Go rollout record) and the analysis panel and price files (`country_panel.csv`, `wave2_*.csv`) |
| `output/` | `results.json`, `results_wave2.json`, `tables/*.csv` (`W1`-`W15b` for the second wave), `figures/*.pdf, *.png` (the shipped results) |
| `paper_en/` | The anonymised manuscript: `main.tex`, `references.bib`, `apalike-doi.bst`, `tables/` (LaTeX table bodies written by the programs) and `figures/` |
| `extensions/` | Additional analyses: `audit_extensions.py` (clustered inference, sensitivities, headline re-checks), `figure_price_ratio.py`, `build_revision_tables.py`, `go_rollout_analysis.py` (design fixed in the script before the outcomes were computed, not externally registered), `policy_counterfactuals.py`, `figure_rollout.py`; outputs in `audit_output/`; `baseline_results_v1.8.json` (frozen baseline); `upstream_validation/` (provider-file re-download checks); `pricing_sources/` (capture record of the tariff change used in the manuscript); `AUDIT_REPORT.md` (audit-stage record). The files of the translated edition of the manuscript are not part of this archive |
| `checks/` | Plan-matching and currency-sample checks (`price_reliability.py`), the Go/Plus table (`build_matched_menu_table.py`), the numerical verification of the model in Appendix A (`verify_tier_model.py`, `sim_check.py` with its output `results/sim_output.txt`), the access-conditions field dictionary and protocol of Appendix G |
| `verification/` | `README.md` (record of the clean-room replication) and `prose_number_audit.py` (checks every number printed in the prose of `paper_en/main.tex` against the outputs; exit status 1 on any mismatch) |
| `LICENSE.txt` | Licence terms (see below) |

Not part of this archive: the title page, other-language editions of the manuscript and the submission files (they
are supplied separately), compiled manuscripts, the large Anthropic release files (about 450 MB) and the ITU workbook. The last
two are not read by `run_all.sh`; `code/00_download_sources.sh` re-downloads them at pinned versions so that the derived country
files can be rebuilt. `code/40_tables_tex.py` and `code/30_figures.py` also write table bodies and figures with translated labels
(`paper_ko/tables/`, `output/figures/*_ko.*`); nothing in this archive reads them.

## Data sources and provenance

All data are publicly available and the archive includes the inputs used by `run_all.sh`.

| Source | Version used | Licence | Files |
|---|---|---|---|
| World Development Indicators; Global Findex 2025; country classification FY2027 (World Bank API) | extracted 27 Sep 2026 (WDI last updated 13 Jul 2026) | CC BY 4.0 | `data/raw/wb/` |
| AI Diffusion dataset, AI User Share H1 2025-Q2 2026 (Microsoft AI Economy Institute) | commit 507c316 (20 Sep 2026) | MIT | `data/raw/ms_repo/data/AI_Diffusion_Q22026_Update.csv`; copy in `extensions/microsoft_pinned.csv` |
| Anthropic Economic Index, country level | commit 2ea58ff (26 Jun 2026) | data CC-BY, code MIT | derived files `data/raw/anthropic/anthropic_country_*.csv` |
| Google AI & Economy ATLAS v1.0 | April 2026 sample, published 23 Jul 2026 | see provider | `data/raw/google_atlas/` |
| ITU ICT Price Baskets 2008-2025 | December 2025 release | ITU terms (attribution) | derived CSVs in `data/raw/itu/` |
| App Store in-app purchase prices (Apple App Store product pages), wave 1: ChatGPT, Claude, Gemini | retrieved 27 Sep 2026 (UTC) | public web pages; factual data | `data/raw/appstore/appstore_iap_raw.jsonl` |
| App Store in-app purchase prices, wave 2: 34 apps and the 30-app default panel (page fingerprints included; the page archive is kept separately) | retrieved 16 Oct 2026 (UTC) | public web pages; factual data | `data/raw/appstore_wave2/` |
| Google Play in-app price ranges (12 apps, 30 countries) and Microsoft 365 web-store prices (57 countries) | retrieved 16 Oct 2026 (UTC) | public web pages; factual data | `data/raw/web/` |
| Historical exchange rates (currency-api snapshots, six dates Mar 2024-Oct 2026) | retrieved 16 Oct 2026 | provider terms | `data/raw/fx_hist/` |
| Exchange rates (ExchangeRate-API; cross-check: currency-api) | 27 Sep 2026 | provider terms | `data/raw/fx/` |
| OpenAI tariff change of 29 Sep 2026 | help-centre pages cited in the manuscript, retrieved 29-30 Sep 2026 | provider terms | `extensions/pricing_sources/` (the $500 fee is the only number used) |

The App Store scrape and the exchange rates are point-in-time snapshots; re-running `code/02_scrape_appstore_prices.py` today
would give different prices. Namibia's ISO2 code is the string `NA`, which pandas reads as missing by default; every script
therefore reads CSV files with `keep_default_na=False, na_values=[""]`.

## Licence

The code (`code/`, `extensions/*.py`, `checks/*.py`, `verification/*.py`, the shell scripts) is released under the MIT
License. Data compiled by the author (the App Store price extraction and the author's contributions to the processed files) are
released under Creative Commons Attribution 4.0 International (CC BY 4.0). Values taken from third-party sources remain subject
to the providers' licences. The manuscript text is copyright of the author, all rights reserved. The full text, with the
author's name replaced by "the author" for review, is in `LICENSE.txt`.
"""


def main():
    args = sys.argv[1:]
    if args and args[0] == "--check":
        zpath = Path(args[1]) if len(args) > 1 else DEFAULT_OUT
        if not zpath.exists():
            print(f"{zpath} does not exist; run python code/54_anonymised_package.py", file=sys.stderr)
            return 1
        return check(zpath)
    out = Path(args[0]) if args else DEFAULT_OUT
    build(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
