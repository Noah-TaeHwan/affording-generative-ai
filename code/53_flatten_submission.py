"""
53_flatten_submission.py -- self-contained LaTeX sources and figure files for the submission folder.

Editorial systems compile a single .tex file that must not depend on \\input files or on running BibTeX.
This script writes, for the anonymised review copy and for the identified copy:
  * a flattened .tex file in which every \\input{tables/...} is replaced by the table file's contents,
    \\bibliography{...} is replaced by the compiled .bbl, the \\ifanon switch is resolved, and figures are
    referenced by bare file names (these folders keep the fig_*_en.pdf names the flattened .tex refers to);
  * copies of the figure PDFs next to it.
Each flattened file is then compiled with pdflatex (three passes) in a scratch directory and its text is
compared with the text of the corresponding PDF built by build_papers.sh, so that the uploaded source is
known to reproduce the reviewed PDF.
The anonymised source is also checked against verification/identifying_strings.txt (full-line comments that
carry such a string are dropped; any other occurrence stops the script).

submission/figures/ holds the figure files for the editorial system under logical, ordered names: the figures are
numbered by order of appearance of \\includegraphics in paper_en/main.tex -- Figure_1.pdf, Figure_2.pdf, ... for figures
before \\appendix, and Figure_<L><k>.pdf (Figure_C1.pdf) for the k-th figure of appendix section L (L = A, B, ... counts the
\\section commands after \\appendix). The mapping is printed and written to submission/figures/FIGURE_INDEX.txt.

submission/Title_Page.tex is paper_en/titlepage.tex with (i) the line that starts with %%POSTAL_ADDRESS%% replaced by
\\textbf{Postal address:} <first line of submission/postal_address.txt>.\\\\ (the line is deleted if that file does not
exist) and (ii) every block between "%%JOURNAL_BLOCK_BEGIN name%%" and "%%JOURNAL_BLOCK_END name%%" lines replaced by the
block of the same name in submission/title_page_journal.tex (the journal name, issue label, article type and submission
history; if that file does not exist the marker lines are dropped and the neutral text between them is kept). It is compiled
here (pdflatex, twice) to submission/Title_Page.pdf, which must be one page without overfull boxes. The deposited package
carries the city only and names no journal (paper_en/titlepage.tex); only this script and check_release.sh read the two files.

Usage: python code/53_flatten_submission.py        (run build_papers.sh first)
       python code/53_flatten_submission.py --check-figures     (is submission/figures/ current? used by check_release.sh)
       python code/53_flatten_submission.py --check-titlepage   (are Title_Page.tex/.pdf what this script would write now?)
The submission/ folder it fills is distributed as a separate archive and is not part of the deposited
replication package; the hand-written files in it (highlights, cover letter, declarations, README) are kept.
Output: submission/ (Manuscript_*.pdf, Title_Page.*, figures/, latex_source_anonymised/, latex_source_identified/)
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "paper_en"
OUT = ROOT / "submission"
IDFILE = ROOT / "verification" / "identifying_strings.txt"
POSTAL = OUT / "postal_address.txt"   # full postal address; kept in submission/ only, never in the deposited package
POSTAL_MARKER = "%%POSTAL_ADDRESS%%"  # line of paper_en/titlepage.tex that stands for the address
JOURNAL = OUT / "title_page_journal.tex"  # journal-specific blocks of the title page; kept in submission/ only
BLOCK_BEGIN, BLOCK_END = "%%JOURNAL_BLOCK_BEGIN ", "%%JOURNAL_BLOCK_END "  # "...BEGIN name%%" / "...END name%%"


def resolve_ifanon(src, anon):
    """Resolve \\ifanon ... \\else ... \\fi blocks (they are not nested in main.tex)."""
    # drop the toggle definition and its comment line first, so the pattern below only sees the two branches
    src = re.sub(r"^% Anonymised review copy:.*$\n", "", src, flags=re.M)
    src = re.sub(r"^\\ifdefined\\ifanon.*$\n", "", src, flags=re.M)
    pat = re.compile(r"\\ifanon\n(.*?)\\else\n(.*?)\\fi\n", re.S)

    def pick(m):
        return m.group(1) if anon else m.group(2)

    src, n = pat.subn(pick, src)
    assert n >= 1 and "\\ifanon" not in src, "unresolved \\ifanon block in main.tex (found %d)" % n
    return src


def identifying_strings():
    """Strings that must not occur in anonymised material (one per line, case-insensitive); empty if the file is absent."""
    if not IDFILE.exists():
        return []
    return [l.strip() for l in IDFILE.read_text(encoding="utf-8").splitlines() if l.strip()]


def drop_identifying_comments(src):
    """Anonymised source: drop full-line LaTeX comments that carry an identifying string, then insist none is left."""
    strings = [t.lower() for t in identifying_strings()]
    if not strings:
        return src
    kept, dropped = [], 0
    for line in src.split("\n"):
        if line.lstrip().startswith("%") and any(t in line.lower() for t in strings):
            dropped += 1
            continue
        kept.append(line)
    src = "\n".join(kept)
    left = sorted({t for t in strings if t in src.lower()})
    if left:
        raise SystemExit("anonymised source still contains identifying string(s): " + ", ".join(left))
    if dropped:
        print(f"anonymised source: dropped {dropped} comment line(s) carrying an identifying string")
    return src


def _braced(src, i):
    """Text of the {...} group whose opening brace is at src[i]; returns (text, index after the closing brace)."""
    assert src[i] == "{"
    depth, j = 0, i
    while j < len(src):
        c = src[j]
        if c == "\\" and j + 1 < len(src):
            j += 2
            continue
        depth += c == "{"
        depth -= c == "}"
        j += 1
        if depth == 0:
            return src[i + 1:j - 1], j
    raise SystemExit("unbalanced braces in main.tex")


def caption_start(caption, nwords=12):
    """First words of a figure caption as plain text (first sentence, at most nwords words)."""
    t = re.sub(r"\\label\{[^}]*\}", "", caption)
    t = t.replace("\\$", "$").replace("\\%", "%").replace("\\&", "&").replace("~", " ").replace("\\\\", " ")
    for _ in range(3):  # \emph{x}, \textbf{x}, \textit{x}, ... -> x
        t = re.sub(r"\\(?:emph|textbf|textit|textrm|textsc|mathrm|mbox)\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\[A-Za-z]+\*?", "", t).replace("{", "").replace("}", "")
    t = " ".join(t.split())
    m = re.search(r"(?<=[a-z0-9\)])\.(?:\s|$)", t)  # end of the first sentence (not "U.S. ")
    sentence = t[:m.start()] if m else t.rstrip(".")
    words = sentence.split()
    return " ".join(words[:nwords]) + (" ..." if len(words) > nwords else "")


def figure_order():
    """Figures in order of appearance in paper_en/main.tex (comments ignored).

    Returns [(new_name, source_pdf_name, label, caption_start)] with new_name Figure_<n>.pdf before \\appendix and
    Figure_<L><k>.pdf in appendix section L (L = A, B, ... counts the \\section commands after \\appendix)."""
    raw = (P / "main.tex").read_text(encoding="utf-8")
    src = "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in raw.splitlines())
    token = re.compile(r"\\appendix\b|\\section(?!\*)(?:\[[^\]]*\])?(?=\{)|\\begin\{figure\*?\}|\\end\{figure\*?\}"
                       r"|\\caption(?:\[[^\]]*\])?(?=\{)|\\includegraphics(?:\[[^\]]*\])?(?=\{)")
    out, appendix, letters, n_main, per_letter = [], False, 0, 0, {}
    env = None  # inside \begin{figure}: {"files": [(file, appendix letter or None)], "caption": text or None}

    def emit(fname, caption, where):
        nonlocal n_main
        if where is None:
            n_main += 1
            new, label = f"Figure_{n_main}.pdf", f"Figure {n_main}"
        else:
            per_letter[where] = per_letter.get(where, 0) + 1
            new, label = f"Figure_{where}{per_letter[where]}.pdf", f"Figure {where}.{per_letter[where]}"
        out.append((new, fname, label, caption_start(caption) if caption else ""))

    pos = 0
    while True:
        m = token.search(src, pos)
        if not m:
            break
        t = m.group(0)
        pos = m.end()
        if t == "\\appendix":
            appendix = True
        elif t.startswith("\\section"):
            letters += appendix
        elif t.startswith("\\begin{figure"):
            env = {"files": [], "caption": None}
        elif t.startswith("\\end{figure"):
            for fname, where in env["files"]:
                emit(fname, env["caption"], where)
            env = None
        elif t.startswith("\\caption"):
            text, pos = _braced(src, pos)
            if env is not None:
                env["caption"] = text
        else:  # \includegraphics
            fname, pos = _braced(src, pos)
            fname = Path(fname).name
            if not Path(fname).suffix:
                fname += ".pdf"
            where = None
            if appendix:
                if letters == 0:
                    raise SystemExit("figure after \\appendix but before the first appendix \\section")
                where = chr(ord("A") + letters - 1)
            if env is not None:
                env["files"].append((fname, where))
            else:
                emit(fname, None, where)
    names = [o[0] for o in out]
    srcs = [o[1] for o in out]
    if len(set(srcs)) != len(srcs):
        raise SystemExit("a figure file is included twice in main.tex: " + ", ".join(sorted({x for x in srcs if srcs.count(x) > 1})))
    assert len(set(names)) == len(names)
    for new, fname, _, _ in out:
        if not (P / "figures" / fname).exists():
            raise SystemExit(f"main.tex includes figures/{fname}, which does not exist")
    return out


def index_lines(order):
    return [f"{new} = {fname} ({label}: {start})" if start else f"{new} = {fname} ({label})"
            for new, fname, label, start in order]


def check_figures():
    """Is submission/figures/ what main() would write now? (used by check_release.sh); returns an exit status."""
    figdir = OUT / "figures"
    order = figure_order()
    problems = []
    expected = {o[0] for o in order} | {"FIGURE_INDEX.txt"}
    actual = {f.name for f in figdir.iterdir()} if figdir.is_dir() else set()
    problems += [f"submission/figures/{n} missing" for n in sorted(expected - actual)]
    problems += [f"submission/figures/{n} is not a Figure_* file of the current manuscript" for n in sorted(actual - expected)]
    for new, fname, _, _ in order:
        f = figdir / new
        if f.exists() and f.read_bytes() != (P / "figures" / fname).read_bytes():
            problems.append(f"submission/figures/{new} differs from paper_en/figures/{fname}")
    idx = figdir / "FIGURE_INDEX.txt"
    if idx.exists() and idx.read_text(encoding="utf-8").splitlines() != index_lines(order):
        problems.append("submission/figures/FIGURE_INDEX.txt does not match the order of figures in paper_en/main.tex")
    for p in problems:
        print("FAIL " + p + "; run code/53_flatten_submission.py", file=sys.stderr)
    return 1 if problems else 0


def postal_address():
    """First line of submission/postal_address.txt, stripped; None if the file does not exist."""
    if not POSTAL.exists():
        return None
    lines = POSTAL.read_text(encoding="utf-8").splitlines()
    address = lines[0].strip() if lines else ""
    if not address:
        raise SystemExit("submission/postal_address.txt is empty")
    return address


def journal_blocks(text, source):
    """{name: [lines]} of the %%JOURNAL_BLOCK_BEGIN name%% ... %%JOURNAL_BLOCK_END name%% blocks of a text (markers excluded)."""
    blocks, name, body = {}, None, []
    for line in text.splitlines(keepends=True):
        s = line.strip()
        if s.startswith(BLOCK_BEGIN) and s.endswith("%%"):
            if name is not None:
                raise SystemExit(f"{source}: block {name!r} is not closed before {s}")
            name, body = s[len(BLOCK_BEGIN):-2].strip(), []
            if name in blocks:
                raise SystemExit(f"{source}: block {name!r} appears twice")
        elif s.startswith(BLOCK_END) and s.endswith("%%"):
            if name is None or s[len(BLOCK_END):-2].strip() != name:
                raise SystemExit(f"{source}: unexpected {s}")
            blocks[name], name = body, None
        elif name is not None:
            body.append(line)
    if name is not None:
        raise SystemExit(f"{source}: block {name!r} is not closed")
    return blocks


def apply_journal_blocks(lines):
    """Replace the marked blocks of paper_en/titlepage.tex by those of submission/title_page_journal.tex (or unmark them)."""
    journal = journal_blocks(JOURNAL.read_text(encoding="utf-8"), "submission/title_page_journal.tex") if JOURNAL.exists() else None
    own = journal_blocks("".join(lines), "paper_en/titlepage.tex")
    if journal is not None:
        missing = sorted(set(journal) - set(own))
        if missing:
            raise SystemExit(f"submission/title_page_journal.tex has blocks that paper_en/titlepage.tex lacks: {missing}")
    out, name = [], None
    for line in lines:
        s = line.strip()
        if s.startswith(BLOCK_BEGIN) and s.endswith("%%"):
            name = s[len(BLOCK_BEGIN):-2].strip()
            if journal is not None and name in journal:
                out.extend(journal[name])
        elif s.startswith(BLOCK_END) and s.endswith("%%"):
            name = None
        elif name is None or journal is None or name not in journal:
            out.append(line)
    return out


def titlepage_source():
    """Expected submission/Title_Page.tex: paper_en/titlepage.tex with its %%POSTAL_ADDRESS%% line and journal blocks replaced."""
    src = (P / "titlepage.tex").read_text(encoding="utf-8")
    address = postal_address()
    lines = apply_journal_blocks(src.splitlines(keepends=True))
    marked = [i for i, l in enumerate(lines) if l.startswith(POSTAL_MARKER)]
    if len(marked) > 1:
        raise SystemExit(f"paper_en/titlepage.tex has {len(marked)} {POSTAL_MARKER} lines (one expected)")
    if address is not None and not marked:
        raise SystemExit(f"submission/postal_address.txt exists but paper_en/titlepage.tex has no {POSTAL_MARKER} line")
    if "%" in (address or ""):
        raise SystemExit("submission/postal_address.txt contains an unescaped % (LaTeX would drop the rest of the line)")
    for i in marked:
        lines[i] = "" if address is None else "\\textbf{Postal address:} " + address.rstrip(".") + ".\\\\\n"
    return "".join(lines)


def compile_titlepage(tex, pdf_out=None):
    """Compile Title_Page.tex source text (pdflatex, twice; SOURCE_DATE_EPOCH respected, default as in build_papers.sh).

    Fails unless the result is one page without overfull boxes. Returns the text of the PDF (pdftotext -layout)."""
    env = dict(os.environ)
    env.setdefault("SOURCE_DATE_EPOCH", "1790726400")
    env.setdefault("FORCE_SOURCE_DATE", "1")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "Title_Page.tex").write_text(tex, encoding="utf-8")
        for _ in range(2):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "Title_Page.tex"],
                               cwd=tmp, capture_output=True, text=True, env=env)
            if r.returncode != 0:
                errors = [l for l in r.stdout.splitlines() if l.startswith(("!", "l."))]
                raise SystemExit("Title_Page.tex does not compile (is the postal address LaTeX-safe? escape & # _ yourself):\n"
                                 + "\n".join(errors[:6]))
        log = (tmp / "Title_Page.log").read_text(errors="replace")
        if "Overfull \\hbox" in log:
            raise SystemExit("Title_Page.tex: overfull box in the title page\n" + "\n".join(
                l for l in log.splitlines() if l.startswith("Overfull")))
        if "undefined references" in log or "Rerun to get" in log:
            raise SystemExit("Title_Page.tex: unresolved references")
        info = subprocess.run(["pdfinfo", str(tmp / "Title_Page.pdf")], capture_output=True, text=True).stdout
        pages = [l.split()[1] for l in info.splitlines() if l.startswith("Pages")][0]
        if pages != "1":
            raise SystemExit(f"Title_Page.pdf has {pages} pages (one expected)")
        text = subprocess.run(["pdftotext", "-layout", str(tmp / "Title_Page.pdf"), "-"], capture_output=True, text=True).stdout
        address = postal_address()
        flat = lambda t: re.sub(r"\s+", "", unicodedata.normalize("NFKC", t))
        if address is not None and flat(address.rstrip(".")) not in flat(text):
            raise SystemExit("Title_Page.pdf does not contain the postal address from submission/postal_address.txt")
        if pdf_out is not None:
            shutil.copy(tmp / "Title_Page.pdf", pdf_out)
    return text


def check_titlepage():
    """Are submission/Title_Page.tex and .pdf what main() would write now? (used by check_release.sh); exit status."""
    tex_file, pdf_file = OUT / "Title_Page.tex", OUT / "Title_Page.pdf"
    problems = []
    expected = titlepage_source()
    if not tex_file.exists() or tex_file.read_text(encoding="utf-8") != expected:
        problems.append("submission/Title_Page.tex differs from paper_en/titlepage.tex with the postal address and journal blocks inserted")
    elif pdf_file.exists():
        text = compile_titlepage(expected)
        shown = subprocess.run(["pdftotext", "-layout", str(pdf_file), "-"], capture_output=True, text=True).stdout
        if text != shown:
            problems.append("submission/Title_Page.pdf is not the compiled submission/Title_Page.tex")
    if not pdf_file.exists():
        problems.append("submission/Title_Page.pdf missing")
    for p in problems:
        print("FAIL " + p + "; run code/53_flatten_submission.py", file=sys.stderr)
    return 1 if problems else 0


def flatten(anon):
    src = (P / "main.tex").read_text(encoding="utf-8")
    src = resolve_ifanon(src, anon)
    if anon:
        src = drop_identifying_comments(src)
    # inline table files
    src = re.sub(r"\\(?:tabinput|input)\{(tables/[^}]+)\}",
                 lambda m: "% --- " + m.group(1) + "\n" + (P / m.group(1)).read_text(encoding="utf-8").rstrip() + "\n% --- end "
                 + m.group(1), src)
    # inline the compiled bibliography
    bbl = (P / ("main_anon.bbl" if anon else "main.bbl")).read_text(encoding="utf-8")
    src = re.sub(r"\\bibliographystyle\{[^}]+\}\n", "", src)
    src = src.replace("\\bibliography{references}", bbl.rstrip())
    # figures by bare file name
    src = src.replace("{figures/", "{")
    assert "\\tabinput{" not in src and "\\input{" not in src and "\\bibliography{" not in src and "\\ifanon" not in src
    return src


def compile_check(tex_dir, name, reference_pdf):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for f in tex_dir.iterdir():
            shutil.copy(f, tmp / f.name)
        for _ in range(3):
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"],
                               cwd=tmp, capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stdout[-3000:])
                raise SystemExit(f"{name}.tex does not compile standalone")
        log = (tmp / (name + ".log")).read_text(errors="replace")
        if "undefined references" in log or "Rerun to get" in log:
            raise SystemExit(f"{name}.tex: unresolved references")
        txt = subprocess.run(["pdftotext", "-layout", str(tmp / (name + ".pdf")), "-"], capture_output=True, text=True).stdout
        ref = subprocess.run(["pdftotext", "-layout", str(reference_pdf), "-"], capture_output=True, text=True).stdout
        if txt != ref:
            raise SystemExit(f"{name}.tex: text of the standalone build differs from {reference_pdf.name}")
        pages = subprocess.run(["pdfinfo", str(tmp / (name + ".pdf"))], capture_output=True, text=True).stdout
        print(f"{name}.tex: compiles standalone; text identical to {reference_pdf.name}; "
              + [l for l in pages.splitlines() if l.startswith("Pages")][0])


def main():
    for anon, folder, name, ref in [(True, "latex_source_anonymised", "manuscript_anonymised", "main_anon.pdf"),
                                    (False, "latex_source_identified", "manuscript_identified", "main.pdf")]:
        d = OUT / folder
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        src = flatten(anon)
        (d / (name + ".tex")).write_text(src, encoding="utf-8")
        for fig in sorted((P / "figures").glob("*_en.pdf")):
            if fig.name in src:  # only the figures the manuscript includes
                shutil.copy(fig, d / fig.name)
        compile_check(d, name, P / ref)
    # copies of the PDFs, the title page and the figure files for upload
    shutil.copy(P / "main_anon.pdf", OUT / "Manuscript_anonymised.pdf")
    shutil.copy(P / "main.pdf", OUT / "Manuscript_identified.pdf")
    tp = titlepage_source()
    (OUT / "Title_Page.tex").write_text(tp, encoding="utf-8")
    compile_titlepage(tp, OUT / "Title_Page.pdf")
    print("Title_Page.tex" + (" (with postal address)" if postal_address() else "") + " compiled to Title_Page.pdf: one page, no overfull box")
    figdir = OUT / "figures"
    if figdir.exists():
        shutil.rmtree(figdir)
    figdir.mkdir()
    order = figure_order()
    print("figure files for upload (order of appearance in paper_en/main.tex):")
    for new, fname, label, start in order:
        shutil.copy(P / "figures" / fname, figdir / new)
    index = index_lines(order)
    (figdir / "FIGURE_INDEX.txt").write_text("\n".join(index) + "\n", encoding="utf-8")
    for line in index:
        print("  " + line)
    print("flattened sources, PDFs, title page and figures written to", OUT)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check-figures":
        sys.exit(check_figures())
    if len(sys.argv) > 1 and sys.argv[1] == "--check-titlepage":
        sys.exit(check_titlepage())
    main()
