"""
50_make_docx.py -- Word version of a manuscript (for journals that require .docx/.hwp submission).
Flattens the LaTeX source (inlines tables, resolves cross-references from the .aux file, simplifies multi-row
table headers, switches figures to PNG) and converts it with pandoc (+citeproc, author-date references).
Usage: python code/50_make_docx.py ko   (or en)
"""
import re, sys, pathlib, subprocess, shutil
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / f"paper_{LANG}"
BUILD = ROOT / "output" / f"docx_build_{LANG}"
BUILD.mkdir(parents=True, exist_ok=True)
src = (P / "main.tex").read_text()
aux = (P / "main.aux").read_text()

# ---------------------------------------------------------------- cross-references from the compiled .aux
labels = dict(re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux))

# ---------------------------------------------------------------- simplified single-row table headers
H = {
 "ko": {
  "tab:burden": r"소득집단 & $N$ & 1인당 GNI 중위값 & \$8 & \$20 & \$60 & \$100 & \$200 & \$300 & \$20에서 2\% 충족(\%) & \$20, 가계소비 기준 & \$20, PPP 연동 \\",
  "tab:quintile": r"소득집단 & $N$ & 하위 20\% & 중위 20\% & 상위 20\% & 모바일 광대역 2GB (GNI 대비 \%) & AI 요금제/광대역 \\",
  "tab:local": r"요금제 & 미국 가격 & 고소득 & 상위중소득 & 하위중소득 & 저소득 & $\hat\beta$ & (표준오차) & $N$ \\",
  "tab:store": r"소득집단 & $N$ & 현지 스토어(\%) & 스토어 없음(\%) & 미제공(\%) & 달러 표시(\%) & 최저가 유료(달러) & 최저가 부담(\%) & Plus 부담(\%) \\",
  "tab:diffusion": r" & (1) 수준 & (2) 로그 & (3) 로그 & (4) 로그 & (5) 로그 & (6) 로그 & (7) 로그 \\",
  "tab:decomp": r"소득집단 & $N$ & AI 이용자(\%) & 인터넷(\%) & 온라인 중 AI(\%) & 로그 격차 전체 & 연결성 & 채택 & 연결성 몫(\%) \\",
  "tab:scen": r"소득집단 & 노출도 $E$(\%) & 채택률 $a$(\%) & 단순 곱($g$=20\%) & 헐튼 $g$=10\% & 헐튼 $g$=20\% & 헐튼 $g$=30\% & 고소득국 채택률 적용($g$=20\%) \\",
  "tab:auitime": r"시점 & 탄력성(전체) & (표준오차) & $N$ & $R^2$ & 탄력성(공통 표본) & (표준오차) \\",
 },
 "en": {
  "tab:burden": r"Income group & $N$ & Median GNI p.c. & \$8 & \$20 & \$60 & \$100 & \$200 & \$300 & Meets 2\% at \$20 (\%) & \$20, HH cons. & \$20, PPP-idx. \\",
  "tab:quintile": r"Income group & $N$ & Poorest 20\% & Middle 20\% & Richest 20\% & Mobile broadband 2 GB (\% GNI p.c.) & AI plan / broadband \\",
  "tab:local": r"Plan & U.S. price & High & Upper-mid. & Lower-mid. & Low & $\hat\beta$ & (s.e.) & $N$ \\",
  "tab:store": r"Income group & $N$ & Local store (\%) & No store (\%) & Not offered (\%) & USD-priced (\%) & Cheapest tier (US\$) & Cheapest burden (\%) & Plus burden (\%) \\",
  "tab:diffusion": r" & (1) Level & (2) Log & (3) Log & (4) Log & (5) Log & (6) Log & (7) Log \\",
  "tab:decomp": r"Income group & $N$ & AI users (\%) & Internet (\%) & AI among online (\%) & Log gap total & Connect. & Adoption & Connectivity share (\%) \\",
  "tab:scen": r"Income group & Exposed $E$ (\%) & Adoption $a$ (\%) & Naive ($g$=20\%) & Hulten $g$=10\% & Hulten $g$=20\% & Hulten $g$=30\% & At HIC adoption ($g$=20\%) \\",
  "tab:auitime": r"Window & Elasticity (all) & (s.e.) & $N$ & $R^2$ & Elasticity (common) & (s.e.) \\",
 }}[LANG]
