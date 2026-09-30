"""
53_flatten_submission.py -- self-contained LaTeX sources for journal upload.

Editorial systems compile a single .tex file that must not depend on \\input files or on running BibTeX.
This script writes, for the anonymised review copy and for the identified copy:
  * a flattened .tex file in which every \\input{tables/...} is replaced by the table file's contents,
    \\bibliography{...} is replaced by the compiled .bbl, the \\ifanon switch is resolved, and figures are
    referenced by bare file names;
  * copies of the figure PDFs next to it.
Each flattened file is then compiled with pdflatex (three passes) in a scratch directory and its text is
compared with the text of the corresponding PDF built by build_papers.sh, so that the uploaded source is
known to reproduce the reviewed PDF.

Usage: python code/53_flatten_submission.py        (run build_papers.sh first)
The submission/ folder it fills is distributed as a separate archive and is not part of the deposited
replication package; the hand-written files in it (highlights, cover letter, declarations, README) are kept.
Output: submission/ (Manuscript_*.pdf, Title_Page.*, figures/, latex_source_anonymised/, latex_source_identified/)
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "paper_en"
OUT = ROOT / "submission"


def resolve_ifanon(src, anon):
    """Resolve \\ifanon ... \\else ... \\fi blocks (they are not nested in main.tex)."""
    # drop the toggle definition and its comment line first, so the pattern below only sees the two branches
    src = re.sub(r"^% Anonymised review copy:.*$\n", "", src, flags=re.M)
    src = re.sub(r"^\\ifdefined\\ifanon.*$\n", "", src, flags=re.M)
    pat = re.compile(r"\\ifanon\n(.*?)\\else\n(.*?)\\fi\n", re.S)

    def pick(m):
        return m.group(1) if anon else m.group(2)

    src, n = pat.subn(pick, src)
    assert n == 2, n
    return src


def flatten(anon):
    src = (P / "main.tex").read_text(encoding="utf-8")
    src = resolve_ifanon(src, anon)
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
    shutil.copy(P / "titlepage.pdf", OUT / "Title_Page.pdf")
    shutil.copy(P / "titlepage.tex", OUT / "Title_Page.tex")
    figdir = OUT / "figures"
    if figdir.exists():
        shutil.rmtree(figdir)
    figdir.mkdir()
    for fig in (OUT / "latex_source_anonymised").glob("fig_*.pdf"):
        shutil.copy(fig, figdir / fig.name)
    print("flattened sources, PDFs, title page and figures written to", OUT)


if __name__ == "__main__":
    main()
