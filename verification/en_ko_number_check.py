"""Check that the Korean edition (paper_ko/main.tex) prints the same numbers as the English original (paper_en/main.tex).

Both manuscripts are split into the same sequence of parts: the front matter (title block, author note and abstract),
then one part per section and subsection, including the declarations and the appendices. In each part every number
written in digits is collected from the prose, headings, captions, table notes and equations; table bodies are not part
of the manuscripts (they are \\tabinput files, and extensions/build_revision_tables_ko.py guarantees that the Korean
bodies carry the English numbers). The two multisets are compared part by part.

Some differences come from the language alone: English writes month names, half-years (H1, H2) and many small numbers as
words ("nine plans", "one-seventh", "two orders of magnitude"), whereas Korean writes month numbers and counters in digits
("9개", "7분의 1", "100배"). Month numbers ("9월") and half-year labels are removed before counting; every other known
difference is listed in EXPECTED with its reason, and was checked by reading both texts. Anything else fails the check.

Usage: python verification/en_ko_number_check.py            (prints a summary; exit status 1 on any unexplained difference)
       python verification/en_ko_number_check.py --report   (lists every difference, explained or not)
"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

# Differences that come from the language only, keyed by the English heading of the part: (numbers written in digits only
# in the Korean text, numbers written in digits only in the English text, reason). Each was checked in both texts.
EXPECTED = {
    "front matter": ({"100": 1, "9": 1}, {},
        "abstract: 'a hundredfold' = 100배; 'nine plans' = 9개 요금제"),
    "Introduction": ({"20": 1, "100": 1, "9": 1, "16": 3, "1": 3, "2": 1, "6": 1, "10": 1}, {},
        "'richest fifth' = 20%; 'two orders of magnitude' = 100배; 'nine plans' = 9개; 'sixteen' (three times) = 16개국; "
        "'second-degree' = 2급; 'a sixth' = 6분의 1; 'one tenth' = 10분의 1; 'a free year' = 1년"),
    "The price menu": ({"0": 1, "2": 1}, {},
        "'near-zero marginal cost' = 한계비용이 거의 0; 'second-degree' = 2급"),
    "The affordability burden": ({"3": 2, "5": 1}, {},
        "'over three years' (text and footnote) = 3년간; 'quintile' = 5분위"),
    "Data": ({"5": 4, "1": 1, "100": 1, "200": 1, "8": 2, "16": 1, "12": 1}, {},
        "'quintile' (table rows, ATLAS sentence) = 5분위; 'one-week window' = 1주일; 'one million' = 100만; "
        "'two million' = 200만; 'eight other West African economies' and 'eight European economies' = 8개국; "
        "'sixteen' = 16개국; 'twelve months' = 12개월"),
    "What vendors localise: local prices by tier": ({"1": 2, "9": 1, "7": 1, "0": 3, "3": 1, "5": 1, "8": 1}, {},
        "'minus one' = -1; 'one-seventh' = 7분의 1; 'nine plans' = 9개; 'near zero', 'from zero', 'excludes zero' = 0; "
        "'three, five and eight times' = 3배, 5배, 8배"),
    "Burdens": ({"20": 3, "5": 3}, {},
        "'poorest/richest fifth' (three times) = 최하위/최상위 20%; 'quintile' (figure and table captions) = 5분위"),
    "Any use: the extensive margin": ({"2": 2, "1": 2}, {},
        "'second quarter of 2026' (twice) = 2026년 2분기; 'one-log-point', 'each log point' = 로그 1포인트"),
    "Per-capita Claude activity: comparison with any-product adoption": ({"1": 4, "5": 1, "4": 1}, {"2026": 1},
        "'one low-income economy' (text and table note) = 저소득국 1개; 'per log point' = 로그 1포인트; 'a quarter of users' = 4분의 1; "
        "'adoption quintile' = 5분위; English repeats the year in 'May 2026', Korean lists 2월, 4월, 5월 after one 2026년"),
    "Localised entry tiers and adoption: the first rollouts of ChatGPT Go": ({"8": 1, "16": 13, "14": 1, "12": 1, "1": 1, "11": 3, "10": 1, "5": 1}, {"2025": 2},
        "'sixteen' (thirteen times) = 16개국; 'eight European economies' = 8개국; 'fourteen' = 14개; 'twelve months' = 12개월; "
        "'a free year' = 1년; 'eleven' (three times) = 11개국; 'ten of the eleven' = 10개국; 'five weeks' = 5주; "
        "Korean states the year once in '2025년 8월 19일 ... 10월 14일' where English repeats 2025 (text and caption)"),
    "Policy counterfactuals": ({"10": 3, "1": 3}, {},
        "'one tenth of the working-age population' (three times) = 10분의 1"),
    "What the evidence does and does not show": ({"0": 1}, {},
        "'a zero price' = 가격 0"),
    "From conditional gains to convergence": ({"2": 1, "3": 1}, {},
        "'twice as large' = 2배; 'more than three times' = 3배"),
    "Policy implications": ({"3": 1, "4": 1, "1": 1}, {},
        "'third-degree' = 3급; 'a quarter of average income' = 4분의 1"),
    "Conclusion": ({"20": 1, "2.5": 1, "4": 2, "1": 2, "10": 1}, {},
        "'richest fifth' = 20%; 'two and a half times' = 2.5배; 'four times' = 4배; 'more than a quarter' = 4분의 1; 'a tenth' = 10분의 1"),
    "A conditional framework for free and paid access": ({"1": 1, "4": 1}, {},
        "'a quarter pay' = 4분의 1"),
    "Data construction and replication": ({"4": 1, "3": 1, "8": 1, "16": 2, "14": 1, "11": 1, "100": 3}, {"1": 3},
        "'Four storefront-plan cells' = 4개; 'In three cells' = 3개; 'eight European economies' = 8개국; 'sixteen' (twice) = 16개국; "
        "'fourteen' = 14개국; 'Eleven' = 11개국; 'about 1 million conversations' (three table rows) = 약 100만 건"),
    "Connectivity accounting": ({"1": 2}, {},
        "'no ratio exceeds one', 'the value of one' = 1"),
}


def identified(src):
    """Resolve the \\ifanon switch of the English source to the identified branch (the Korean edition has no other)."""
    src = re.sub(r"^% Anonymised review copy:.*$\n", "", src, flags=re.M)
    src = re.sub(r"^\\ifdefined\\ifanon.*$\n", "", src, flags=re.M)
    return re.sub(r"\\ifanon\n(.*?)\\else\n(.*?)\\fi\n", lambda m: m.group(2), src, flags=re.S)


def parts(src):
    body = src[src.index("\\title{"):src.index("\\end{document}")]
    body = re.sub(r"(?<!\\)%.*", "", body)                               # comments
    pieces = re.split(r"\\(?:sub)?section\*?\{", body)
    return pieces


def numbers(tex, lang):
    t = tex
    t = re.sub(r"\\(?:label|ref|eqref|pageref)\{[^}]*\}", " ", t)
    t = re.sub(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{[^}]*\}", " ", t)
    t = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\tabinput\{[^}]*\}", " ", t)
    t = re.sub(r"\\href\{[^}]*\}", " ", t)                                # keep the link text, drop the target
    t = re.sub(r"\\begin\{tabularx?\}(?:\{\\textwidth\})?\{(?:[^{}]|\{[^{}]*\})*\}", " ", t)   # column specifications
    t = re.sub(r"\\(?:multicolumn|cmidrule)(?:\([^)]*\))?\{[^}]*\}(?:\{[^}]*\})?", " ", t)
    t = re.sub(r"\\setlength\{[^}]*\}\{[^}]*\}", " ", t)
    if lang == "ko":
        t = re.sub(r"\d+(?:--\d+)?월", " ", t)         # month numbers (English writes month names)
        t = t.replace("1인당", " ")                     # "per capita"
    else:
        t = re.sub(r"\bH[12]\b", " ", t)               # half-years (Korean writes 상반기, 하반기)
    t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", t)      # thousands separators
    return Counter(re.findall(r"\d+(?:\.\d+)?", t))


def main():
    report = "--report" in sys.argv
    en = parts(identified((ROOT / "paper_en/main.tex").read_text(encoding="utf-8")))
    ko = parts((ROOT / "paper_ko/main.tex").read_text(encoding="utf-8"))
    if len(en) != len(ko):
        raise SystemExit(f"different section structure: {len(en)} English parts, {len(ko)} Korean parts")
    bad = 0
    checked = 0
    seen = set()
    for i, (e, k) in enumerate(zip(en, ko)):
        ce, ck = numbers(e, "en"), numbers(k, "ko")
        checked += sum(ce.values())
        ko_extra, en_extra = ck - ce, ce - ck
        title = e.split("}", 1)[0].replace("\n", " ").replace("\\$", "$") if i else "front matter"
        exp_ko, exp_en, _ = EXPECTED.get(title, ({}, {}, ""))
        seen.add(title)
        unexplained_ko = ko_extra - Counter(exp_ko)
        unexplained_en = en_extra - Counter(exp_en)
        stale = (Counter(exp_ko) - ko_extra) + (Counter(exp_en) - en_extra)
        if report and (ko_extra or en_extra):
            print(f"[{i}] {title}\n    Korean only: {dict(ko_extra)}\n    English only: {dict(en_extra)}")
        if unexplained_ko or unexplained_en or stale:
            bad += 1
            print(f"UNEXPLAINED [{i}] {title}: Korean only {dict(unexplained_ko)}; English only {dict(unexplained_en)};"
                  f" listed but not found {dict(stale)}")
    for title in set(EXPECTED) - seen:
        bad += 1
        print(f"UNEXPLAINED: EXPECTED lists a part that does not exist: {title}")
    explained = sum(sum(Counter(v[0]).values()) + sum(Counter(v[1]).values()) for v in EXPECTED.values())
    print(f"{len(en)} parts, {checked} numbers in the English text; {explained} language-only differences listed; "
          f"{bad} part(s) with unexplained differences")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