TABWORD, FIGWORD = ("표", "그림") if LANG == "ko" else ("Table", "Figure")


def inline_tables(t):
    return re.sub(r"\\tabinput\{(tables/[^}]+)\}", lambda m: (P / m.group(1)).read_text(), t)


def multicol(t):
    # \multicolumn{n}{spec}{text} -> text followed by n-1 empty cells
    return re.sub(r"\\multicolumn\{(\d+)\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}",
                  lambda m: m.group(2) + " &" * (int(m.group(1)) - 1), t)


def fix_table(env):
    lab = re.search(r"\\label\{(tab:[^}]+)\}", env)
    lab = lab.group(1) if lab else None
    notes = re.search(r"\\begin\{tablenotes\}(?:\[[^\]]*\])?(.*?)\\end\{tablenotes\}", env, re.S)
    note_txt = re.sub(r"\\(footnotesize|small)\b", "", notes.group(1)).replace("\\item", "").strip() if notes else ""
    env = re.sub(r"\\begin\{tablenotes\}.*?\\end\{tablenotes\}", "", env, flags=re.S)
    env = re.sub(r"\\(begin|end)\{threeparttable\}", "", env)
    env = re.sub(r"\\setlength\{\\tabcolsep\}\{[^}]*\}", "", env)
    env = re.sub(r"\\(footnotesize|scriptsize|small)\b", "", env)
    env = re.sub(r"\\cmidrule(\([a-z]*\))?\{[^}]*\}", "", env)
    env = env.replace("\\addlinespace", "")
    env = re.sub(r"\\begin\{tabularx\}\{[^}]*\}\{", r"\\begin{tabular}{", env).replace("\\end{tabularx}", "\\end{tabular}")

    def spec(m):
        s = m.group(1)
        s = re.sub(r">\{[^}]*\}", "", s)
        s = re.sub(r"p\{[^}]*\}", "l", s).replace("X", "l").replace("@{}", "")
        return "\\begin{tabular}{" + s + "}"
    env = re.sub(r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}", spec, env)
    if lab in H:
        env = re.sub(r"(\\toprule)(.*?)(\\midrule)", lambda m: m.group(1) + "\n" + H[lab] + "\n" + m.group(3), env,
                     count=1, flags=re.S)
    env = multicol(env)
    num = labels.get(lab, "")
    env = re.sub(r"\\caption\{", lambda m: "\\caption{" + f"{TABWORD} {num}. ", env, count=1)
    return env + ("\n\n" + note_txt + "\n\n" if note_txt else "")


def fix_figure(env):
    lab = re.search(r"\\label\{(fig:[^}]+)\}", env)
    num = labels.get(lab.group(1), "") if lab else ""
    env = re.sub(r"(figures/[A-Za-z0-9_]+)\.pdf", r"\1.png", env)
    env = re.sub(r"\\caption\{", lambda m: "\\caption{" + f"{FIGWORD} {num}. ", env, count=1)
    return env


t = inline_tables(src)
t = re.sub(r"\\begin\{table\}.*?\\end\{table\}", lambda m: fix_table(m.group(0)), t, flags=re.S)
t = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", lambda m: fix_figure(m.group(0)), t, flags=re.S)
# equations: show their numbers explicitly
def eqnum(m):
    body = m.group(1)
    lab = re.search(r"\\label\{([^}]+)\}", body)
    n = labels.get(lab.group(1), "") if lab else ""
    body = re.sub(r"\\label\{[^}]+\}", "", body).strip()
    return "\\[\n" + body + (f" \\qquad ({n})" if n else "") + "\n\\]"
t = re.sub(r"\\begin\{equation\}(.*?)\\end\{equation\}", eqnum, t, flags=re.S)
t = re.sub(r"\\eqref\{([^}]+)\}", lambda m: f"({labels.get(m.group(1), '?')})", t)
t = re.sub(r"\\ref\{([^}]+)\}", lambda m: labels.get(m.group(1), "?"), t)
# section numbering as in the PDF (numbers, then appendix letters)
sec, sub, app = 0, 0, False
out = []
for line in t.split("\n"):
    if line.strip() == "\\appendix":
        app, sec = True, 0
        continue
    m = re.match(r"\\section\{(.*?)\}(.*)", line)
    if m:
        sec += 1; sub = 0
        n = chr(64 + sec) if app else str(sec)
        line = f"\\section*{{{n}~~{m.group(1)}}}{m.group(2)}"
    m = re.match(r"\\subsection\{(.*?)\}(.*)", line)
    if m:
        sub += 1
        line = f"\\subsection*{{{sec}.{sub}~~{m.group(1)}}}{m.group(2)}"
    out.append(line)
t = "\n".join(out)
ref_title = "참고문헌" if LANG == "ko" else "References"
t = re.sub(r"\\bibliographystyle\{[^}]*\}\s*\\bibliography\{[^}]*\}",
           "\\\\section*{" + ref_title + "}\n\nREFSPLACEHOLDER\n", t)
t = t.replace("\\qed", "").replace("\\nolinkurl{", "\\texttt{").replace("\\clearpage", "").replace("\\newpage", "")
t = re.sub(r"\\makeatletter.*?\\makeatother[^\n]*", "", t)
(BUILD / "flat.tex").write_text(t)

# ---------------------------------------------------------------- reference document with suitable fonts
ref = BUILD / "reference.docx"
subprocess.run(["pandoc", "-o", str(ref), "--print-default-data-file", "reference.docx"], check=True)
doc = Document(ref)
latin, east = ("Times New Roman", "Malgun Gothic") if LANG == "ko" else ("Times New Roman", "Times New Roman")
for st in doc.styles:
    try:
        rpr = st.element.get_or_add_rPr()
    except Exception:
        continue
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = rpr.makeelement(qn("w:rFonts"), {}); rpr.insert(0, fonts)
    for a in ["w:ascii", "w:hAnsi", "w:cs"]:
        fonts.set(qn(a), latin)
    fonts.set(qn("w:eastAsia"), east)
    for a in ["w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"]:
        if fonts.get(qn(a)) is not None:
            del fonts.attrib[qn(a)]
for name, size in [("Normal", 10.5), ("Body Text", 10.5), ("First Paragraph", 10.5), ("Compact", 9)]:
    if name in [s.name for s in doc.styles]:
        doc.styles[name].font.size = Pt(size)
doc.save(ref)

lua = BUILD / "refs.lua"
lua.write_text('function Para(el)\n  if #el.content == 1 and el.content[1].t == "Str" and el.content[1].text == "REFSPLACEHOLDER" then\n'
               '    return pandoc.Div({}, pandoc.Attr("refs"))\n  end\nend\n')
out_docx = ROOT / "output" / f"Affording_Generative_AI_{LANG.upper()}.docx"
cmd = ["pandoc", str(BUILD / "flat.tex"), "-f", "latex", "-t", "docx", "--resource-path", str(ROOT / "output"),
       "--reference-doc", str(ref), "--lua-filter", str(lua), "--citeproc",
       "-M", "abstract-title=" + ("국문 초록" if LANG == "ko" else "Abstract"),
       "--bibliography", str(P / "references.bib"), "-o", str(out_docx)]
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stderr[-2000:] if r.stderr else "", "->", out_docx)

# pandoc 3.1 ignores abstract-title for docx: relabel the abstract heading in place
d = Document(out_docx)
for para in d.paragraphs[:12]:
    if para.text.strip() == "Abstract" and LANG == "ko":
        for run in para.runs:
            run.text = ""
        para.runs[0].text = "국문 초록"
        break
d.save(out_docx)
print("abstract heading set")
