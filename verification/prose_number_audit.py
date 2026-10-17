"""Audit of the numbers printed in the prose of paper_en/main.tex (version 3.1).

Every numerical statement in the abstract, Sections 1-8 (introduction, institutional background, model, data, results,
public usage indicators, discussion, conclusion), the Declarations and Appendices A-G (model, data construction, other channels,
usage indicators, additional tables, the Go rollout, the measurement protocol), including the numbers typed by hand in table
notes, captions and column headers and in the hand-written Tables 1, 2, A.1, B.1 and G.1, is compared with the value produced
by the pipeline: output/results.json (baseline analysis), output/results_wave2.json (second App Store wave, default panel and,
since version 3.1, the key families rel_*/relplus_*/relfront_*/stacked_*/incr_*/incrusd_* of code/13_relative_prices.py,
taxabs_* and <plan>_n_exact/_above3/_above10/_dev_slope_nonusd/_popw/_se_hc3 of code/12_default_panel.py, guard_*/applevel_*/
wave2_dedup_* of code/09b_wave2_items.py, val_* of code/14_default_validation.py, vint_* of code/15_vintage_test.py and xch_* of
code/16_cross_channel.py; also rel_frontierpairs_* (the bound over the nine within-firm pairs of two
frontier tiers), round_* (the round-number listings of Claude Pro and Perplexity Pro in dollar storefronts) and taxabs_*_lmic of
code/12, the storefront-clustered standard errors vint_*_se_sf/_absdev_fx_se_sf of code/15, stacked_*_ri_n_ge and the 22-item
stack of code/13 (the family variants are outside it), and xch_play_chatgpt_exact_n of code/16), the tables in output/tables/
(W1-W15b; W2_benchmarks.csv supplies the item-sample slopes of the storage, creator and family items quoted in the footnote of
Section 5.1, W8_relative_pairs.csv the 21 pairs and their groups, W10_cross_vendor.csv the rows of Table E.10,
W13_tax_absorption.csv the LMIC columns of Table E.13, W15b_play_countries.csv the Brazilian prices of Appendix C), the
CSV/JSON outputs of extensions/ and checks/ (among them checks/results/sim_output.txt, the output of checks/sim_check.py, for
the calibrated examples of Appendix A), the READMEs of the raw extracts (data/raw/web, data/raw/appstore_wave2,
data/raw/fx_hist), or a direct recomputation from the processed data, the raw App Store records, the rollout record or the
closed-form expressions of Appendix A. Table bodies are not checked here
because they are written by code (code/40_tables_tex.py, code/41_tables_wave2.py, code/42_tables_relative.py,
extensions/build_revision_tables.py, checks/build_matched_menu_table.py) and verified with the --check modes of those scripts;
the numerical claims of the model (Appendix A) are verified by checks/verify_tier_model.py and checks/sim_check.py, and this
script recomputes the constants quoted in the text from the same closed-form expressions and reads the simulated values from
sim_output.txt.

Usage:  python verification/prose_number_audit.py [--list-pins] [--list-unresolved] [--no-coverage] [--strict]
        (from the package root; exit code 1 on any mismatch, on any numeral or number word of the prose that no check accounts
        for, or when a passage that the audit parses has been reworded: the audit then stops and reports the failures found so far;
        the last line of the report is "N checks, M mismatches")

How the ledger works.
  * Each paragraph or sentence of main.tex that carries numbers is anchored with S(start, end): the text between two exact
    snippets, each of which must occur in main.tex (the start exactly once), so the ledger cannot drift from the manuscript.
  * P.v(printed, value) compares a number printed in the anchored passage with the pipeline value. A printed value passes if
    it equals the pipeline value rounded (half-up or half-even) to the printed number of decimals; the sign is read from the
    text ("$-0.007$" is minus). P.gt / ge / lt / le check statements of the form "more than", "at most", "below"; P.about
    checks "about 23%" against a stated tolerance; P.w checks a number written as a word ("sixteen", "ninefold", "one half").
    Every call consumes one occurrence of the number in the passage, so a number that is changed in the text, or added to it,
    is found.
  * P.pin(...) records numbers for which no pipeline value can exist (a price taken from a vendor page, an allowance multiple,
    a number quoted from another paper): the statement is only pinned to the text, that is, the exact number must still be there.
    P.pin_rest(expected...) pins the numerals that remain in a passage and requires them to be exactly the expected ones, in
    order, so that a vendor-page number that is changed, added or deleted is reported; without arguments it requires that no
    numeral is left. P.wpin pins a number word that is part of the structure of the argument ("the two channels"). --list-pins
    prints every pin.
  * P.dt("27 September 2026", ts) compares a printed date as a whole: the phrase must occur in the passage, and its day, month name
    (full or abbreviated) and year are compared with the timestamp ts of the pipeline record it refers to (fetch dates of the
    App Store waves, the rollout record, the sample windows and release dates of the Anthropic data dictionary, the WDI update,
    the exchange-rate snapshots of data/raw/fx_hist, the Apple Developer News dates quoted in code/15_vintage_test.py);
    ranges of days ("4--11 August 2025") take a second timestamp. A month name is therefore tied to its own day and year, and
    a month that is changed, or exchanged with that of another date, is found. A date that has no pipeline record (a vendor
    announcement, a press report, a World Bank effective date) is pinned with P.dtpin.
  * An "unresolved" entry is a printed number that does not match the pipeline under the literal reading of its sentence and that
    cannot be repaired without changing the wording or the definition of the sentence, which is the author's decision, not the
    audit's (P.open). It is compared like any other number: it is a pass as soon as the text states a number that the pipeline
    reproduces. Until then it is neither a pass nor counted as a mismatch, it is printed at the end of every run (and by
    --list-unresolved), and it does not change the exit status; with --strict every unresolved entry is a mismatch. P.open_cond
    records a claim that is a condition on pipeline values in the same way when it fails under the literal reading
    (it carried the former "the only slopes beyond +-0.01" claim of Section 5.1 until the text was reworded; no entry at present).
  * Two forms of main.tex are audited. The identified manuscript (paper_en/main.tex of the working copy) carries both branches of the
    \\ifanon switch; the anonymised copy of the package (code/54_anonymised_package.py) carries the anonymised branch only and
    lacks extensions/zenodo_record.json. The passages and sources that exist only in the identified form (author line with the
    preprint number and the version, date line, data-availability paragraph with the archive versions) are checked when they are
    present and skipped otherwise; the AI-use declaration, which both branches carry, is anchored through the \\ifanon and \\else
    lines in the identified form and directly in the anonymised form; everything else is audited in both forms.
  * Coverage: every digit string of the prose (title block to the end of the document, captions, table notes, column headers and
    the hand-written tables; comments, labels, references, citations, URLs, layout arguments such as \\arraystretch excluded) must
    be consumed by a check or a pin, and so must every number word from "two" to "seventeen" and the multiplicative words (twice,
    doubles, doubling, ninefold, hundredfold, half, quarter, fifth, tenth, million) and every month name of a date (January ...
    December, Jan ... Dec); "one", "zero" and ordinals are not scanned and are checked where a passage states an empirical count.
    Names and labels (Microsoft 365, HC1, CR1, P1-P5, Pro 200, SHA-256, fawazahmed0, Gemini 100 GB, Google AI Plus 2 TB) and
    single digits inside in-line, display (\\[ ... \\]) and equation mathematics are recorded as labels or notation, not as numbers.

Rules for derived numbers (each check repeats its rule in its note).
  * Rounding: a printed number equals the pipeline value rounded (half-up or half-even) to the printed decimals; "more than",
    "at least", "below", "at most" are inequalities against the unrounded value; "about" carries the tolerance written in the call.
  * Log points to per cent: a deviation d = ln(listed price / default price) is printed as 100 (e^d - 1) per cent wherever the text
    says "per cent" or "%" (the conversion of code/12_default_panel.py, whose factors the audit reads from that code) and as 100 d
    only where the text says "log points"; slopes on log income, elasticities and index changes in logs are not converted.
  * Within-firm relative prices (Section 5.1, code/13_relative_prices.py): "A is x% cheaper relative to B in the median poorer
    storefront" is 100 (1 - m) with m the median of e^d over the low- and lower-middle-income storefronts (rel_<pair>_lmic_med);
    "absolute slopes at most 0.022" (abstract, introduction) is an inequality on rel_frontierpairs_abs_slope_max, the largest
    |slope| over the nine pairs of Table 3 whose two plans are both frontier tiers (group_a = group_b = frontier in
    W8_relative_pairs.csv), and "slopes between -0.022 and 0.011" (Section 5.1) their min/max, every pair measured
    as the higher tier (A) relative to the firm's standard frontier tier (B; keys rel_pro100_plus_*, rel_ultra_aipro_*,
    rel_max5_claudepro_* and so on); "0.15--0.34 for YouTube and X Premium" and "50--73% cheaper" are ranges over the seven pairs
    whose first plan is a YouTube or X Premium product; "45--95% of the storefronts" is the range of the mass at a relative price
    of one over the nine frontier pairs; "randomisation p < 0.0005" is a p-value of zero of 2,000 permutations; "more than 10%
    cheaper" is e^d < 0.9 and "at the same relative price" |d| < 0.005, the thresholds read from the code. The slopes of the storage, creator and family items quoted in
    the footnote of Section 5.1 are the item-sample slopes of Appendix Table E.9 (W2_benchmarks.csv), not the plan-level
    <plan>_usd_slope keys, whose sample is the storefronts with a multiplier (X creator subscription: 0.032 against 0.026); "move
    with the plans they extend" is read as: a family variant is localised (median LMIC ratio below 0.9, dollar slope above 0.10)
    exactly when the plan it extends is.
  * Stacked regression (Table 4): the 22 items and five firms are read from STACK in code/13_relative_prices.py (the family
    variants are excluded since the sample rule was applied literally); the printed randomisation shares (0.05%, 0.006%, 41%)
    and the introduction's p = 0.0005 are stacked_<group>_ri_p rounded to the printed decimals (0.000476, 0.000056, 0.4145).
  * Round-number listings (Section 5.3, Table E.13 notes): "both at $25.00 in all 16 taxed dollar storefronts" and "both at $22.00
    in the same eight dollar storefronts whose panel tax factor is one" are the keys round_usd16_both25_n and round_tf1_both22_n
    of code/12_default_panel.py, recomputed from wave2_plan_vs_default.csv and wave2_default_multiplier.csv; "Ten of these 16
    storefronts are low- or lower-middle-income" and the counts "in all ten" / "in five" are taxabs_n_lmic_storefronts and
    taxabs_<plan>_at_us_lmic.
  * Other channels: "identical in 20" is code/16's definition of identical, |ln(Play / App Store)| < 0.005, which the text calls
    "the 0.5% band of the stability comparison" (xch_play_chatgpt_exact_n; the "19 to the cent" and Brazil's R$39.99 / R$39.90 are
    read from W15b_play_countries.csv); for Microsoft, "identical to the cent in 37 of 49" is xch_ms_web_vs_app_<plan>_exact_n
    (|web - App Store| < 0.005 in the storefront's currency), "within 0.5% in 45" xch_ms_web_vs_app_<plan>_within05_n
    (|ln difference| < 0.005) and "the widest gap, Sweden, 4.3% / 2.4%" the _maxgap_pct keys with the country from the note column
    of W15_cross_channel.csv; "98 comparisons" is the sum of the Premium and Personal comparisons (49 + 49).
  * Vintage test: the text quotes the storefront-clustered standard errors (vint_frontier_se_sf, _se_ctrl_sf, _absdev_fx_se_sf),
    Table E.15's notes both the storefront- and the currency-clustered ones; "37 currencies in the price sample" (Table 2) is the
    currency count of the regression sample with income data and a multiplier (vint_go_n_currencies = vint_frontier_n_currencies),
    whereas vint_currencies (39) also counts NGN and TRY, which enter the file only through the Gemini 100 GB item's exact reference.
  * Table E.9: its 29 rows are the 22 stacked items plus the storage plans (Google One 100 GB, Microsoft 365 Basic), the Google One
    app's second listing of Google AI Plus (2 TB), the family variants (YouTube Premium Family, YouTube Music Family, Microsoft
    365 Family) and X's creator subscription, with the groups storage / capped_one / family / creator in W2_benchmarks.csv; the
    inclusion rule of its notes is re-applied to wave2_item_slopes.csv (subscriptions of the five firms' nine apps in at least 60
    storefronts, less the annual variants and the post-promotion product).
  * The dollar gap of ChatGPT Go on the high-usage tiers: "0.6--4% on a $100--500 tier" (Section 3, Appendix A.4) applies the
    rounded $3 and $4 gaps to the $500 and $100 tiers.
  * Ranges "a--b" over plans, pairs, storefronts, income groups, releases, windows or tie rules: a is the minimum and b the maximum of
    the pipeline values over exactly the items the sentence lists, each rounded to its printed decimals (for example the 13 frontier
    tiers of the six vendors for "the $20 and $100--500 tiers", the plans named for "Claude Pro, Claude Max, Perplexity Pro and
    SuperGrok ... in 25--37%").
  * Counts "n of N" (for example 1,551 of 2,414 storefront-point cells, 22 of 25 same-currency countries, 117 of 126 storefronts):
    n and N are counted in the CSV or in the raw records with the filter the sentence names (income group, currency, clean storefront,
    at least three price points, unique mode at or above one half); "LMIC" in the keys of results_wave2.json is low plus lower-middle
    income.
  * The dollar gap of ChatGPT Go ("$3--4 below its U.S. price") is the U.S. price less the median low-income first-wave price and
    less the lowest listed first-wave price; the discounts "15--20% on a $20 tier" and "1--4% on a $100--300 tier" apply the rounded
    gaps to the standard price and to the $300 and $100 tiers.
  * Tax factor: the storefront multiplier divided by the market exchange rate (data/processed/wave2_default_multiplier.csv); a
    dollar storefront "embeds a tax of more than 5%" when its tax factor exceeds 1.05 (code/12_default_panel.py).
  * Tie-rule ranges: minimum and maximum over the treatments of 50/50 ties that keep the tied cells (file order, lower price,
    higher price) in results_wave2.json (keys default_tie_*); the strict rule that discards them is quoted separately.
  * "HC3 standard errors leave every standard error unchanged at three decimals" is read as a change of less than 0.0005 (the
    half-unit of the third decimal) for every plan of Table 5; the condition's note records the plans whose third decimal would
    flip under strict rounding.
  * Calibrated examples of Appendix A (the $8 / $20 menu, the override gains by cost share) are read from the income grid and the
    summary lines of checks/results/sim_output.txt; the dispersions, cost shares and income fractions that are inputs of
    checks/sim_check.py are pinned or checked against the calibration header of that file.
  * Exposure to the Go tier: days from the arrival date in data/raw/openai/chatgpt_go_rollout.csv to 31 December 2025, divided by
    30.44 (365.25 / 12) and rounded to one decimal.
"""
import argparse
import bisect
import calendar
import json
import math
import re
import sys
import time
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

T0 = time.time()


def _abort_report(exc_type, exc, tb):
    """an unhandled exception means that a sentence the audit parses was reworded (or a source file changed): report the failures
    recorded so far, then the traceback, and exit with status 1"""
    import traceback
    for e in LEDGER:
        if e["status"] == "FAIL":
            print(f"  MISMATCH  {e['loc']}: printed {e['printed']!r}, pipeline value {e['value']!r} {e['note']}")
    traceback.print_exception(exc_type, exc, tb)
    print(f"prose_number_audit: ABORTED ({exc_type.__name__}: {exc}); a passage or a source file that the audit reads has probably "
          f"changed, and the checks after the failing line did not run.", file=sys.stderr)          # the interpreter then exits with status 1


sys.excepthook = _abort_report
ROOT = Path(__file__).resolve().parents[1]
AO = ROOT / "extensions" / "audit_output"
PU = ROOT / "checks" / "results"
PROC = ROOT / "data" / "processed"
TEXFILE = ROOT / "paper_en" / "main.tex"
TEX = TEXFILE.read_text(encoding="utf-8")
ANON_COPY = "\\ifanon" not in TEX          # anonymised copy of the package: the \ifanon switch of main.tex has been resolved to its anonymised branch

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--list-pins", action="store_true", help="also list every number that is pinned to the text only")
ap.add_argument("--list-unresolved", "--list-open", dest="list_open", action="store_true",
                help="list the printed numbers that do not match the pipeline literally (unresolved entries; they are listed in every run)")
ap.add_argument("--no-coverage", action="store_true", help="do not fail on numerals of the prose that no check accounts for")
ap.add_argument("--strict", action="store_true", help="count the unresolved entries (printed numbers awaiting the author's decision) as mismatches")
ARGS = ap.parse_args()

R = json.load(open(ROOT / "output" / "results.json"))
R2 = json.load(open(ROOT / "output" / "results_wave2.json"))


def D(x):
    return Decimal(repr(float(x)))


def rnd(x, d, mode=ROUND_HALF_UP):
    return D(x).quantize(Decimal(1).scaleb(-d), rounding=mode)


# ------------------------------------------------------------------------------------------------ months
MONTH_FULL = list(calendar.month_name)          # ['', 'January', ..., 'December']
MONTH_ABBR = list(calendar.month_abbr)          # ['', 'Jan', ..., 'Dec']
_MONTH_NAMES = ("January|February|March|April|May|June|July|August|September|October|November|December|"
                "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec")


# ------------------------------------------------------------------------------------------------ the ledger
LEDGER = []          # dicts: status ('ok' | 'FAIL' | 'open'), kind, loc, printed, value, note
COVER = {}           # offset of a numeral in main.tex -> 'value' | 'pin' | 'open' | 'notation'
COVERW = {}          # offset of a number word -> 'value' | 'pin'
COVERM = {}          # offset of a month name -> 'value' | 'pin'
PINS = []            # (line, token, why) of the numbers that are pinned to the text only

TOKEN = re.compile(r"\d{1,3}(?:(?:,|\{,\})\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
LINE_STARTS = [0]
for _l in TEX.split("\n"):
    LINE_STARTS.append(LINE_STARTS[-1] + len(_l) + 1)


def lineno(pos):
    return bisect.bisect_right(LINE_STARTS, pos)


def norm(tok):
    return tok.replace("{,}", "").replace(",", "")


# number words: meaning of the phrase (used by P.w); the coverage scan applies to SCAN_WORDS
WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "twenty": 20, "twice": 2, "doubles": 2, "doubling": 2, "ninefold": 9, "hundredfold": 100, "half": 0.5,
         "one half": 0.5, "one quarter": 0.25, "a quarter": 0.25, "quarter": 0.25, "three quarters": 0.75,
         "two and a half": 2.5, "four fifths": 0.8, "one tenth": 0.1, "a tenth": 0.1, "nine in ten": 0.9, "nine tenths": 0.9,
         "one million": 1e6, "two million": 2e6, "million": 1e6, "richest fifth": 0.2, "poorest fifth": 0.2,
         "fifth": 0.2, "fifths": 0.2, "a fifth": 0.2, "tenth": 0.1, "first": 1, "second": 2, "third": 3, "fourth": 4,
         "three weeks": 3, "five times": 5, "four times": 4, "a hundredfold": 100, "two quarters": 2}
SCAN_WORDS = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
              "sixteen", "seventeen", "twice", "doubles", "doubling", "ninefold", "hundredfold", "half", "quarter", "quarters", "fifth",
              "fifths", "tenth", "million"]


def text_sign(pos):
    """-1 if the numeral at pos is preceded by a minus sign ('$-0.007$', '(-1'), else +1 ('--' is a range dash)."""
    b = TEX[max(0, pos - 3):pos]
    if b.endswith("-") and not b.endswith("--") and (len(b) == 1 or b[-2] in "${(\\ \t~"):
        return -1
    if b.endswith("\u2212"):
        return -1
    return 1


def auto_label(p, t):
    """numerals that are part of a name or label and carry no quantity: 'Microsoft 365', 'HC1'/'HC3', 'P1'-'P5', exponents
    and subscripts inside formulas, period labels 'H1', 'Q2'"""
    pre = MASKED[max(0, p - 14):p]
    if t == "365" and re.search(r"Microsoft\s*$", pre):
        return True
    if t in ("1", "3") and re.search(r"HC$", pre):
        return True
    if t == "1" and re.search(r"(?<![A-Za-z])CR$", pre):
        return True                            # CR1: the small-sample corrected cluster-robust covariance estimator
    if len(t) == 1 and t in "12345" and re.search(r"(?<![A-Za-z])P$", pre):
        return True
    if len(t) == 1 and in_math(p) and re.search(r"[\^_]\{?$", pre):
        return True
    if t in ("1", "2", "3", "4") and re.search(r"(?<![A-Za-z])[HQ]$", pre):
        return True
    if t in ("1", "2") and re.search(r"[Ww]ave\s*$", pre):
        return True
    if t == "256" and re.search(r"SHA-$", pre):
        return True
    if t in ("100", "200", "500") and re.search(r"Pro\s*$", pre):
        return True
    if t in ("5", "20") and re.search(r"(Pro|Max)\s*$", pre) and MASKED[p + len(t):p + len(t) + 8].startswith("$\\times$"):
        return True
    if len(t) == 1 and MASKED[p - 1:p] == "(" and MASKED[p + 1:p + 2] == ")":
        ls = MASKED.rfind("\n", 0, p) + 1
        le = MASKED.find("\n", p)
        if re.match(r"\s*&?\s*\(\d\)(\s*&\s*\(\d\))+", MASKED[ls:le]):
            return True                        # column numbers in the header row of a regression table
    return False


class Passage:
    """A stretch of main.tex found by S(); numbers are consumed from it in the order the checks are written."""

    def __init__(self, loc, start, end, ok=True):
        self.loc, self.start, self.end, self.ok = loc, start, end, ok
        self.text = TEX[start:end] if ok else ""
        self.mtext = MASKED[start:end] if ok else ""          # prose only: no citations, labels, references, URLs
        self.toks = ([(start + m.start(), start + m.end(), norm(m.group(0))) for m in TOKEN.finditer(self.mtext)]
                     if ok else [])
        for a, b, t in self.toks:                       # names and labels carry no quantity and are never offered to a check
            if a not in COVER and auto_label(a, t):
                COVER[a] = "label"

    # -- sub-passages
    def sub(self, start, end=None):
        """A narrower passage: from `start` (which must occur exactly once in this passage) to the end of `end`
        (first occurrence after it) or to the end of this passage."""
        if not self.ok:
            return self
        n = self.text.count(start)
        if n != 1:
            LEDGER.append(dict(status="FAIL", kind="anchor", loc=f"{self.loc}: sub-anchor {start[:50]}", printed="", value=float(n),
                               note="SUB-ANCHOR OCCURS %d TIMES IN THE PASSAGE (must be exactly once)" % n))
            return Passage(self.loc, 0, 0, ok=False)
        a = self.text.index(start)
        if end is None:
            b = len(self.text)
        else:
            i = self.text.find(end, a)
            if i < 0:
                LEDGER.append(dict(status="FAIL", kind="anchor", loc=f"{self.loc}: sub-anchor end {end[:50]}", printed="", value=0.0,
                                   note="END SNIPPET NOT FOUND AFTER THE START"))
                return Passage(self.loc, 0, 0, ok=False)
            b = i + len(end)
        return Passage(f"{self.loc} > {start[:28]}", self.start + a, self.start + b)

    # -- bookkeeping
    def _take(self, printed, kind):
        key = norm(printed)
        for a, b, t in self.toks:
            if t == key and a not in COVER:
                COVER[a] = kind
                return a
        return None

    def _add(self, status, kind, label, printed, value, note=""):
        LEDGER.append(dict(status=status, kind=kind, loc=f"{self.loc}: {label}", printed=printed, value=value, note=note))
        return status == "ok"

    def _missing(self, kind, printed, value):
        return self._add("FAIL", kind, printed, printed, value,
                         "NUMBER NOT FOUND (OR ALREADY USED) IN THE ANCHORED PASSAGE" if self.ok else "ANCHOR NOT FOUND")

    # -- numeric comparisons
    def v(self, printed, value, note="", label=None):
        """printed equals the pipeline value rounded to the printed decimals (sign read from the text)."""
        a = self._take(printed, "value")
        if a is None:
            return self._missing("value", printed, value)
        sg = text_sign(a)
        d = len(printed.split(".")[1]) if "." in printed else 0
        p = Decimal(norm(printed)) * sg
        ok = p in (rnd(value, d), rnd(value, d, ROUND_HALF_EVEN))
        return self._add("ok" if ok else "FAIL", "value", label or (("-" if sg < 0 else "") + printed), printed, float(value), note)

    def _cmp(self, printed, value, op, note, label):
        a = self._take(printed, "value")
        if a is None:
            return self._missing("value", printed, value)
        b = float(Decimal(norm(printed))) * text_sign(a)
        ok = {"gt": value > b, "ge": value >= b, "lt": value < b, "le": value <= b}[op]
        sym = {"gt": ">", "ge": ">=", "lt": "<", "le": "<="}[op]
        return self._add("ok" if ok else "FAIL", "value", label or f"value {sym} {printed}", printed, float(value), note)

    def gt(self, printed, value, note="", label=None):
        return self._cmp(printed, value, "gt", note, label)

    def ge(self, printed, value, note="", label=None):
        return self._cmp(printed, value, "ge", note, label)

    def lt(self, printed, value, note="", label=None):
        return self._cmp(printed, value, "lt", note, label)

    def le(self, printed, value, note="", label=None):
        return self._cmp(printed, value, "le", note, label)

    def about(self, printed, value, tol, note=""):
        """'about 23%': |value - printed| <= tol (the tolerance is stated in the call)."""
        a = self._take(printed, "value")
        if a is None:
            return self._missing("value", printed, value)
        b = float(Decimal(norm(printed))) * text_sign(a)
        return self._add("ok" if abs(value - b) <= tol else "FAIL", "value", f"about {printed} (tol {tol})", printed, float(value), note)

    def _word_match(self, word):
        pat = re.compile(r"(?<![A-Za-z\\])" + re.escape(word).replace(r"\ ", r"\s+") + r"(?![A-Za-z])", re.I)
        for m in pat.finditer(self.mtext):
            a = self.start + m.start()
            if not any(a + k in COVERW for k in range(len(m.group(0)))):
                return a, a + len(m.group(0))
        return None

    def w(self, word, value, note="", tol=1e-9):
        """a number written as a word or phrase ('sixteen', 'one half'): the phrase must occur (unused) in the passage and
        its numeric meaning (WORDS) must equal the pipeline value within tol."""
        m = self._word_match(word) if self.ok else None
        key = word.lower()
        if m is None or key not in WORDS:
            return self._add("FAIL", "word", word, word, float(value) if value is not None else 0.0,
                             ("PHRASE NOT FOUND (OR USED) IN THE ANCHORED PASSAGE" if self.ok else "ANCHOR NOT FOUND") if m is None
                             else "PHRASE NOT IN WORDS")
        for k in range(m[0], m[1]):
            COVERW[k] = "value"
        return self._add("ok" if abs(WORDS[key] - float(value)) <= tol else "FAIL", "word", word, word, float(value), note)

    def wpin(self, word, why=""):
        """number word that is part of the text's own structure or an idiom: pinned to the text"""
        m = self._word_match(word) if self.ok else None
        if m is None:
            return self._add("FAIL", "word", word, word, 0.0, "PHRASE NOT FOUND (OR USED) IN THE ANCHORED PASSAGE")
        for k in range(m[0], m[1]):
            COVERW[k] = "pin"
        PINS.append((lineno(m[0]), word, why))
        return self._add("ok", "pin", word, word, 0.0, why)

    # -- dates
    def _find_date(self, printed):
        """locate the date phrase `printed` ('27 September 2026', '4--11 August 2025', 'Sep.\\ 2026', 'October') in the passage with
        none of its numerals or its month name used; returns (parts, offsets) or None"""
        pm = re.fullmatch(r"(?:(\d{1,2})(?:--(\d{1,2}))?\s+)?(" + _MONTH_NAMES + r")(\.)?(?:(?:\\ |\s)+(\d{4}))?", printed)
        if pm is None or not self.ok:
            return None
        d0, d1_, month, dot, year = pm.groups()
        pat = ""
        if d0:
            pat += r"(?<![\d.,])(?<!\d-)(?<!\d--)(" + d0 + r")" + (r"--(" + d1_ + r")" if d1_ else r"()") + r"(?:\s|~|\\ )+"
        else:
            pat += r"()()"
        pat += r"(?<![A-Za-z\\])(" + month + r")" + (r"\." if dot else r"(?![A-Za-z.])")
        pat += (r"(?:\s|~|\\ )+(" + year + r")(?!\d)") if year else r"()"
        toks_at = {a for a, b, t in self.toks if a not in COVER}
        for m in re.finditer(pat, self.mtext):
            off = [self.start + m.start(g) if m.group(g) else None for g in (1, 2, 3, 4)]
            if (off[0] is None or off[0] in toks_at) and (off[1] is None or off[1] in toks_at) and (off[3] is None or off[3] in toks_at) \
                    and off[2] not in COVERM:
                return (d0, d1_, month, year), off
        return None

    def dt(self, printed, ts, ts_end=None, note=""):
        """a date printed as 'D Month YYYY', 'D Month', 'D--D Month YYYY', 'Month YYYY' or 'Month' (also abbreviated, 'Sep.\\ 2026'):
        day, month name and year are compared with the timestamp ts (and, for a range of days, ts_end) of the pipeline record; the
        phrase must occur in the passage with none of its numerals used, so that a month name cannot be matched to another date"""
        f = self._find_date(printed)
        if f is None:
            return self._add("FAIL", "date", printed, printed, str(ts)[:10], "DATE PHRASE NOT FOUND (OR USED) IN THE ANCHORED PASSAGE" if self.ok else "ANCHOR NOT FOUND")
        (d0, d1_, month, year), off = f
        for k in (0, 1, 3):
            if off[k] is not None:
                COVER[off[k]] = "value"
        COVERM[off[2]] = "value"
        last = ts_end if ts_end is not None else ts
        ok = month in (MONTH_FULL[ts.month], MONTH_ABBR[ts.month], "Sept" if ts.month == 9 else "-") and month in (
            MONTH_FULL[last.month], MONTH_ABBR[last.month], "Sept" if last.month == 9 else "-")
        if d0:
            ok = ok and int(d0) == ts.day
        if d1_:
            ok = ok and ts_end is not None and int(d1_) == ts_end.day
        if year:
            ok = ok and int(year) == ts.year == last.year
        return self._add("ok" if ok else "FAIL", "date", printed, printed, str(ts)[:10] + ("" if ts_end is None else " to " + str(ts_end)[:10]), note)

    def dtpin(self, printed, why=""):
        """a date that no pipeline record can back (a vendor announcement, an external release): pinned to the text"""
        f = self._find_date(printed)
        if f is None:
            return self._add("FAIL", "pin", printed, printed, 0.0, "DATE PHRASE NOT FOUND (OR USED) IN THE ANCHORED PASSAGE" if self.ok else "ANCHOR NOT FOUND")
        _, off = f
        for k in (0, 1, 3):
            if off[k] is not None:
                COVER[off[k]] = "pin"
        COVERM[off[2]] = "pin"
        PINS.append((lineno(off[2]), printed, why))
        return self._add("ok", "pin", printed, printed, 0.0, why)

    def cond(self, label, ok, value=0.0, note="", printed=""):
        """a claim that is a condition on pipeline values rather than a rounding comparison"""
        return self._add("ok" if ok else "FAIL", "cond", label, printed, float(value), note)

    # -- pins and open items
    def pin(self, *printed, why=""):
        """numbers that no pipeline value can back (dates, vendor prices, labels, equation indices, quoted literature):
        pinned to the text"""
        for pr in printed:
            a = self._take(pr, "pin")
            if a is None:
                self._missing("pin", pr, 0.0)
            else:
                PINS.append((lineno(a), pr, why))
                self._add("ok", "pin", pr, pr, 0.0, why)

    def pin_rest(self, *expected, why=""):
        """pin the numerals of the passage that no check has consumed. They must be exactly the `expected` ones, in order of
        appearance, so that a changed, added or deleted number is found; without `expected` the passage must have no numeral
        left (a number added to the sentence is then reported instead of being absorbed)."""
        if not self.ok:
            return
        rest = [(a, b, t) for a, b, t in self.toks if a not in COVER]
        got, want = [t for a, b, t in rest], [norm(e) for e in expected]
        if got != want:
            self._add("FAIL", "pin", "numerals left over", " ".join(got), 0.0,
                      f"PINNED NUMERALS CHANGED: expected {want}, found {got}")
            return
        if not rest:
            self._add("ok", "cond", "no numeral left over in the passage", "", 0.0, why)
        for a, b, t in rest:
            COVER[a] = "pin"
            PINS.append((lineno(a), TEX[a:b], why))
            self._add("ok", "pin", TEX[a:b], TEX[a:b], 0.0, why)

    def notation(self, why="mathematical notation"):
        """single digits that occur inside mathematical notation (subscripts, 'beta = 1', '0 < q_F') and that no check has
        consumed: recorded as notation. Digit strings of two or more digits and decimals are never absorbed."""
        for a, b, t in self.toks:
            if a not in COVER and re.fullmatch(r"\d", t) and in_math(a):
                COVER[a] = "notation"

    def open(self, printed, value, documented, note="", label=None):
        """a printed number whose sentence, read literally, defines a pipeline quantity that the number does not match, and whose
        repair (wording or definition of the sentence) is the author's decision: documented as an unresolved entry, not failed.
        `printed` is the number the text states now, `documented` the number for which the entry was written. The number is compared
        like any other (P.v): once the text states a number that the pipeline reproduces, the entry is a pass; a text that states
        another number which the pipeline does not reproduce either is a failure (the entry must then be reviewed)."""
        a = self._take(printed, "value")
        if a is None:
            return self._missing("open", printed, value)
        d = len(printed.split(".")[1]) if "." in printed else 0
        p = Decimal(norm(printed)) * text_sign(a)
        if p in (rnd(value, d), rnd(value, d, ROUND_HALF_EVEN)):
            return self._add("ok", "value", label or printed, printed, float(value), note)
        if norm(printed) != norm(documented):
            return self._add("FAIL", "open", label or printed, printed, float(value),
                             "THE UNRESOLVED NUMBER CHANGED: the entry documents %s, the text now prints %s, which the pipeline value does not "
                             "reproduce either" % (documented, printed))
        COVER[a] = "open"
        return self._add("open", "open", label or printed, printed, float(value), note)

    def open_cond(self, label, ok, value, printed=None, note=""):
        """a claim that is a condition on pipeline values (like P.cond) and that fails under the literal reading of its sentence
        in a way that only a wording decision of the author can repair (for example 'the only slopes beyond +-0.01 are A and B'
        when a third pair's slope is 0.011): recorded as an unresolved entry, like P.open, not as a failure. `printed` is the
        numeral of the claim, which the entry consumes; `value` is the pipeline value that contradicts the claim."""
        a = self._take(printed, "value" if ok else "open") if printed else None
        if printed and a is None:
            return self._missing("open", printed, value)
        return self._add("ok" if ok else "open", "open", label, printed or "", float(value), note)


def S(start, end=None, loc=None):
    """Anchor: the text of main.tex from the exact snippet `start` (which must occur once) to the end of the first
    occurrence of `end` after it, or to the end of the line (= the paragraph) when `end` is omitted."""
    n = TEX.count(start)
    label = loc or (start[:34].replace("\n", " ") + "...")
    if n != 1:
        LEDGER.append(dict(status="FAIL", kind="anchor", loc=f"text anchor: {start[:60]}", printed="", value=float(n),
                           note="ANCHOR OCCURS %d TIMES (must be exactly once)" % n))
        return Passage(label, 0, 0, ok=False)
    a = TEX.index(start)
    if end is None:
        b = TEX.find("\n", a)
        b = len(TEX) if b < 0 else b
    else:
        i = TEX.find(end, a)
        if i < 0:
            LEDGER.append(dict(status="FAIL", kind="anchor", loc=f"text anchor end: {end[:60]}", printed="", value=0.0,
                               note="END SNIPPET NOT FOUND AFTER THE START"))
            return Passage(label, 0, 0, ok=False)
        b = i + len(end)
    return Passage(f"L{lineno(a)} {label}", a, b)


def check_in_text(snippet):
    """Assert that the exact snippet occurs in main.tex (no numeral consumed)."""
    ok = TEX.count(snippet) >= 1
    LEDGER.append(dict(status="ok" if ok else "FAIL", kind="text", loc="text contains: " + snippet[:70], printed="", value=0.0,
                       note="" if ok else "SNIPPET NOT FOUND"))
    return ok


def csv(name, folder=AO):
    return pd.read_csv(folder / name)


def pcsv(name, **kw):
    return pd.read_csv(PROC / name, keep_default_na=False, na_values=[""], **kw)


# ------------------------------------------------------------------------------------------------ masking and coverage
def _blank(tex, rngs):
    s = list(tex)
    for a, b in rngs:
        for i in range(a, b):
            if s[i] != "\n":
                s[i] = " "
    return "".join(s)


def _math_spans(tex):
    """character spans of mathematical notation: $...$ and equation environments"""
    spans, i, n = [], 0, len(tex)
    while i < n:
        c = tex[i]
        if c == "%":
            j = tex.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "\\" and i + 1 < n:
            if tex.startswith("\\begin{equation}", i):
                j = tex.index("\\end{equation}", i)
                spans.append((i, j))
                i = j + 14
                continue
            if tex.startswith("\\[", i):                     # display mathematics \[ ... \] (the proofs of Appendix A)
                j = tex.index("\\]", i)
                spans.append((i, j + 2))
                i = j + 2
                continue
            i += 2
            continue
        if c == "$":
            j = i + 1
            while j < n and not (tex[j] == "$" and tex[j - 1] != "\\"):
                if tex[j] == "\\":
                    j += 1
                j += 1
            spans.append((i, j + 1))
            i = j + 1
            continue
        i += 1
    return spans


MATH = _math_spans(TEX)
MATH_A = [a for a, b in MATH]


def in_math(pos):
    k = bisect.bisect_right(MATH_A, pos) - 1
    return k >= 0 and MATH[k][0] <= pos < MATH[k][1]


def prose_mask(tex):
    """main.tex with everything blanked that is not prose: preamble (but not the title block), comments, labels, references,
    citations, URLs, file names and layout arguments"""
    rngs = [(0, tex.index("\\title{"))]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"(?<!\\)%[^\n]*", tex)]
    for cmd in ["label", "ref", "eqref", "pageref", "tabinput", "nolinkurl", "url", "includegraphics", "bibliographystyle",
                "bibliography"]:
        rngs += [(m.start(), m.end()) for m in re.finditer(r"\\" + cmd + r"\*?(\[[^\]]*\])?\{[^}]*\}", tex)]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\texttt\{[^}]*\.zip\}", tex)]                         # file names of the deposited archives
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\cite[a-z]*\*?(\[[^\]]*\])*\{[^}]*\}", tex)]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\href\{[^}]*\}\{[^}]*\}", tex)]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\begin\{(tabularx|tabular)\}(\{[^}]*\})?(\{(?:[^{}]|\{[^{}]*\})*\})", tex)]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\(multicolumn|cmidrule)(\([a-z]*\))?\{[^}]*\}(\{[^}]*\})?", tex)]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\(setlength|counterwithin|setstretch|hspace|vspace)\*?\{[^}]*\}(\{[^}]*\})?", tex)]
    rngs += [(m.start(), m.end()) for m in re.finditer(r"\\renewcommand\{\\arraystretch\}\{[^}]*\}", tex)]          # row-spacing factor of a table (layout)
    rngs += [(m.start(), m.end()) for m in re.finditer(
        r"\\begin\{(table|figure|tablenotes|enumerate|aproposition|proposition|remark|proof)\}(\[[^\]]*\])?", tex)]
    return _blank(tex, rngs)


MASKED = prose_mask(TEX)


# ================================================================================================ data and derived quantities
panel = pcsv("country_panel.csv").copy()                # "NA" is Namibia: keep_default_na=False
prices = pcsv("appstore_prices_long.csv")               # wave 1, one row per storefront and plan
wide = pcsv("appstore_prices_wide.csv")
raw1 = [json.loads(l) for l in open(ROOT / "data" / "raw" / "appstore" / "appstore_iap_raw.jsonl")]
raw2 = [json.loads(l) for l in open(ROOT / "data" / "raw" / "appstore_wave2" / "core" / "appstore_iap_raw_wave2.jsonl")]
rawd = [json.loads(l) for l in open(ROOT / "data" / "raw" / "appstore_wave2" / "default_panel" / "appstore_iap_raw_wave2_default.jsonl")]
items = pcsv("wave2_items_long.csv")                    # wave 2, one row per storefront and item
pvd = pcsv("wave2_plan_vs_default.csv")                 # wave 2, the 28 plans against the revealed default
ladder = pcsv("wave2_default_ladder.csv")
mult = pcsv("wave2_default_multiplier.csv")
islopes = pcsv("wave2_item_slopes.csv")
W1 = pd.read_csv(ROOT / "output" / "tables" / "W1_wave2_plans.csv", keep_default_na=False, na_values=[""]).set_index("plan")
W2 = pd.read_csv(ROOT / "output" / "tables" / "W2_benchmarks.csv", keep_default_na=False, na_values=[""]).set_index("key")
W5 = pd.read_csv(ROOT / "output" / "tables" / "W5_item_classes.csv", keep_default_na=False, na_values=[""]).set_index(["item_class", "type"])
A1 = pd.read_csv(ROOT / "output" / "tables" / "A1_burden_by_group.csv", keep_default_na=False, na_values=[""]).set_index("group")
A2 = pd.read_csv(ROOT / "output" / "tables" / "A2_burden_by_quintile.csv", keep_default_na=False, na_values=[""]).set_index("group")
pol = csv("policy_counterfactuals_groups.csv").set_index("group")
POLJ = json.load(open(AO / "audit_results_policy.json"))
GROUPS = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]
SH = {"High income": "HIC", "Upper-middle income": "UMIC", "Lower-middle income": "LMIC", "Low income": "LIC"}
gni = panel.dropna(subset=["gni_atlas"]).copy()          # the 201 economies with GNI per capita
gni["aab20"] = 1200 * 20 / gni["gni_atlas"]


def grp_median(df, col, group):
    return float(df.loc[df.income_group == group, col].median())


def has_local(df, plan):
    return df[(df.plan == plan) & df.price_local.notna()]


# second-wave app classes and the plan list of Table 3
APPS = json.load(open(ROOT / "data" / "raw" / "appstore_wave2" / "apps_v3.json"))        # app -> {id, class}
W1["cls"] = W1.app.map(lambda a: APPS[a]["class"])                                          # class of the app that sells each plan
rows2 = pcsv("wave2_plan_rows.csv")                                                          # wave 2, plan x storefront rows after the guard (code/09b)


# ------------------------------------------------------------------------------------------------ constants read from the pipeline code
SRC10 = (ROOT / "code" / "10_build_dataset.py").read_text()
FINDEX_EDITION = int(re.search(r"Global Findex (\d{4})", SRC10).group(1))                   # edition named in the dataset builder
FY_CLASS = int(re.search(r"FY(\d{4}) classification", SRC10).group(1))                       # fiscal year of the income classification
AGE_UP = int(re.search(r"SP\.POP\.(\d\d)UP\.TO\.ZS", SRC10).group(1))                          # age threshold of the old-age population share
AAB_F = re.search(r"def aab\(price, denom\):\s*return ([0-9.]+) \* price / denom \* ([0-9.]+)", (ROOT / "code" / "20_analysis.py").read_text())
AAB_MONTHS, AAB_PCT = float(AAB_F.group(1)), float(AAB_F.group(2))                           # 12 months, factor 100 of the burden
PCT_F = re.search(r"return float\((\d+) \* \(math\.exp\(x\) - (\d+)\)\)", (ROOT / "code" / "12_default_panel.py").read_text())
PCT_CONV, PCT_ONE = int(PCT_F.group(1)), int(PCT_F.group(2))                                 # 100 (e^d - 1) of a log deviation
FIG_SCALE = int(re.search(r"(\d+) \* z\.dev_log", (ROOT / "code" / "31_figures_wave2.py").read_text()).group(1))      # axis of Figure 2: 100 x log deviation
SRC12 = (ROOT / "code" / "12_default_panel.py").read_text() + (ROOT / "code" / "wave2_common.py").read_text()   # schedule()/modal() live in wave2_common.py since v3.1
SRC09B = (ROOT / "code" / "09b_wave2_items.py").read_text()
SRC13 = (ROOT / "code" / "13_relative_prices.py").read_text()
SRC14 = (ROOT / "code" / "14_default_validation.py").read_text()
SRC15 = (ROOT / "code" / "15_vintage_test.py").read_text()
SRC16 = (ROOT / "code" / "16_cross_channel.py").read_text()


def grab(src, pat, name):
    m = re.search(pat, src)
    if not m:
        raise SystemExit(f"prose_number_audit: cannot read the constant {name} from the pipeline code (pattern {pat!r})")
    return float(m.group(1))


THR_WITHIN = grab(SRC12, r"within3=float\(\(c\.dev_log\.abs\(\) <= ([0-9.]+)\)", "within-band")                 # 0.03
THR_BELOW = -grab(SRC12, r"below10=float\(\(c\.dev_log < (-[0-9.]+)\)", "below-threshold")                        # 0.10
THR_CLEAN = grab(SRC12, r"clean_sf = \{sf for sf, v in mult\.items\(\) if v\[2\] < ([0-9.]+)\}", "clean spread")    # 0.2
THR_AT_DEFAULT = grab(SRC12, r"at_default_n=int\(\(c\.dev_log\.abs\(\) <= ([0-9.]+)\)", "at-default band")        # 0.005
MIN_ITEMS_POINT = grab(SRC12, r"def schedule\(d, rule=MAIN, min_items=([0-9]+)\)", "items per price point")         # 3
MIN_POINTS_MULT = grab(SRC12, r"if len\(ms\) >= ([0-9]+):", "points per multiplier")                                  # 3
POINT_MIN_USD = grab(SRC12, r"p >= ([0-9.]+) and e\[", "lowest price point of the multiplier")                         # 2.99
MODE_SHARE = 1 / grab(SRC12, r"else (\d) \* top >= n", "mode share")                                                     # 1/2
MIN_STORES_ITEM = grab(SRC09B, r"if len\(g\) < ([0-9]+):", "storefronts per item")                                   # 60
THR_SLOPE = grab(SRC09B, r"share_gt_010=float\(\(s > ([0-9.]+)\)", "slope threshold")                               # 0.10
ANNUAL_CUT = grab(SRC09B, r"x < ([0-9]+) \* p\[0\]", "annual-variant cutoff")                                       # 5
STAB_TOL = grab(SRC09B, r"abs\(a - b\) < ([0-9.]+) \* max\(a, b\)", "stability tolerance")                          # 0.005
RATIO_LO = grab(SRC09B, r"\(g\.ratio_us > ([0-9.]+)\)", "lower ratio bound")                                       # 0.05
RATIO_HI = grab(SRC09B, r"\(g\.ratio_us < ([0-9.]+)\)", "upper ratio bound")                                       # 20
GUARD_K = grab(SRC09B, r"\nGUARD_K = ([0-9]+)", "annual-as-monthly guard multiple")                                 # 3
N_PERM = grab(SRC13, r"SEED, N_PERM = \d+, ([0-9]+)", "permutations of the randomisation inference")             # 2,000
RI_SEED = grab(SRC13, r"SEED, N_PERM = ([0-9]+), \d+", "seed of the randomisation inference")                      # 20261016
MASS_BAND = grab(SRC13, r"mass_at1=float\(\(d\.abs\(\) < ([0-9.]+)\)", "band of the mass at a relative price of one")   # 0.005
BELOW09 = grab(SRC13, r"share_below09=float\(\(d < math\.log\(([0-9.]+)\)", "threshold of the share below 0.9")   # 0.9
FRONTIER_US = grab(SRC13, r'FRONTIER, FRONTIER_US = \[[^\]]*\], ([0-9.]+)', "U.S. price of the frontier numeraire")   # 19.99
N_SPLITS = grab(SRC14, r"SEED, N_SPLITS = \d+, ([0-9]+)", "split-half repetitions")                                # 300
SPLIT_SEED = grab(SRC14, r"SEED, N_SPLITS = ([0-9]+), \d+", "seed of the split-half test")                         # 20261016
ANOM_FX = grab(SRC14, r"> math\.log\(([0-9.]+)\)\)", "departure from exchange-rate parity")                        # 1.20
FX_STABLE = grab(SRC15, r"STABLE, MOVED, BAND = math\.log\(([0-9.]+)\)", "stable-currency threshold")              # 1.1
FX_MOVED = grab(SRC15, r"STABLE, MOVED, BAND = math\.log\([0-9.]+\), math\.log\(([0-9.]+)\)", "moved-currency threshold")   # 1.3
VINT_BAND = grab(SRC15, r"STABLE, MOVED, BAND = math\.log\([0-9.]+\), math\.log\([0-9.]+\), ([0-9.]+)", "vintage within-band")   # 0.03
XCH_BAND = grab(SRC16, r"\nBAND = ([0-9.]+)", "cross-channel within-band")                                          # 0.05
XCH_EXACT = grab(SRC16, r"float\(\(np\.abs\(comp\) < ([0-9.]+)\)\.mean\(\)\)", "cross-channel identical band")       # 0.005: 'identical' = |ln difference| < 0.005 (Google Play)
MS_WITHIN05 = grab(SRC16, r"_within05\", float\(\(np\.abs\(ld\) < ([0-9.]+)\)\.mean\(\)\)", "Microsoft within-0.5% band")   # 0.005: |ln(web / App Store)| < 0.005


# ------------------------------------------------------------------------------------------------ closed forms of Appendix A
from scipy.optimize import brentq
from scipy.stats import norm as snorm


def hazard(z):
    """standard normal hazard lambda(z) = phi(z) / (1 - Phi(z))"""
    return np.exp(snorm.logpdf(z) - snorm.logsf(z))


def beta_ln(L, s):
    """Proposition A.2, equation (A.8): income elasticity of the optimal price increment for lognormal valuations with
    dispersion s and marginal-cost share L: beta = lam' / (lam' + lam (lam - s)), lam' = lam (lam - z), lam(z*) = s / (1 - L)"""
    target = s / (1.0 - L)
    z = brentq(lambda t: hazard(t) - target, -50.0, 1e5, xtol=1e-14, rtol=1e-14)
    lam = float(hazard(z))
    lam1 = lam * (lam - z)
    return lam1 / (lam1 + lam * (lam - s))


def mills(z):
    """inverse Mills ratio of the lower tail h(z) = phi(z) / Phi(z)"""
    return snorm.pdf(z) / snorm.cdf(z)


def bstar(share_use, share_pay_of_users):
    """beta* = 1 - h(z_D) / h(z_L) with Phi(z_D) = share_use and Phi(z_L) = share_pay_of_users * share_use (Proposition A.1)"""
    return 1 - mills(snorm.ppf(share_use)) / mills(snorm.ppf(share_use * share_pay_of_users))


# ================================================================================================ shared quantities
d1, d2 = pd.Timestamp(R2["wave1_fetch_date_utc"]), pd.Timestamp(R2["wave2_fetch_date_utc"])
us1 = prices[prices.storefront == "us"].set_index("plan").price_local          # U.S. App Store prices, wave 1
us2 = W1.us_price                                                               # U.S. App Store prices, wave 2 (plan table)
CLS = pd.Series({a: v["class"] for a, v in APPS.items()})
N_CORE, N_OTHER_AI = int((CLS == "ai_core").sum()), int(CLS.isin(["ai", "ai_bundle"]).sum())
N_NONAI, N_AIFEAT = int((CLS == "nonai").sum()), int((CLS == "ai_feature").sum())
STD = ["chatgpt_plus", "claude_pro", "gemini_pro", "perplexity_pro", "m365_premium"]                       # $20 standard tiers
STD_PRICE = float(np.median([us2[k] for k in STD]))                                                       # the $20 standard tier (median U.S. price of the five)
HIGH = ["chatgpt_pro100", "chatgpt_pro200", "claude_max5x", "claude_max20x", "gemini_ultra", "supergrok_heavy"]   # $100-300 tiers
FRONTIER = ["chatgpt_plus", "chatgpt_pro200", "claude_pro", "claude_max20x", "gemini_pro", "gemini_ultra", "perplexity_pro",
            "supergrok", "m365_premium"]                                                                      # the nine frontier tiers
p95_p5 = float(gni.gni_atlas.quantile(0.95) / gni.gni_atlas.quantile(0.05))
ro = pd.read_csv(ROOT / "data" / "raw" / "openai" / "chatgpt_go_rollout.csv", keep_default_na=False)
ro["date"] = pd.to_datetime(ro.first_available)
MAN_DATES = sorted({m["retrieved_utc"][:10] for m in json.load(open(ROOT / "extensions" / "pricing_sources" / "manifest.json"))})   # retrieval dates of the vendor pages


def iso_of(day, month_name, year):
    """ISO date of a date printed as '29 September 2026'"""
    return f"{int(year):04d}-{list(calendar.month_name).index(month_name):02d}-{int(day):02d}"


def date_is(P, ts, day, month, year=None, note=""):
    """a date printed as 'day month' or 'day month year': day, month name and year are compared with the timestamp ts of the
    pipeline record, and the phrase must occur as such in the passage (a month name cannot be matched to another date)"""
    P.dt(f"{day} {month}" + (f" {year}" if year else ""), ts, note=note)


day_month_is = date_is


def month_year_is(P, ts, month, year, note=""):
    """a period printed as 'November 2025'"""
    P.dt(f"{month} {year}", ts, note=note)




def n_leads(start, end):
    """number of paragraphs that open with an emphasised lead (\\emph{...}) between two snippets of the manuscript"""
    a = TEX.index(start)
    return len(re.findall(r"^\\emph\{", TEX[a:TEX.index(end, a)], re.M))


PG = {"US": R2["plusgo_ratio_us"], "HIC": R2["plusgo_ratio_HIC"], "UMIC": R2["plusgo_ratio_UMIC"],
      "LMIC": R2["plusgo_ratio_LMIC"], "LIC": R2["plusgo_ratio_LIC"]}
N_WAVES = len({R2["wave1_fetch_date_utc"], R2["wave2_fetch_date_utc"]})
MULT_ALLOW = sorted({int(m.group(1)) for k in list(W1.index) + list(prices.plan.unique()) for m in [re.search(r"(\d+)x$", k)] if m})   # 5 and 20: usage multiples in the plan names
N_OPT = 1 + len(re.search(r"k\\in\\\{([A-Z,]+)\\\}", S("u_0=0,\\qquad u_k=vq_k").text.replace("\n", " ")).group(1).split(","))
N_THR = S("T_{D,c}\\equiv", "\\label{eq:nested_condition}").text.count("<") + 1
TAB = ROOT / "paper_en" / "tables"                                                      # the generated table bodies (row counts and plan lists are read from them)
N_PRED = len(re.findall(r"\\item", S("\\begin{enumerate}[label=(P\\arabic*),leftmargin=*]", "\\end{enumerate}").text))   # five predictions P1-P5

# ================================================================================================ title block
_vm = re.search(r"version (\d\.\d) \(compile", TEX)                         # manuscript version named in the header comment of main.tex
VERSION = _vm.group(1) if _vm else "3.1"                                     # (the anonymised copy may drop the comment: the pins below then use the version of this audit)
if not ANON_COPY:          # the author line and the date of the identified manuscript are absent from the anonymised copy
    p = S("An earlier version circulated as SSRN working paper")
    p.pin(re.search(r"SSRN working paper (\d+)", p.text).group(1), why="SSRN abstract number of the earlier version (title page)")
    p.pin(VERSION, why="version of this manuscript (the header comment of main.tex names the same version)")
    p.dt("October 2026", d2, note="this version is dated in the month of the second audit (the latest data)")
    S("\\date{October 2026}\n\\fi", "2026}").dt("October 2026", d2, note="date line of the identified manuscript (the \\else branch)")
# the date line of the anonymised branch (both branches carry \date{October 2026}; the anonymised copy keeps this one only)
S("\\author{~}\n\\date{", "October 2026}").dt("October 2026", d2, note="date line of the anonymised manuscript")

# ================================================================================================ Abstract
STAB_PLANS = sorted({m.group(1) for k in R2 for m in [re.fullmatch(r"stab_(.+)_compared", k)] if m and m.group(1) != "all"})
HIGH500 = HIGH + ["chatgpt_pro500"]                                                                     # the $100-500 high-usage tiers
FRONT13 = ["chatgpt_plus", "chatgpt_pro100", "chatgpt_pro200", "chatgpt_pro500", "claude_pro", "claude_max5x", "claude_max20x",
           "gemini_pro", "gemini_ultra", "perplexity_pro", "supergrok", "supergrok_heavy", "m365_premium"]   # the $20 and $100-500 tiers of the six vendors (Table 5)
VENDORS6 = {"chatgpt": "OpenAI", "claude": "Anthropic", "gemini": "Google", "perplexity": "Perplexity", "supergrok": "xAI", "m365": "Microsoft"}
N_VENDORS = len({k.split("_")[0] for k in FRONT13})                                                        # six vendors
W8 = pd.read_csv(ROOT / "output" / "tables" / "W8_relative_pairs.csv", keep_default_na=False, na_values=[""])   # the 22 within-firm pairs of Table 3 (code/13)
N_PAIRS = len(W8)
PAIRS_FF = list(W8[(W8.group_a == "frontier") & (W8.group_b == "frontier")].pair)             # the nine pairs of two frontier tiers of the same firm
YTX_PLANS = ["youtube_premium", "youtube_premium_lite", "youtubemusic_music", "x_premium", "x_premium_basic"]   # "the same firms' YouTube and X Premium subscriptions"
PAIRS_YTX = list(W8[W8.plan_a.isin(YTX_PLANS)].pair)                                             # their seven pairs in Table 3 (against AI Pro, SuperGrok, X Premium Plus, SuperGrok Lite)
PAIRS_CAPPED = ["go_plus", "aiplus_aipro", "sglite_supergrok", "cai_lite_plus"]                       # capped tier against the tier above it
LOC_CAPPED = [k for k in PAIRS_CAPPED if R2[f"rel_{k}_lmic_med"] < BELOW09]                            # localised capped tiers: Go, Character.AI Lite
A = S("Generative-AI assistants are sold through one subscription menu", "median low-income one.")
A.w("hundredfold", p95_p5, tol=10,
    note="rhetorical: ratio of the 95th to the 5th percentile of GNI per capita across the 201 economies (within 10 of 100)")
A.w("Two", N_WAVES, note="two audit waves")
A.w("six", N_OTHER_AI, note="apps of class ai (5) and ai_bundle (1) in apps_v3.json")
A.v("21", N_NONAI)
A.w("four", N_AIFEAT, note="apps with AI features (class ai_feature)")
A.v("20", np.median([us2[k] for k in STD]), note="median U.S. App Store price of the five $20 standard tiers")
A.cond("all five standard-tier U.S. prices round to the median standard-tier price", all(round(us2[k]) == round(np.median([us2[j] for j in STD])) for k in STD))
A.v("100", min(us2[k] for k in HIGH500), note="cheapest high-usage tier")
A.v("500", max(us2[k] for k in HIGH500), note="ChatGPT Pro 500")
A.le("0.022", R2["rel_frontierpairs_abs_slope_max"], note="'absolute slopes at most 0.022': largest |slope| of the nine within-firm pairs of two frontier tiers (ChatGPT Pro 500 relative to Plus, -0.0219; key rel_frontierpairs_abs_slope_max)",
     label="absolute slopes at most 0.022")
A.cond("the frontier-pair bound of results_wave2.json is the max |slope| over the nine pairs of W8_relative_pairs.csv whose two plans are both frontier tiers, and it rounds to the printed 0.022",
       R2["rel_frontierpairs_n_pairs"] == len(PAIRS_FF) == 9 and abs(max(abs(R2[f"rel_{k}_slope"]) for k in PAIRS_FF) - R2["rel_frontierpairs_abs_slope_max"]) < 1e-9
       and rnd(R2["rel_frontierpairs_abs_slope_max"], 3) == Decimal("0.022"), len(PAIRS_FF))
A.v("50", 100 * (1 - max(R2[f"rel_{k}_lmic_med"] for k in PAIRS_YTX)), note="smallest LMIC discount of the YouTube and X Premium pairs (X Premium Basic vs SuperGrok and vs SuperGrok Lite, median relative price 0.50)")
A.v("73", 100 * (1 - min(R2[f"rel_{k}_lmic_med"] for k in PAIRS_YTX)), note="largest LMIC discount (YouTube Premium Lite vs Google AI Pro, 0.266; YouTube Music 0.268)")
A.v("15", 100 * (1 - R2["rel_m365pers_prem_lmic_med"]), note="Microsoft 365 Personal relative to Premium: median relative price 0.85 in LMIC storefronts")
A.w("Two", len(LOC_CAPPED), note="capped AI tiers whose median relative price in LMIC storefronts is below 0.9: ChatGPT Go and Character.AI Lite")
A.about("40", 100 * (1 - R2["rel_go_plus_lmic_med"]), 3.0, note="'about 40% cheaper': ChatGPT Go relative to Plus 37.5%, Character.AI Lite relative to Character.AI+ 40.1% (both within 3 points)")
A.cond("Character.AI Lite is also about 40% cheaper (within 3 points)", abs(100 * (1 - R2["rel_cai_lite_plus_lmic_med"]) - 40) <= 3, 100 * (1 - R2["rel_cai_lite_plus_lmic_med"]))
A.v("30", R2["default_apps"])
A.cond("'Google Play's lowest ChatGPT price and Microsoft's web prices match the App Store': Play within 5% of the App Store Go price in most same-currency countries, Microsoft's web prices within 5% in every comparison",
       R2["xch_play_chatgpt_within5"] > 0.5 and R2["xch_ms_web_vs_app_premium_within5"] == 1 == R2["xch_ms_web_vs_app_personal_within5"], R2["xch_play_chatgpt_within5"])
A.w("four", N_OPT, note="four options of Appendix A: non-use, F, L, H (u_0 and u_k for k in {F, L, H})")
A.cond("'the frontier-to-entry dollar gap widens where incomes are low': the Plus-Go increment slope is negative and more than two s.e. below zero",
       R2["incr_plus_go_slope"] < -2 * R2["incr_plus_go_se"], R2["incr_plus_go_slope"])
A.v("20", np.median([us2[k] for k in STD]), label="a $20 plan")
A.v("0.65", R["aab_p20_HIC"])
A.v("29", R["aab_p20_LIC"])
p = S("\\noindent\\textbf{JEL codes:}")
p.pin("11", "15", "81", "86", "42", "33", why="JEL classification codes")

# ================================================================================================ Section 1
P = S("Some digital goods are priced to market:")
P.pin("0.14", "0.18", why="price-income elasticities of Simonovska (2015), quoted from the literature")
P.v("8", R2["applevel_nonai_localise"], note="general subscription apps with at least one subscription item whose dollar slope exceeds 0.10 (applevel_nonai_localise, Appendix Table E.8)")
P.v("21", R2["applevel_nonai_apps"], label="8 of 21 general subscription apps")
P.cond("21 = the general subscription apps of the audit", R2["applevel_nonai_apps"] == N_NONAI)
P.v("20", np.median([us2[k] for k in STD]))
P.v("100", min(us2[k] for k in HIGH500))
P.v("500", max(us2[k] for k in HIGH500))
P.w("two", N_WAVES, note="two audits")

P = S("The question matters for two reasons.")
P.wpin("two", "reasons: industrial organization and policy")
P.w("hundredfold", p95_p5, tol=10, note="spread of incomes (95th over 5th percentile of GNI per capita)")
P.v("0.65", R["aab_p20_HIC"])
P.v("29", R["aab_p20_LIC"])

P = S("The evidence comes from four sources collected for this paper.")
P.w("four", len(re.findall(r"The (?:first|second|third|fourth)\b", P.text)), note="sources: the paragraph describes the first, the second, the third and the fourth")
P.w("two", N_WAVES, note="two-wave audit")
P.dt("27 September", d1, note="first audit date")
P.dt("16 October 2026", d2, note="second audit date")
P.v("218", len({r["storefront"] for r in raw1}))
P.v("170", prices[prices.price_local.notna()].storefront.nunique(),
    note="storefronts with a local list for at least one of the three assistants in wave 1")
P.v("173", R2["wave2_storefronts_local"])
P.w("six", N_OTHER_AI)
P.v("21", N_NONAI)
P.w("four", N_AIFEAT)
P.v("34", R2["wave2_apps"])
P.v("7,412", R2["wave2_requests"])
P.v("30,817", R2["wave2_items"])
P.v("30", R2["default_apps"])
P.v("19.99", us2["chatgpt_plus"], note="a price point that small developers use: the U.S. price of ChatGPT Plus")
P.w("twelve", R2["xch_play_apps"], note="apps whose Google Play pages were retrieved (code/16_cross_channel.py)")
P.v("30", R2["xch_play_countries"], label="Google Play in 30 countries")
P.v("57", R2["xch_ms_countries"], note="countries covered by the Microsoft web-store locale pages")

P = S("Three findings follow.")
P.w("Three", len(re.findall(r"(?<![A-Za-z])(?:First|Second|Third), ", P.text)), note="paragraph enumerates First, Second and Third")
f = P.sub("First, within the same firm", "(Google AI Plus, SuperGrok Lite).")
f.v("20", np.median([us2[k] for k in STD]), label="$20 tiers")
f.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (lower end)")
f.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (upper end: ChatGPT Pro 500)")
f.le("0.022", R2["rel_frontierpairs_abs_slope_max"], note="largest |slope| of the nine frontier pairs (rel_frontierpairs_abs_slope_max, 0.0219)", label="absolute slopes at most 0.022")
f.v("0.15", min(R2[f"rel_{k}_slope"] for k in PAIRS_YTX), note="smallest slope of the seven YouTube and X Premium pairs of Table 3 (X Premium vs X Premium Plus, 0.1495)")
f.v("0.34", max(R2[f"rel_{k}_slope"] for k in PAIRS_YTX), note="largest (YouTube Premium Lite vs Google AI Pro, 0.3404)")
f.v("0.20", R2["stacked_noai_gamma"], label="no AI allowance: 0.20 log points faster")
f.v("0.0005", R2["stacked_noai_ri_p"], note="randomisation p of the no-allowance gap, 0.000529, printed to four decimals", label="randomisation p = 0.0005 (no allowance)")
f.v("0.12", R2["stacked_smallai_gamma"], label="small allowance: 0.12 faster")
f.cond("the localised capped tiers are ChatGPT Go and Character.AI Lite, and Google AI Plus and SuperGrok Lite are not localised relative to the tier above them (median relative price one in LMIC storefronts, slope at or below zero)",
       set(LOC_CAPPED) == {"go_plus", "cai_lite_plus"} and R2["rel_aiplus_aipro_lmic_med"] == 1 == R2["rel_sglite_supergrok_lmic_med"]
       and R2["rel_aiplus_aipro_slope"] <= 0 and R2["rel_sglite_supergrok_slope"] <= 0, len(LOC_CAPPED))
f = P.sub("Second, relative to the estimated platform schedule", "(identical to the cent in 37).")
f.v("20", np.median([us2[k] for k in STD]), label="$20 tiers (deviations)")
f.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (lower end, deviations)")
f.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (upper end, deviations)")
f.w("six", N_VENDORS, note="vendors of the $20 and $100-500 tiers: OpenAI, Anthropic, Google, Perplexity, xAI, Microsoft")
f.v("0.016", min(R2[k + "_dev_slope"] for k in FRONT13), note="smallest deviation slope of the 13 frontier tiers (ChatGPT Pro 500, negative)")
f.v("0.004", max(R2[k + "_dev_slope"] for k in FRONT13), note="largest deviation slope (ChatGPT Plus)")
_pv13 = pvd[pvd.plan.isin(FRONT13) & pvd.dev_log.notna() & (pvd.gni > 0)]
_medg = _pv13.groupby(["plan", "income_group"]).dev_log.median()
f.cond("'medians of zero in every income group below high income': the median deviation of each of the 13 frontier tiers is zero in the low-, lower-middle- and upper-middle-income storefronts (data/processed/wave2_plan_vs_default.csv)",
       all(_medg[(k, g)] == 0 for k in FRONT13 for g in GROUPS[1:]),
       note="high-income medians are zero for %d of the 13 plans (the exceptions, within 0.04, are stated in Section 5.3)" % sum(_medg[(k, "High income")] == 0 for k in FRONT13))
f.v("0.110", R2["chatgpt_go_dev_slope"])
f.v("0.006", R2["chatgpt_go_dev_se"], label="Go deviation s.e.")
f.v("38", -R2["chatgpt_go_med_lmic_pct"])
f.v("5", 100 * XCH_BAND, note="within 5%: |ln(Play / App Store)| <= 0.05 (code/16_cross_channel.py)")
f.v("22", R2["xch_play_chatgpt_within5_n"])
f.v("25", R2["xch_play_chatgpt_same_currency"], note="same-currency countries of the Google Play comparison")
f.v("5", 100 * XCH_BAND, label="within 5% (Microsoft)")
f.v("49", R2["xch_ms_web_vs_app_premium_n"], label="all 49 same-currency countries (Microsoft)")
f.v("37", R2["xch_ms_web_vs_app_premium_exact_n"], note="'identical to the cent in 37': |web - App Store| < 0.005 in the storefront's currency (code/16; xch_ms_web_vs_app_premium_exact_n = _personal_exact_n = 37)")
f.cond("37 of 49 for Personal as well", R2["xch_ms_web_vs_app_personal_exact_n"] == R2["xch_ms_web_vs_app_premium_exact_n"] == 37)
f.cond("'within 5% ... for both of its plans in all 49': every Microsoft web price is within 5% of the App Store price for Premium and Personal alike, 49 comparisons each, median log difference zero",
       R2["xch_ms_web_vs_app_premium_within5"] == 1 == R2["xch_ms_web_vs_app_personal_within5"]
       and R2["xch_ms_web_vs_app_personal_n"] == R2["xch_ms_web_vs_app_premium_n"] == R2["xch_ms_web_vs_app_premium_within5_n"] == R2["xch_ms_web_vs_app_personal_within5_n"]
       and R2["xch_ms_web_vs_app_premium_median"] == 0 == R2["xch_ms_web_vs_app_personal_median"])
f = P.sub("Third, within the same storefront ChatGPT Plus costs", "where incomes are low.")
f.v("2.5", PG["US"])
f.v("4.0", PG["LIC"])
f.v("25", 100 * (R2["incr_plus_go_med_lmic"] - 1), note="median ratio of the Plus-Go dollar gap to the schedule gap in lower-middle-income storefronts (1.250); low-income 1.251")
f.cond("the low-income median of the increment ratio also rounds to 25% wider", round(100 * (R2["incr_plus_go_med_lic"] - 1)) == 25, R2["incr_plus_go_med_lic"])
f.v("0.047", R2["incr_plus_go_slope"])
f.v("0.005", R2["incr_plus_go_se"])
f.v("0.010", R2["incrusd_plus_go_slope"], label="in dollars relative to the U.S. gap (negative)")
f.v("0.007", R2["incrusd_plus_go_se"])

P = S("Section~\\ref{sec:model} develops a model under which a profit-maximising vendor would price this way")
P.v("8", us1["chatgpt_go"], note="an $8 capped tier: the U.S. price of ChatGPT Go")
P.v("200", us2["chatgpt_pro200"], note="a $200 tier: ChatGPT Pro 200")
P.v("20", np.median([us2[k] for k in STD]), label="the $20 tiers")
P.w("five", N_PRED, note="number of predictions in the list of Section 3.3")
P.notation()

P = S("The paper contributes to four literatures.")
P.w("four", len(re.findall(r"(?:^|\. )(?:It |And it )", P.text.split("The paper contributes to four literatures. ", 1)[1].split(" The uneven access")[0])),
    note="the four contributions are the four sentences that begin 'It adds', 'It brings', 'It extends', 'And it supplies'")
W12 = pd.read_csv(ROOT / "output" / "tables" / "W12_increment.csv", keep_default_na=False, na_values=[""]).set_index("pair")   # the increment pairs (code/13)
N_PAIR_PLANS = len({W12.loc["plus_go", "high"], W12.loc["plus_go", "low"]})                   # the two plans of the Plus-Go increment
S("and the dollar gap between the two plans, relative to the gap").w("two", N_PAIR_PLANS, note="the two plans of the ratio and the increment: ChatGPT Plus and Go (W12_increment.csv, pair plus_go)")
S("documents the two audit waves").w("two", N_WAVES)

# ================================================================================================ Section 2
P = S("Table~\\ref{tab:ladder} summarises the consumer plans")
P.dt("27 September 2026", d1)
P.w("three", N_CORE, note="the three leading assistants (apps of class ai_core)")
P.w("Three", n_leads("Three features of the menu stand out.", "\\subsection{How App Store prices are set}"),
    note="features of the menu = the paragraphs that open with an emphasised lead: convergence, quantity above the standard tier, localisation at the bottom")

# Table 1: the U.S. App Store prices in brackets are the U.S. rows of the two audits; web prices, plan names and allowance
# multiples are vendor-page facts that no audit output can contain and are pinned to the text.
S("The consumer price ladder of three leading AI assistants, September 2026").dt("September 2026", d1)
T1 = S("Entry & Go: \\$8 [\\$8.00]", "\\bottomrule")
for printed, val, what in [("8.00", us1["chatgpt_go"], "Go"), ("4.99", us1["gemini_plus"], "AI Plus"),
                           ("19.99", us1["chatgpt_plus"], "Plus"), ("20.00", us1["claude_pro"], "Claude Pro"),
                           ("19.99", us1["gemini_pro"], "AI Pro"), ("100.00", us1["chatgpt_pro5x"], "Pro 5x (now Pro 100)"),
                           ("124.99", us1["claude_max5x"], "Max 5x"), ("200.00", us1["chatgpt_pro20x"], "Pro 20x (now Pro 200)"),
                           ("500.00", us2["chatgpt_pro500"], "Pro 500 (16 October audit)"), ("249.99", us1["claude_max20x"], "Max 20x"),
                           ("199.99", us1["gemini_ultra"], "AI Ultra")]:
    T1.v(printed, val, note=f"U.S. App Store price, {what}", label=f"[${printed}] {what}")
d_in = ro.loc[ro.iso3 == "IND", "date"].iloc[0]
d_us = ro.loc[ro.iso3 == "USA", "date"].iloc[0]
T1.dt("Aug.\\ 2025", d_in, note="ChatGPT Go launched in India (rollout record)")
T1.dt("Jan.\\ 2026", d_us, note="ChatGPT Go in the United States (rollout record)")
T1.dt("Oct.", d2, note="the Pro 500 price is from the audit of 16 October 2026")
T1.dtpin("10--29 Sep.\\ 2026", why="period in which new Pro 200 sign-ups were paused (vendor release notes)")
T1.dtpin("29 Sep.\\ 2026", why="date on which the Pro 500 tier was added (vendor release notes)")
# the numerals that remain are the vendor-page facts, in order of appearance: Go $8; Plus $20, Claude Pro $20 monthly and $17 annual;
# Pro $100 (5x), Max 5x "from $100", AI Ultra $100 (5x); Pro $200 (20x), Pro $500, Max 20x $200, AI Ultra $200 (was $250, 20x).
# A change of any of them is reported, not absorbed.
T1.pin_rest("8", "20", "20", "17", "100", "5", "100", "100", "5", "200", "20", "500", "200", "200", "250", "20",
            why="vendor-page fact: web price, plan name or allowance multiple (Table 1)")

ULTRA_N = {"Table 5 (income data and multiplier)": int(W1.loc["gemini_ultra", "n"]), "item slopes": R2["item_gemini_ultra_n"],
           "wave 2, storefronts other than the U.S.": int(rows2[(rows2.plan == "gemini_ultra") & (rows2.storefront != "us")].storefront.nunique()),
           "wave 1 compared with wave 2": R2["stab_gemini_ultra_compared"]}
P = S("Official U.S. web prices per month as documented on 27 September 2026")
P.dt("27 September 2026", d1)
P.dt("16 October 2026", d2, note="Pro 500 price from the 16 October 2026 audit")
P.v("199.99", us1["gemini_ultra"], note="U.S. App Store price of the single Ultra plan")
P.cond("the App Store lists one Ultra plan in the U.S.", (prices[prices.plan == "gemini_ultra"].storefront == "us").sum() == 1)
P.v("94", min(ULTRA_N.values()), note="smallest Ultra sample: " + "; ".join(f"{k} {v}" for k, v in ULTRA_N.items()))
P.v("98", max(ULTRA_N.values()), note="largest Ultra sample: storefronts other than the U.S. with an Ultra listing in wave 2 (data/processed/wave2_plan_rows.csv)")
P.cond("'its absence elsewhere is list truncation': every Gemini list without Ultra is full (has exactly ten entries)", R2["wave2_gemini_lists_without_ultra"] == R2["wave2_gemini_lists_without_ultra_full"] > 0, R2["wave2_gemini_lists_without_ultra"])
P.dtpin("19 May 2026", why="announcement of Google's new Ultra tiers (vendor announcement)")
# remaining: Google's Ultra tiers ($100 new tier; $200, down from $250)
P.pin_rest("100", "200", "250", why="vendor-page fact: web price (notes to Table 1)")

P = S("\\emph{Convergence.}")
P.w("three", N_CORE, note="the menus of ChatGPT, Claude and Gemini")
P.v("5", min(us1["gemini_plus"], us1["chatgpt_go"]), note="entry tier: Google AI Plus $4.99")
P.v("8", max(us1["gemini_plus"], us1["chatgpt_go"]), note="entry tier: ChatGPT Go $8.00")
P.v("20", np.median([us2[k] for k in STD]), note="standard tier")
P.v("100", us2["chatgpt_pro100"], note="'about $100'")
P.v("200", us2["chatgpt_pro200"], note="'about $200'")
P.v("20", min(us2["perplexity_pro"], us2["m365_premium"]), note="Perplexity Pro and Microsoft 365 Premium")
P.v("30", us2["supergrok"], note="SuperGrok")
P.v("300", us2["supergrok_heavy"], note="SuperGrok Heavy")

P = S("\\emph{Quantity, not intelligence, above the standard tier.}")
P.v("5", MULT_ALLOW[0], note="allowance multiple in the plan names (chatgpt_pro5x, claude_max5x)")
P.v("20", MULT_ALLOW[1], note="allowance multiple in the plan names (chatgpt_pro20x, claude_max20x)")
P.w("hundredfold", p95_p5, tol=10, note="range of incomes (95th over 5th percentile of GNI per capita)")

LOC_AI = [k for k in W1.index if W1.loc[k, "cls"] in ("ai_core", "ai") and W1.loc[k, "dev_slope"] > 0.05]        # AI plans whose deviation rises with income
PLAY_APPS_COLLECTED = set(pd.read_csv(ROOT / "data" / "raw" / "web" / "play_iap_ranges.csv", keep_default_na=False).app)   # apps whose Google Play pages were retrieved
P = S("\\emph{Localisation at the bottom of the ladder.}")
P.dt("August 2025", d_in, note="India, first_available in the rollout record")
P.v("8", us1["chatgpt_go"], note="U.S. launch price of ChatGPT Go")
P.dt("January 2026", d_us, note="U.S. launch, first_available in the rollout record")
P.w("two", len(LOC_AI), note="AI plans (apps of class ai_core or ai) whose deviation slope from the schedule exceeds 0.05: " + ", ".join(LOC_AI))
P.cond("the two localised AI tiers are ChatGPT Go and Character.AI Lite", set(LOC_AI) == {"chatgpt_go", "characterai_lite"})
P.dtpin("29 September 2026", why="date of the tariff change (vendor release notes)")
_t = re.search(r"tariff change of (\d+) ([A-Z][a-z]+) (\d{4})", P.text)
P.cond("the vendor pages that document the tariff change (extensions/pricing_sources/manifest.json) were all retrieved on the printed date",
       MAN_DATES == [iso_of(_t.group(1), _t.group(2), _t.group(3))], len(MAN_DATES),
       note="retrieval date of the archived vendor pages; the date of the vendor's announcement is pinned")
P.v("500", us2["chatgpt_pro500"], note="Pro 500 tier")

# ================================================================================================ Section 2: App Store pricing mechanics
n_codes = len({r["storefront"] for r in raw1})
redir1 = sorted({r["storefront"] for r in raw1 if r["http_status"] == 200 and "/us/" in r["final_url"] and r["storefront"] != "us"})
plus_s = prices[(prices.plan == "chatgpt_plus") & prices.price_usd.notna()].merge(
    panel.assign(storefront=panel.iso2.str.lower())[["storefront", "gni_atlas", "income_group"]], on="storefront").dropna(subset=["gni_atlas"])
cur_n = plus_s.currency.value_counts()
TAX_EMBED = grab(SRC12, r"tax_factor > ([0-9.]+)", "tax factor of a U.S.-dollar storefront whose schedule embeds a tax")     # 1.05
APPLE_FIRST_UPDATE = min(pd.Timestamp(f"{d} {m} {y}") for d, m, y in re.findall(r"(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})", SRC15.split("Inputs")[0]))   # earliest Apple Developer News update named in code/15_vintage_test.py

P = S("The prices this paper audits are listed by Apple's App Store")
P.w("four", len(re.findall(r"(?<![A-Za-z])(?:First|Second|Third|Fourth), ", P.text)), note="First, Second, Third and Fourth rule of the paragraph")
P.pin("175", why="number of App Store countries and regions quoted from Apple's documentation (apple2026pricing)")
P.v("19.99", us1["chatgpt_plus"])
P.v("199.99", us1["gemini_ultra"])
P.dt("February 2025", APPLE_FIRST_UPDATE, note="the earliest of Apple's periodic price updates that exclude auto-renewable subscriptions, as dated in the docstring of code/15_vintage_test.py (6 Feb 2025)")
P.v("45", len(redir1), note="codes whose request was redirected to the U.S. store")
P.v("218", n_codes)
P.w("two", next(iter({len(r["storefront"]) for r in raw1})), note="length of the storefront codes in the raw records (ISO 3166-1 alpha-2)")
P.v("102", int(cur_n["USD"]), note="USD-priced ChatGPT Plus storefronts in the first-wave regression sample")
P.v("164", len(plus_s), note="storefronts in the first-wave price regression (ChatGPT Plus)")
P.cond("every storefront in a low-income economy is denominated in U.S. dollars", R["store_usd_LIC"] == 1.0, R["store_usd_LIC"])
P.v("16", R2["taxabs_n_storefronts"], note="U.S.-dollar storefronts whose tax factor exceeds 1.05 (code/12_default_panel.py, keys taxabs_*)")
P.v("5", 100 * (TAX_EMBED - 1), note="a tax of more than 5%: tax_factor > 1.05")
P.cond("16 = the number of U.S.-dollar storefronts of the multiplier file with a tax factor above 1.05",
       int(((mult.currency == "USD") & (mult.tax_factor > TAX_EMBED)).sum()) == R2["taxabs_n_storefronts"], R2["taxabs_n_storefronts"])
P.pin("15", "30", why="Apple's commission rates on subscription revenue (15% for small developers and after the first year, 30% otherwise): platform policy")
P.cond("45 redirected codes = 135 redirected requests / 3 assistants",
       sum(1 for r in raw1 if r["http_status"] == 200 and "/us/" in r["final_url"] and r["storefront"] != "us") == 3 * len(redir1))
S("The consumer price ladder of three leading AI assistants, September 2026").w("three", N_CORE)

# ================================================================================================ Section 3: the model
go_usd = prices[prices.plan == "chatgpt_go"].set_index("storefront").price_usd           # first-wave dollar prices of ChatGPT Go
GO_GAP_LO = us1["chatgpt_go"] - R["price_chatgpt_go_LIC"]                                  # $8.00 less the median low-income price ($4.99): 3.01
GO_GAP_HI = us1["chatgpt_go"] - go_usd.drop("us").min()                                    # $8.00 less the lowest listed price (India, $4.16): 3.84
P = S("This section sets out a compact model")
P.w("five", N_PRED, note="number of predictions in the list of Section 3.3")

P = S("In market $c$ a share $\\kappa_c$ of the population is connected")
P.w("four", N_OPT, note="non-use, F, L, H: u_0 and u_k for k in {F, L, H} in Appendix A")
P.w("doubling", math.exp(math.log(2 * 7.0) - math.log(7.0)), note="mu_c = mu_0 + ln(y_c/y_0): doubling y adds ln 2 to ln v")
P.w("doubles", math.exp(math.log(2 * 7.0) - math.log(7.0)))
P.w("three", N_THR, note="thresholds in the nested condition: tau/q_F, p_L/(q_L-q_F), (p_H-p_L)/(q_H-q_L)")
P.notation()
S("and the shares of the connected population using any tier").w("three", N_THR, note="the three terms of the nested condition (eq. 3.1)")
S("Three features of the supply side distinguish").w("Three", n_leads("Three features of the supply side distinguish", "\\subsection{Predictions}"),
                                                     note="features = the paragraphs that open with an emphasised lead")
P = S("\\emph{Positive, income-invariant marginal cost.}")
P.v("20", np.median([us2[k] for k in STD]), note="a $20 plan")
P.notation()
S("\\emph{The platform default.} For each tier the vendor sets a U.S. base price").notation()
S("\\emph{Cross-border arbitrage.}").wpin("two", "the two storefronts of an arbitrage pair (structural)")
S("Let $\\Delta p_{k,c}$ denote the price increment of tier $k$").w("two", N_OPT - 2, note="the two paid increments: the entry price over the free tier and the frontier price over the entry price")
P = S("where $\\rho_k=1/(\\xi_k+\\ell_k)$ is the rate")
P.v("1", beta_ln(0.0, 1.0), note="beta(L = 0) from (A.8)", label="beta = 1 at zero marginal cost")
P.v("0", beta_ln(0.999, 1.0), note="beta(L -> 1) from (A.8), evaluated at L = 0.999", label="beta -> 0 as the cost share tends to one")
P.notation()
S("\\beta_k\\equiv\\frac{\\partial\\ln\\Delta p^*_{k,c}}{\\partial\\ln y_c}", "\\label{eq:beta_supply}").notation()

P = S("The frontier price is the sum of the two increments")
P.w("two", N_OPT - 2, note="the two increments of the menu")
P.v("20", np.median([us2[k] for k in STD]), label="not for the $20 tiers")
P.v("3", GO_GAP_LO, note="ChatGPT Go listed $3-4 cheaper than in the U.S.: $8.00 less the median low-income first-wave price ($4.99)")
P.v("4", GO_GAP_HI, note="$8.00 less the lowest listed first-wave price (India, $4.16)")
_g_lo, _g_hi = round(GO_GAP_LO), round(GO_GAP_HI)
P.v("15", 100 * _g_lo / np.median([us2[k] for k in STD]), note="a $3 gap on a $20 tier")
P.v("20", 100 * _g_hi / np.median([us2[k] for k in STD]), note="a $4 gap on a $20 tier", label="15--20% discount")
P.v("20", np.median([us2[k] for k in STD]), label="discount on a $20 tier")
P.v("0.6", 100 * _g_lo / max(us2[k] for k in HIGH500), note="a $3 gap on the $500 tier (0.6%)")
P.v("4", 100 * _g_hi / min(us2[k] for k in HIGH500), note="a $4 gap on a $100 tier")
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tier (lower end)")
P.v("500", max(us2[k] for k in HIGH500), label="$100-500 tier (upper end)")
P.v("20", np.median([us2[k] for k in STD]), label="the override cost and the $20 tiers")
P.notation()
S("\\item \\emph{Cheap access through less service, not a lower price.}").wpin("two", "the two instruments of the sentence: a usage cap and a weaker model (structural)")

# the burden: AAB = 12 p / y x 100 (eq. 3.2); the audit recomputes the burden from this definition
rec = {g: float((1200 * 20 / gni.loc[gni.income_group == g, "gni_atlas"]).median()) for g in GROUPS}
P = S("\\AAB_c(p_c) = \\frac{12\\,p_c}{y_c}\\times 100", "\\label{eq:aab}")
BENCH = 100 * grab((ROOT / "code" / "20_analysis.py").read_text(), r"threshold_gni_for_2pct_p20\"\] = 12 \* 20 / ([0-9.]+)", "benchmark")
MONTHS = grab((ROOT / "code" / "20_analysis.py").read_text(), r"threshold_gni_for_2pct_p20\"\] = ([0-9]+) \* 20 /", "months")
P.v("12", MONTHS, note="months per year in the burden (code/20_analysis.py)")
P.v("100", AAB_PCT, note="percent factor of aab() in code/20_analysis.py")
P.cond("median burdens recomputed from 12 p / y x 100 equal results.json for the four income groups",
       all(abs(rec[g] - R["aab_p20_" + SH[g]]) < 5e-7 for g in GROUPS), note="results.json stores six decimals")
P = S("the annual price of a plan as a percentage of GNI per capita")
P.v("2", BENCH, note="2% benchmark (code/20_analysis.py: threshold_gni_for_2pct_p20 = 12 * 20 / 0.02)")
P.cond("the benchmark of 2% reproduces the number of economies above it in results.json",
       int((gni.aab20 > BENCH).sum()) == R["n_countries_aab20_gt2"], R["n_countries_aab20_gt2"])

# ================================================================================================ Section 4: data
nf_all3 = sorted(sf for sf, apps_ in {sf: {r["app"] for r in raw1 if r["storefront"] == sf and r["http_status"] == 404} for sf in {r["storefront"] for r in raw1}}.items() if len(apps_) == N_CORE)
cname = panel.assign(sf=panel.iso2.str.lower()).set_index("sf").country_wb
W2_INCOME_SF = int(items[items.gni > 0].storefront.nunique())                              # second-wave storefronts with income data (U.S. included)
W1_BY_APP = [R["loc_chatgpt_plus_n"], R["loc_claude_pro_n"], R["loc_gemini_pro_n"]]        # first-wave storefronts with income data, by app (U.S. included)
W1_BY_PLAN = [v for k, v in R.items() if re.fullmatch(r"loc_\w+_n", k)]                   # the same by plan (Google AI Ultra is listed in 95)
mult_no_income = sorted(s for s in mult.storefront if not (panel.set_index(panel.iso2.str.lower()).gni_atlas.get(s, 0) > 0))


def _code(lst):
    """storefront codes of the economies named in a list of the text (names matched as prefixes of the World Bank names)"""
    out = set()
    for n in re.split(r", | and ", lst):
        hit = panel.loc[panel.country_wb.str.startswith(n.strip()), "iso2"].str.lower()
        if len(hit) == 1:
            out.add(hit.iloc[0])
    return out


P = S("Table~\\ref{tab:data} lists sources and coverage")
P.v("218", n_codes)
P.w("two", next(iter({len(r["storefront"]) for r in raw1})), note="two-letter codes")
P.v("217", len(panel), note="World Bank economies in the panel; the 218th code is Taiwan")
P.v("170", prices[prices.price_local.notna()].storefront.nunique(), note="first wave: storefronts with a local list for at least one of the three assistants")
P.w("three", N_CORE, note="assistants of the first wave")
P.v("173", R2["wave2_storefronts_local"])
P.v("162", min(W1_BY_APP), note="first-wave storefronts with income data, by app: Claude 162, ChatGPT 164, Gemini 165 (loc_<plan>_n of results.json)")
P.v("165", max(W1_BY_APP))
P.v("170", W2_INCOME_SF, note="second-wave storefronts with income data, U.S. included (data/processed/wave2_items_long.csv)")
P.v("161", R2["default_slope_n"], note="storefronts with income data and a multiplier")
f = P.sub("\\footnote{Storefront arithmetic:", "have income data.}")
f.v("218", n_codes)
f.v("45", len(redir1))
f.v("173", n_codes - len(redir1), note="218 - 45 active storefronts")
f.cond("the active storefronts are those of the second wave's local lists", n_codes - len(redir1) == R2["wave2_storefronts_local"])
f.cond("Belarus, China and Russia are the storefronts whose three first-wave requests all returned 'not found'",
       set(nf_all3) == _code("Belarus, China and Russia"), len(nf_all3))
f.w("three", N_CORE, note="all three assistants")
f.v("170", n_codes - len(redir1) - len(nf_all3), note="173 active storefronts less the three 'not found' ones = the 170 of the first wave")
f.cond("170 = the first-wave storefronts with a local list", n_codes - len(redir1) - len(nf_all3) == prices[prices.price_local.notna()].storefront.nunique())
f.v("167", R2["default_storefronts"])
_ex6 = re.search(r"all active storefronts except (.*?)\)", f.text).group(1)
_last2 = {}
for _r in raw2:                                                                            # last definitive record per storefront (code/09b)
    if _r["app"] == "chatgpt" and _r.get("http_status") in (200, 404, 410):
        _last2[_r["storefront"]] = _r["http_status"]
_no_chatgpt2 = {sf for sf, st in _last2.items() if st != 200}
f.cond("the six storefronts without a ChatGPT page in wave 2 are those named (Belarus, China, Hong Kong SAR, Macao SAR, Russia, Venezuela): 173 active less 6 = 167",
       len(_code(_ex6)) == 6 == n_codes - len(redir1) - R2["default_storefronts"] and _code(_ex6) == _no_chatgpt2, len(_no_chatgpt2))
f.v("164", R2["default_multiplier_storefronts"])
f.cond("the storefronts without a multiplier are Nigeria and Turkiye (the U.S. storefront is the base of the schedule and has none by construction)",
       set(json.load(open(ROOT / "data" / "raw" / "appstore_wave2" / "local_storefronts.json"))) - set(mult.storefront) == {"ng", "tr", "us"}
       and R2["default_storefronts"] - R2["default_multiplier_storefronts"] == 3)
f.v("161", R2["default_slope_n"])
f.cond("the multiplier storefronts without income data are Taiwan, the British Virgin Islands and Yemen", mult_no_income == ["tw", "vg", "ye"]
       and R2["default_multiplier_storefronts"] - len(mult_no_income) == R2["default_slope_n"], len(mult_no_income))
f.v("108", R2["chatgpt_plus_clean_n"], note="clean storefronts with income data")
f.v("111", R2["default_clean_storefronts"])
P.v("201", R["n_econ_gni"])
P.v("217", len(panel))

# -- Table 2 (hand-written)
ATLAS_README = (ROOT / "data" / "raw" / "google_atlas" / "README.md").read_text()
n_ms_matched = len(panel.dropna(subset=["ms_q2_2026"]))
n_ms_total = n_ms_matched + 2          # + French Guiana and Taiwan, which are not World Bank economies (Appendix B)
n_ms_pooled = int(panel.dropna(subset=["ms_q2_2026"]).ms_region_imputed.sum()) + 1      # + French Guiana
aui_n = [R[f"aui_{w}_n"] for w in ("aug25", "nov25", "feb26", "apr26", "may26")]
aei_all = pd.read_csv(ROOT / "data" / "raw" / "anthropic" / "anthropic_country_panel.csv", keep_default_na=False, na_values=[""])
aei_win = aei_all.groupby(["release", "date_start"]).date_end.first().reset_index()
roll = json.load(open(AO / "audit_results_rollout.json"))
aui_w = [w for w in roll["windows"] if w["source"] == "aui"]
recomputed_n = [int(panel[c].notna().sum()) for c in ("aui_aug25", "aui_nov25", "aui_feb26")]
FX_DATES = sorted(pd.Timestamp(re.search(r"usd_(\d{4}-\d\d-\d\d)\.json", f.name).group(1)) for f in (ROOT / "data" / "raw" / "fx_hist").glob("usd_*.json"))   # the six snapshots of the vintage test
T2 = S("Income, groups & World Development Indicators", "\\bottomrule")
T2.v("2027", FY_CLASS, note="fiscal year of the income classification named in code/10_build_dataset.py")
T2.v("201", R["n_econ_gni"])
T2.v("2025", int(gni.gni_atlas_year.mode().iloc[0]), note="vintage of GNI per capita for the 182 economies")
T2.v("182", R["n_econ_gni2025"])
T2.v("2010", int(panel.dist_year.min()), note="earliest survey year of the quintile shares")
T2.v("2025", int(panel.dist_year.max()), note="latest survey year of the quintile shares")
T2.v("163", R["n_dist"])
T2.dt("27 Sep 2026", d1, note="first audit")
T2.v("218", n_codes)
T2.v("170", prices[prices.price_local.notna()].storefront.nunique())
T2.v("162", min(W1_BY_APP), note="first-wave storefronts with income data by app (Claude)")
T2.v("165", max(W1_BY_APP), note="by app (Google AI Pro)")
T2.v("95", min(W1_BY_PLAN), note="by plan: Google AI Ultra (loc_gemini_ultra_n)")
T2.v("165", max(W1_BY_PLAN), note="by plan: Google AI Pro")
T2.v("34", R2["wave2_apps"])
T2.w("three", N_CORE)
T2.w("six", N_OTHER_AI)
T2.v("21", N_NONAI)
T2.w("four", N_AIFEAT)
T2.dt("16 Oct 2026", d2, note="second audit, core and benchmark apps")
T2.v("218", n_codes)
T2.v("173", R2["wave2_storefronts_local"])
T2.v("7,412", R2["wave2_requests"])
T2.v("30,817", R2["wave2_items"])
T2.v("30", R2["default_apps"])
T2.dt("16 Oct 2026", d2, note="second audit, default panel")
T2.v("167", R2["default_storefronts"])
T2.v("164", R2["default_multiplier_storefronts"])
T2.v("161", R2["default_slope_n"])
T2.v("12", R2["xch_play_apps"], note="apps retrieved from Google Play")
T2.v("30", R2["xch_play_countries"])
T2.v("57", R2["xch_ms_countries"])
T2.dt("16 Oct 2026", d2, note="cross-channel extracts, same day as the second wave (code/16_cross_channel.py)")
T2.v("360", R2["xch_play_apps"] * R2["xch_play_countries"], note="12 apps x 30 countries = Google Play app-country pages")
T2.v("63", R2["xch_ms_locales"], note="Microsoft web-store locale pages with prices")
T2.pin("0", why="part of the name of the exchange-rate source (fawazahmed0 currency-api)")
T2.w("six", R2["vint_fx_dates"], note="snapshots of the exchange-rate history (code/15_vintage_test.py)")
T2.dt("March 2024", FX_DATES[0], note="first snapshot (data/raw/fx_hist/usd_2024-03-06.json)")
T2.dt("October 2026", FX_DATES[-1], note="last snapshot (usd_2026-10-15.json)")
T2.cond("the exchange-rate history has as many snapshots as the vintage test counts", len(FX_DATES) == R2["vint_fx_dates"], len(FX_DATES))
_vint_all = pvd[(pvd.storefront != "us") & pvd.dev_log.notna() & pvd.gni.notna()]                      # the rows of the vintage test (code/15), any plan
_vint_go = _vint_all[_vint_all.plan == "chatgpt_go"]
T2.v("37", R2["vint_go_n_currencies"], note="currencies of the storefronts in the vintage test's price sample (161 storefronts with income data and a multiplier: vint_go_n_currencies = "
                                           "vint_frontier_n_currencies = 37); the key vint_currencies, 39, also counts NGN and TRY, whose storefronts (no multiplier) enter the file only through the "
                                           "Gemini 100 GB item's exact reference (see the report)")
T2.cond("vint_currencies (39) = the 37 currencies of the regression sample plus NGN and TRY, which appear only in rows of other items (Nigeria and Turkiye have no multiplier)",
        R2["vint_go_n_currencies"] == R2["vint_frontier_n_currencies"] == _vint_go.currency.nunique() == 37 and R2["vint_currencies"] == _vint_all.currency.nunique()
        and set(_vint_all.currency) - set(_vint_go.currency) == {"NGN", "TRY"} and not set(mult.storefront) & {"ng", "tr"}, R2["vint_currencies"])
MS_COLS = [c for c in panel.columns if re.fullmatch(r"ms_[hq][12]_\d{4}", c)]
T2.v("2025", int(MS_COLS[0][-4:]), label="H1 2025", note="first period of the Microsoft series (panel column " + MS_COLS[0] + ")")
T2.v("2026", int(MS_COLS[-1][-4:]), label="Q2 2026", note="last period of the Microsoft series (panel column " + MS_COLS[-1] + ")")
T2.v("147", n_ms_total)
T2.v("111", n_ms_total - n_ms_pooled, note="147 economies less the 36 pooled ones")
T2.dt("Aug 2025", pd.Timestamp(aei_win.date_start.min()), note="first Anthropic window (4 August 2025)")
T2.dt("May 2026", pd.Timestamp(aei_win.date_start.max()), note="last Anthropic window (May 2026)")
T2.v("113", min(aui_n), note="smallest number of economies above the publication floor across the five windows")
T2.v("120", max(aui_n))
T2.v("165", min(recomputed_n), note="recomputed index, smallest window (geolocated economies)")
T2.v("169", max(recomputed_n), note="recomputed index, February 2026 window (largest)")
T2.v("1.0", float(re.search(r"ATLAS v(\d\.\d)", ATLAS_README).group(1)), note="version of Google ATLAS (README)")
_am = re.search(r"in ([A-Z][a-z]+) (\d{4})", ATLAS_README)
T2.dt("Apr 2026", pd.Timestamp(year=int(_am.group(2)), month=MONTH_FULL.index(_am.group(1)), day=1), note="data month of Google ATLAS (README: April 2026)")
T2.v("195", R["g_n"])
T2.v("27", int(((ro.iso3 != "") & ro.cohort.isin(["C1", "C2", "C4"])).sum()), note="economies dated individually: India, Indonesia (C1), 16 Asian (C2), Brazil and 8 European (C4); the U.S. launch of January 2026 (C6) is separate")
T2.v("71", int(re.search(r"(\d+) further countries", ro.loc[ro.cohort == "C3", "country"].iloc[0]).group(1)),
     note="rollout record, C3 batch of 14 October 2025")
T2.dt("14 Oct 2025", ro.loc[ro.cohort == "C3", "date"].iloc[0], note="rollout record, C3 batch")
T2.v("2025", FINDEX_EDITION, note="edition of the Global Findex named in code/10_build_dataset.py")
T2.v("142", int(panel.fx_online_merchant_pay.notna().sum()), note="smallest availability among the complements in the paper's regressions (Findex digital merchant payments)")
T2.v("217", int(panel.urban_pct.notna().sum()), note="largest availability (urbanisation)")

P = S("Income groups follow the World Bank classification for fiscal year 2027")
P.v("2027", FY_CLASS, note="fiscal year of the income classification named in code/10_build_dataset.py")
P.dtpin("1 July 2026", why="effective date of the classification: World Bank announcement")
P.v("2025", int(gni.gni_atlas_year.mode().iloc[0]), note="vintage of the GNI per capita on which the classification rests")
LICx, LMx, UMx, HIx = (gni[gni.income_group == g].gni_atlas for g in GROUPS[::-1])
nonmis = gni[~gni.iso3.isin(["ARG", "TUR"])]
P.pin("1,175", "1,176", "4,635", "4,636", why="World Bank FY2027 thresholds")
P.cond("thresholds are consistent with the shipped income groups: max(low) <= 1,175 < min(lower-middle), max(lower-middle) <= 4,635 < min(upper-middle)",
       LICx.max() <= 1175 < LMx.min() and LMx.max() <= 4635 < UMx.min(), LICx.max())
P.v("14,375", R["hic_threshold_fy27"], note="upper-middle / high boundary (code/20_analysis.py)")
P.v("14,375", R["hic_threshold_fy27"])
P.cond("apart from Argentina and Turkiye, upper-middle economies lie at or below 14,375 and high-income economies above it",
       nonmis[nonmis.income_group == "Upper-middle income"].gni_atlas.max() <= 14375 < nonmis[nonmis.income_group == "High income"].gni_atlas.min())

# -- Income
nga = panel.loc[panel.iso3 == "NGA"].iloc[0]
wdi = pd.read_csv(ROOT / "data" / "raw" / "wb" / "wb_indicators_long.csv")
non25 = gni[gni.gni_atlas_year != 2025].gni_atlas_year
P = S("The main denominator is GNI per capita (Atlas method)")
P.v("2025", int(gni.gni_atlas_year.mode().iloc[0]))
P.v("182", R["n_econ_gni2025"])
P.v("19", R["n_econ_gni"] - R["n_econ_gni2025"])
P.v("2022", int(non25.min()), note="oldest vintage used for the remaining economies")
P.v("2024", int(non25.max()), note="newest vintage used for the remaining economies")
P.pin("2022", why="year of the Nigerian value quoted (column gni_atlas_2022)")
P.pin("2,140", why="earlier WDI vintage of Nigeria's 2022 GNI per capita; the shipped data contain only the current vintage")
P.v("2,940", nga["gni_atlas_2022"])
P.v("2025", int(nga["gni_atlas_year"]), label="Nigeria 2025 value")
P.v("1,360", nga["gni_atlas"])
P.v("2027", FY_CLASS, note="fiscal-year label of the income groups")
arg, tur = (panel.loc[panel.iso3 == c].iloc[0] for c in ("ARG", "TUR"))
P.v("14,650", arg["gni_atlas"])
P.v("16,300", tur["gni_atlas"])
P.v("2025", int(arg["gni_atlas_year"]), label="Argentina and Turkiye 2025 values")
P.dt("July 2026", pd.Timestamp(wdi.lastupdated.max()), note="WDI update of July 2026 (lastupdated 2026-07-13)")
P.cond("both exceed the high-income threshold but are classified as upper-middle income",
       arg["gni_atlas"] > R["hic_threshold_fy27"] and tur["gni_atlas"] > R["hic_threshold_fy27"]
       and arg["income_group"] == tur["income_group"] == "Upper-middle income")

# -- Local prices, wave 1
fxdev = float(((prices.fx_check_ratio - 1).abs().max()) * 100)
P = S("For each of the 218 storefront codes and each of the three assistants")
P.v("218", n_codes)
P.w("three", N_CORE)
P.dt("27 September 2026", d1)
P.w("five", ANNUAL_CUT, note="annual-variant cutoff 5 x the lowest price (code/09_appstore_prices.py and 09b)")
P.v("1.6", fxdev, note="largest deviation of the market rates of open.er-api.com from the independent source (fx_check_ratio)")
P.v("45", len(redir1))
P.v("124.99", us1["claude_max5x"])
P.pin("100", why="web price 'from $100' of Claude Max 5x (vendor page)")
nf = {a: {r["storefront"] for r in raw1 if r["app"] == a and r["http_status"] != 200} for a in ("chatgpt", "claude", "gemini")}
_nfm = re.search(r"\(ChatGPT: (.*?); Claude: the same plus (.*?); Gemini: (.*?)\)", P.text)
P.cond("the economies listed in the text as returning 'not found' pages are those of the raw records (ChatGPT; Claude the same plus others; Gemini)",
       nf["chatgpt"] == _code(_nfm.group(1)) and nf["claude"] == nf["chatgpt"] | _code(_nfm.group(2)) and nf["gemini"] == _code(_nfm.group(3))
       and all(len(_code(_nfm.group(i))) == len(re.split(r", | and ", _nfm.group(i))) for i in (1, 2, 3)), sum(len(v) for v in nf.values()))

# -- Local prices, wave 2, and the benchmark apps
W6 = pd.read_csv(ROOT / "output" / "tables" / "W6_annual_guard.csv", keep_default_na=False, na_values=[""]).set_index("item_key")
W7 = pd.read_csv(ROOT / "output" / "tables" / "W7_dedup.csv", keep_default_na=False, na_values=[""])
GUARD_MIN_ROWS = int(grab((ROOT / "code" / "42_tables_relative.py").read_text(), r"n_flagged >= ([0-9]+)", "flagged cells needed for a row of the guard table"))   # 5
guard_top = W6[W6.n_flagged >= GUARD_MIN_ROWS]
P = S("On 16 October 2026 the same procedure was applied to 34 apps")
P.dt("16 October 2026", d2)
P.v("34", R2["wave2_apps"])
lists = re.search(r"34 apps: ([^;]*); ([^;]*); 21 general subscription apps \(([^)]*)\); and four apps that sell AI features inside a general product \(([^)]*)\)", P.text)
P.cond("the first list names three assistants of class ai_core", len(re.split(r", | and ", lists.group(1))) == N_CORE, N_CORE)
P.cond("the second list names the six other AI assistants", len(re.split(r", | and ", lists.group(2))) == N_OTHER_AI, N_OTHER_AI)
P.v("21", N_NONAI)
P.cond("the parenthesis lists 21 general subscription apps", len(lists.group(3).split(", ")) == N_NONAI, N_NONAI)
P.w("four", N_AIFEAT)
P.cond("the parenthesis lists four apps that sell AI features", len(lists.group(4).split(", ")) == N_AIFEAT, N_AIFEAT)
P.v("7,412", R2["wave2_requests"])
P.v("7,218", R2["wave2_pages_200"])
P.v("5,688", R2["wave2_local_pages"])
P.v("1,530", R2["wave2_no_local_pages"])
P.v("194", R2["wave2_app_not_offered"])
P.cond("pages = local + redirected, requests = pages + not found",
       R2["wave2_pages_200"] == R2["wave2_local_pages"] + R2["wave2_no_local_pages"]
       and R2["wave2_requests"] == R2["wave2_pages_200"] + R2["wave2_app_not_offered"] + R2["wave2_errors"])
P.v("173", R2["wave2_storefronts_local"])
P.v("122", R2["wave2_pages_no_iap_list"], note="local pages without a purchase list")
P.v("30,817", R2["wave2_items"])
P.w("ten", R2["wave2_list_max_items"], note="Apple's product page lists at most ten purchases (wave2_list_max_items)")
P.v("4,632", R2["wave2_lists_with_10"])
P.v("5,566", R2["wave2_lists_nonempty"])
P.w("ten", R2["wave2_list_max_items"], note="lists with exactly ten entries")
P.w("Two", len([k for k in ("guard_flagged_cells", "wave2_dedup_dropped_n") if k in R2]), note="the two rules of the paragraph, each with its own output: the annual-as-monthly guard (guard_* keys) and the de-duplication (wave2_dedup_dropped_n)")
P.w("three", GUARD_K, note="the guard flags a price above three times the reference (code/09b_wave2_items.py, GUARD_K)")
P.v("151", R2["guard_flagged_cells"])
P.v("21,938", R2["guard_cells_considered"])
P.w("five", len(guard_top), note="'concentrated in five items': items with at least five flagged cells (W6_annual_guard.csv; the rows of Appendix Table E.11), which Appendix B names")
P.cond("the five items with the most flagged cells are Super Duolingo, Headspace Plus, Gemini 100 GB, Character.AI+ and Evernote Plus (named in Appendix B; item key gemini_100gb)",
       set(guard_top.index) == {"duolingo_super", "headspace_plus", "gemini_100gb", "characterai_plus", "evernote_plus"}, len(guard_top))
P.v("0.092", R2["guard_characterai_plus_slope_before"])
P.v("0.034", R2["guard_characterai_plus_slope_after"])
P.wpin("two", "items listed under two apps or two spellings (structural)")
P.wpin("two", "two spellings (structural)")
P.w("five", R2["wave2_dedup_dropped_n"], note="items dropped by the de-duplication (W7_dedup.csv)")
P.cond("W7 lists as many dropped items as results_wave2.json counts", len(W7) == R2["wave2_dedup_dropped_n"] == R2["wave2_item_slopes_n"] - R2["wave2_item_slopes_n_after"], len(W7))
P.v("152", R2["wave2_item_slopes_n"], note="items listed with a U.S. price in at least 60 storefronts before the de-duplication")
P.v("60", MIN_STORES_ITEM, note="storefronts per item (code/09b_wave2_items.py)")
P.w("two", N_WAVES, note="between the two waves")
P.cond("the page format changed between the waves: wave 2 is parsed with the HTML-list parser only (JSON parser: 0 pages)",
       R2["wave2_parser_html_v2"] > 0 and R2["wave2_parser_json_v1"] == 0, R2["wave2_parser_html_v2"])
P.v("20", MULT_ALLOW[1], note="former plan name ChatGPT Pro 20x")
P.v("1,586", R2["stab_all_compared"])
P.w("ten", len(STAB_PLANS), note="AI plans observed in both waves")
P.cond("all compared prices identical", R2["stab_all_identical"] == R2["stab_all_compared"])
P.v("19", R2["days_between_waves"])

P = S("\\paragraph{Computational workflow.}")
P.w("two", len([k for k in ("guard_flagged_cells", "wave2_dedup_dropped_n") if k in R2]),
    note="'an audit of the extraction found two errors': the two errors are those the two rules of the wave-2 paragraph address, each with its own output "
         "(the list-truncation guard, guard_* keys; the de-duplication, wave2_dedup_dropped_n)")

# -- The platform schedule
ditems = pcsv("wave2_default_items_long.csv")
US_PTS = ditems[ditems.storefront == "us"].groupby("us_price").size()                     # U.S. price points of the panel and the items at each
PT_DENSE_MAX = float(US_PTS[US_PTS >= 3].index.max())                                      # highest point with at least three items ($69.99)
PT_TAIL = US_PTS[US_PTS.index > PT_DENSE_MAX]                                              # 'a few' items above it: at most two per point
TAB5_PLANS = [k for k in W1.index if any(l.startswith(W1.loc[k, "label"].replace("$\\times$", "$\\times$") + " &") for l in (TAB / "tab_wave2_plans.tex").read_text().splitlines())]   # the 17 AI and Microsoft plans of Table 5
EXACT_PTS = sorted({float(W1.loc[k, "us_price"]) for k in TAB5_PLANS if W1.loc[k, "n_exact"] > 0})   # price points of the AI plans with exact schedule prices
P = S("Apple's own equalisation table is available only through a developer account")
P.v("30", R2["default_apps"])
P.v("85", len(json.load(open(ROOT / "data" / "raw" / "appstore_wave2" / "indie_candidates.json"))), note="candidate apps returned by the App Store searches (data/raw/appstore_wave2/indie_candidates.json)")
P.v("167", R2["default_storefronts"])
P.v("5,007", R2["default_pages"])
P.v("5,010", R2["default_requests"])
P.w("two", R2["default_panel_apps_without_priced_subscription"], note="panel apps without a priced subscription item")
P.v("30", R2["default_apps"], label="two of the 30 apps")
P.w("half", MODE_SHARE, note="share of the panel's items that the modal price must account for (wave2_common.py: 2 * top >= n)")
P.v("2.99", POINT_MIN_USD, note="lowest U.S. price point of the multiplier (wave2_common.py)")
P.v("1,551", R2["default_ladder_points"])
P.v("164", R2["default_multiplier_storefronts"])
P.v("0.99", float(US_PTS.index.min()), note="lowest U.S. price point of the panel (data/processed/wave2_default_items_long.csv)")
P.v("69.99", PT_DENSE_MAX, note="highest U.S. price point with at least three panel items; the points above it hold at most two items each ('a few')")
P.cond("the points above $69.99 hold at most two items each and seven in all", PT_TAIL.max() <= 2, int(PT_TAIL.sum()))
P.v("74.99", float(PT_TAIL.index.min()), note="lowest of the sparse points")
P.v("169.99", float(PT_TAIL.index.max()), note="highest U.S. price point of the panel")
P.v("4.99", EXACT_PTS[0], note="AI plan price points with an exact schedule price (n_exact > 0 in W1): " + ", ".join(f"{x:.2f}" for x in EXACT_PTS))
P.v("9.99", EXACT_PTS[1])
P.v("19.99", EXACT_PTS[2])
P.cond("the AI plans with an exact schedule price are priced at $4.99, $9.99 or $19.99 only", EXACT_PTS == [4.99, 9.99, 19.99], len(EXACT_PTS))
P.v("19.99", us2["chatgpt_plus"], label="the $19.99 plans")
P.w("three quarters", float(np.mean([W1.loc[k, "n_exact"] / W1.loc[k, "n"] for k in ("chatgpt_plus", "gemini_pro", "m365_premium")])), tol=0.03,
    note="share of storefronts with an exact reference for the $19.99 plans: ChatGPT Plus 123/161, Google AI Pro 121/159, Microsoft 365 Premium 122/157 (about 0.76)")
P.v("8.00", us2["chatgpt_go"])
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers")
P.v("500", max(us2[k] for k in HIGH500))
P.cond("ChatGPT Go and the $100-500 tiers have no exact reference anywhere (n_exact = 0)", all(R2[k + "_n_exact"] == 0 for k in ["chatgpt_go"] + HIGH500))

# -- Cross-channel prices
P = S("\\paragraph{Cross-channel prices.}")
P.v("30", R2["xch_play_countries"])
P.v("63", R2["xch_ms_locales"])
P.v("57", R2["xch_ms_countries"])
P.v("8.00", us2["chatgpt_go"], note="the lowest ChatGPT item on Google Play in the U.S. is the Go price (code/16_cross_channel.py)")
P.v("20.00", us2["claude_pro"], note="the lowest Claude item is the Pro price")
_w15b = csv("W15b_play_countries.csv", ROOT / "output" / "tables")
_usmin = _w15b[_w15b.country == "us"].set_index("app")
P.cond("the U.S. minima of the Google Play ranges are the App Store prices of ChatGPT Go ($8.00) and Claude Pro ($20.00) (W15b_play_countries.csv)",
       _usmin.loc["ChatGPT", "play_min"] == _usmin.loc["ChatGPT", "app_store_price"] == us2["chatgpt_go"]
       and _usmin.loc["Claude", "play_min"] == _usmin.loc["Claude", "app_store_price"] == us2["claude_pro"], _usmin.loc["Claude", "play_min"])
P.cond("Gemini shows no price range in any of the 30 countries", R2["xch_play_gemini_with_range"] == 0 and R2["xch_play_gemini_n"] == R2["xch_play_countries"], R2["xch_play_gemini_n"])

# -- Diffusion
DD = (ROOT / "data" / "raw" / "anthropic" / "docs" / ".." / "DATA_DICTIONARY.md").resolve().read_text()
ONE_M = 1e6 * int(re.search(r"\((\d+)M conv\.\)", DD).group(1))
MIN_CONV = int(re.search(r"MIN_OBSERVATIONS_COUNTRY = (\d+)", DD).group(1))
june = aei_all[aei_all.release == "release_2026_06_26"]


def REL_DATE(rel):
    """publication date of an Anthropic release from its identifier ('release_2026_06_26')"""
    return pd.Timestamp("-".join(rel.split("_")[1:]))


T_AUG, T_NOV, T_FEB = (pd.Timestamp(aei_all.loc[aei_all.release == r_, "date_start"].iloc[0])
                       for r_ in ("release_2025_09_15", "release_2026_01_15", "release_2026_03_24"))
T_APR, T_MAY = sorted(pd.Timestamp(x_) for x_ in june.date_start.unique())
P = S("The Microsoft AI User Share is the estimated share of people aged 15")
P.pin("15", "64", why="age band of the Microsoft metric (technical paper of Misra et al.)")
P.pin("19", why="number of AI services in the Microsoft telemetry (technical paper)")
ms_lic = panel.dropna(subset=["ms_q2_2026"]).query("income_group == 'Low income'")
P.v("36", n_ms_pooled)
P.v("147", n_ms_total)
P.v("20", int(ms_lic.ms_region_imputed.sum()), note="low-income economies with a pooled (regional) series")
P.v("23", len(ms_lic), note="low-income economies in the Microsoft data")
P.v("200", MIN_CONV, note="MIN_OBSERVATIONS_COUNTRY of the Anthropic data dictionary")
P.v("2025", int(aei_all.loc[aei_all.release == "release_2025_09_15", "date_start"].iloc[0][:4]), label="2025 windows (recomputed index)")
P.dt("February 2026", T_FEB, note="recomputed index, release of 24 March 2026 (window 5-12 February 2026)")
P.v("165", min(recomputed_n))
P.v("169", max(recomputed_n))
P.v("113", min(aui_n))
P.v("120", max(aui_n))
P.dt("April 2026", pd.Timestamp(year=int(_am.group(2)), month=MONTH_FULL.index(_am.group(1)), day=1), note="data month of Google ATLAS (README)")

# -- Estimands and inference
P = S("Four estimands recur.")
P.w("three", len(re.split(r", | and ", re.search(r"under the same (.*?), so all three cancel", P.text).group(1))), note="currency, tax rule and platform conversion: the three factors that cancel in the within-firm relative price")
P.w("Four", len(re.findall(r"\\emph\{[^}]*\}", P.text)), note="the four emphasised estimands: within-firm relative price, U.S.-dollar price regression, deviation regression, within-storefront ratio")
P.v("0.033", R2["default_slope"])
P.v("3", 100 * THR_WITHIN, label="within +/-3%")
P.v("10", 100 * THR_BELOW, label="more than 10% below")
P.w("two", len(set(re.findall(r"p_\{([HL]),c\}", P.text))), note="the two listings of the ratio and the increment: p_{H,c} and p_{L,c} of the same storefront")
HC3_MAXDIFF = float(max(abs(W1.loc[k, "dev_se_hc3"] - W1.loc[k, "dev_se"]) for k in TAB5_PLANS))        # largest |HC3 - HC1| deviation s.e. over the 17 plans of Table 5
P.lt("0.0002", HC3_MAXDIFF, note="HC3 errors differ from the HC1 errors of the second-wave plans by less than 0.0002: largest |dev_se_hc3 - dev_se| over the 17 plans of Table 5 (W1_wave2_plans.csv; Google AI Plus, 0.00012)",
     label="|HC3 - HC1| < 0.0002")
_w2cur = items[(items.gni > 0) & (items.storefront != "us")].groupby("storefront").currency.first()
P.v("102", int(cur_n["USD"]), note="U.S.-dollar storefronts in the first-wave regression sample (164 storefronts)")
P.v("104", int((_w2cur == "USD").sum()), note="U.S.-dollar storefronts among the %d second-wave storefronts with income data other than the U.S. (the stacked regression's 104 of 169)" % len(_w2cur))
P.cond("104 is also the number of dollar storefronts of the stacked regression", int((_w2cur == "USD").sum()) == R2["stacked_n_storefronts_usd"], R2["stacked_n_storefronts_usd"])
P.about("40", float(W8.n_currencies.median()), 2.0,
        note="'about 40 clusters': median number of currency clusters over the 21 within-firm pairs of Table 3 (39; 35-41 for all pairs but Google AI Ultra vs AI Pro, 18; rel_<pair>_n_currencies)")
P.v("1200", MONTHS * 100, note="12 months x 100 (equation 3.2)")
lnaab = np.log(1200 * 20 / gni.gni_atlas)
P.cond("the burden slope of a constant price on ln y is exactly -1 (and beta - 1 for a priced plan)",
       abs(np.polyfit(np.log(gni.gni_atlas), lnaab, 1)[0] + 1) < 1e-9)
P.notation()

# ================================================================================================ Section 5.1: relative prices within firm and storefront
rel_long = pcsv("wave2_relative_long.csv")                                                # pair x storefront relative prices (code/13)
PAIR_KEYS = [m.group(1) for k in R2 for m in [re.fullmatch(r"rel_(.+)_n_currencies", k)] if m]
N_FRONT_NUM = len(re.search(r'FRONTIER, FRONTIER_US = \[([^\]]*)\]', SRC13).group(1).split(","))   # the three $19.99 frontier plans of the cross-vendor numeraire
XV_FRONT = [k for k in FRONT13 if k != "chatgpt_plus"]                                       # the $20-500 tiers of the six vendors in Table E.10 other than ChatGPT Plus (its own numeraire)
XV_SLOPES = [R2[f"relplus_{k}_slope"] for k in XV_FRONT] + [R2[f"relfront_{k}_slope"] for k in FRONT13]
N_T5 = len(TAB5_PLANS)
N_D1 = len([l for l in (TAB / "tab_local.tex").read_text().splitlines() if l.strip().endswith("\\\\")])
_stack_src = SRC13.split("STACK = [")[1].split("\n]")[0]
STACK = [(p, f, g) for p, f, g in re.findall(r'\("([a-z0-9_]+)", "([^"]+)", "([a-z]+)"\)', _stack_src)]              # the items of the stacked regression (code/13)
STACK_PLANS, STACK_GROUP = [p for p, _, _ in STACK], {p: g for p, _, g in STACK}
N_STACK_FIRMS = len({f for _, f, _ in STACK})                                                                           # firms of the stacked regression
NUMERAIRE = {"OpenAI": "chatgpt_plus", "Google": "gemini_pro", "X Corp/xAI": "supergrok", "Microsoft": "m365_premium",
             "Character.AI": "characterai_plus", "Anthropic": "claude_pro"}                                              # each firm's $20 frontier tier (SuperGrok, $30, for X Corp/xAI)
_num = W8.firm.map(NUMERAIRE)
PAIRS_RULE = W8[W8.plan_b == _num].assign(other=lambda d: d.plan_a)                                                     # pairs 'as A, relative to its firm's standard frontier tier as B'
PAIRS_EXTRA = W8[W8.plan_b != _num]                                                                                      # the two X Corp pairs that hold the app fixed or compare the entry products
FIVE_FIRM_APPS = ["chatgpt", "gemini", "googleone", "youtube", "youtubemusic", "x", "grok", "copilot_m365", "characterai"]   # the apps of the five firms in wave2_item_slopes.csv
_e9 = islopes[islopes.app.isin(FIVE_FIRM_APPS) & (islopes.type == "subscription") & (islopes.n >= MIN_STORES_ITEM)]
_e9 = _e9[~_e9.name.str.contains(r"Annual|Promote Post")]                                                               # 'except annual variants and X's post-promotion product' (Table E.9 notes)
N_E9_RULE = len(_e9)                                                                                                     # Table E.9's inclusion rule applied to the item file (29 since the family variants joined the table)
E9_EXCLUDED = sorted(set(W2.index) - set(STACK_PLANS))                                                                   # items of Table E.9 outside the stacked regression (storage, family, creator)
STORAGE = ["gemini_100gb", "m365_basic"]                                                                                 # the storage plans of Table E.9
SECOND = ["googleone_aiplus2tb"]                                                                                         # the Google One app's second listing of Google AI Plus (2 TB), group capped_one
FAMILY = {"youtube_premium_family": "youtube_premium", "youtubemusic_family": "youtubemusic_music", "m365_family": "m365_personal"}   # family variant -> the plan it extends

P = S("The cleanest evidence needs no estimate of the platform's schedule.")
P.wpin("two", "two products of a firm in the same storefront (the pair A, B; structural)")
P.wpin("two", "the two local prices of the pair (structural)")
P.v("21", N_PAIRS, note="pairs of Table 3 (rows of W8_relative_pairs.csv, PAIRS of code/13_relative_prices.py; Microsoft 365 Family vs Premium dropped with the family variants)")
P.cond("the 21 pairs follow the stated rule: every plan of the stacked regression other than its firm's frontier numeraire, and each of Anthropic's higher tiers, against that numeraire (19 pairs), plus two further X Corp pairs",
       set(PAIRS_RULE.other) == (set(STACK_PLANS) - set(NUMERAIRE.values())) | {"claude_max5x", "claude_max20x"} and len(PAIRS_RULE) == len(STACK_PLANS) - 5 + 2
       and set(PAIRS_EXTRA.pair) == {"xprem_xplus", "xbasic_sglite"} and len(PAIRS_RULE) + len(PAIRS_EXTRA) == N_PAIRS, len(PAIRS_RULE))
f = P.sub("\\footnote{Inclusion rule.", "move with the plans they extend.}")
f.w("five", N_STACK_FIRMS, note="firms of the stacked regression (STACK in code/13_relative_prices.py)")
f.cond("the five firms are OpenAI, Google, X Corp/xAI, Microsoft and Character.AI", {f_ for _, f_, _ in STACK} == {"OpenAI", "Google", "X Corp/xAI", "Microsoft", "Character.AI"})
f.v("4", min(us2[p] for p in STACK_PLANS), note="'a U.S. price of $4 or more': the lowest U.S. price among the stacked items is X Premium Basic, $4.00 (W1_wave2_plans.csv)")
f.cond("every monthly subscription of the five firms priced below $4 in the U.S. is outside the stack (the $1.99 storage plans)", all(us2[p] < 4 for p in ("gemini_100gb", "m365_basic")) and all(us2[p] >= 4 for p in STACK_PLANS))
f.v("60", MIN_STORES_ITEM, note="storefronts per item (code/09b_wave2_items.py)")
f.pin("2", why="name of the item 'Google AI Plus (2 TB)', the Google One app's second listing (storage size)")
f.cond("the items excluded by name are the storage plans (Google One 100 GB, Microsoft 365 Basic), the Google One app's second listing of Google AI Plus (2 TB), the family variants "
       "(YouTube Premium Family, YouTube Music Family, Microsoft 365 Family) and X's creator subscription; annual variants and the post-promotion product are outside Table E.9 as well",
       E9_EXCLUDED == sorted(STORAGE + SECOND + list(FAMILY) + ["x_creator"]) and not W2.item_name.str.contains("Promote|Annual").any()
       and len(W2) == N_E9_RULE == len(STACK_PLANS) + 7 and not set(FAMILY) & set(STACK_PLANS), len(W2))
f.v("30", us2["supergrok"], note="SuperGrok, the X Corp/xAI numeraire")
f.v("9.99", us2["characterai_plus"], note="Character.AI+, the Character.AI numeraire")
f.cond("the standard frontier tiers (plan B of the rule pairs) are ChatGPT Plus, Google AI Pro, SuperGrok, Microsoft 365 Premium, Character.AI+ and Claude Pro, all frontier tiers",
       set(PAIRS_RULE.plan_b) == set(NUMERAIRE.values()) and all(STACK_GROUP.get(v, "frontier") == "frontier" for v in NUMERAIRE.values()), len(set(PAIRS_RULE.plan_b)))
f.w("two", len(PAIRS_EXTRA), note="the two X Corp pairs outside the rule: X Premium vs X Premium Plus, X Premium Basic vs SuperGrok Lite (W8_relative_pairs.csv)")
f.w("two", len({W8.set_index("pair").loc["xbasic_sglite", "plan_a"], W8.set_index("pair").loc["xbasic_sglite", "plan_b"]}), note="the two entry products of the pair X Premium Basic vs SuperGrok Lite")
f.pin("100", "100", why="name of the item 'Google One 100 GB' (storage size; named twice in the footnote)")
f.v("0.033", W2.loc["gemini_100gb", "slope"], note="USD income slope of Google One 100 GB in Appendix Table E.9 (W2_benchmarks.csv, the item-slope sample of code/09b)")
f.v("0.007", W2.loc["gemini_100gb", "se"], label="s.e. (Google One 100 GB)")
f.v("0.029", W2.loc["m365_basic", "slope"], note="Microsoft 365 Basic (Table E.9)")
f.v("0.011", W2.loc["m365_basic", "se"], label="s.e. (Microsoft 365 Basic)")
f.v("0.032", W2.loc["x_creator", "slope"], note="X's creator subscription (Table E.9; the plan-level sample of code/12, x_creator_usd_slope, gives 0.026 on 139 storefronts)")
f.v("0.009", W2.loc["x_creator", "se"], label="s.e. (X creator subscription)")
f.cond("'not localised either': the three excluded items have a median LMIC price ratio of one and a dollar slope below 0.10",
       all(W2.loc[k, "median_ratio_lmic"] == 1 and W2.loc[k, "slope"] < THR_SLOPE for k in ("gemini_100gb", "m365_basic", "x_creator")), W2.loc["x_creator", "median_ratio_lmic"])
f.v("0.36", W2.loc["youtube_premium_family", "slope"], note="YouTube Premium Family, USD slope of Table E.9 (W2_benchmarks.csv, group 'family')")
f.v("0.04", W2.loc["youtube_premium_family", "se"], label="s.e. (YouTube Premium Family)")
f.v("0.38", W2.loc["youtubemusic_family", "slope"], note="YouTube Music Family")
f.v("0.04", W2.loc["youtubemusic_family", "se"], label="s.e. (YouTube Music Family)")
f.v("0.056", W2.loc["m365_family", "slope"], note="Microsoft 365 Family")
f.v("0.010", W2.loc["m365_family", "se"], label="s.e. (Microsoft 365 Family)")
f.cond("'move with the plans they extend': each family variant is localised exactly when the plan it extends is (median LMIC ratio below 0.9 for YouTube Premium/Music and their family variants, "
       "Microsoft 365 Personal and Family alike), with a dollar slope on the same side of 0.10",
       all((W2.loc[k, "median_ratio_lmic"] < 0.9) == (W2.loc[v, "median_ratio_lmic"] < 0.9) and (W2.loc[k, "slope"] > THR_SLOPE) == (W2.loc[v, "slope"] > THR_SLOPE) for k, v in FAMILY.items())
       and all(W2.loc[k, "group"] == "family" for k in FAMILY), len(FAMILY))
P.v("10", 100 * (1 - BELOW09), note="more than 10% cheaper: e^d < 0.9 (code/13_relative_prices.py)")
P.wpin("two", "the two relative prices (the storefront's and the U.S. ratio) coincide: structural")

P = S("Income gradients of relative prices within firm and storefront, 16 October 2026")
P.dt("16 October 2026", d2)
P = S("Pair ($A$ vs $B$) & $N$ & Slope & (HC1) & [currency] & RI $p$ & median & $<0.9$ (\\%) & at 1 (\\%) \\\\")
P.v("0.9", BELOW09, label="share < 0.9 (header)")
P.v("1", math.exp(0.0), label="share at 1 (header): relative price e^0")
P = S("\\item \\emph{Notes:} Monthly App Store prices in storefronts other than the United States with income data. The outcome is")
P.w("two", len(PAIRS_EXTRA), note="'plus two X Corp pairs': the pairs of Table 3 whose second plan is not the firm's standard frontier tier")
P.cond("results_wave2.json carries the cluster counts of all 22 pairs", len(PAIR_KEYS) == N_PAIRS, len(PAIR_KEYS))
P.v("18", min(R2[f"rel_{k}_n_currencies"] for k in PAIR_KEYS), note="fewest currency clusters among the 22 pairs (Google AI Pro vs AI Ultra)")
P.v("41", max(R2[f"rel_{k}_n_currencies"] for k in PAIR_KEYS), note="most currency clusters (Character.AI Lite vs Character.AI+)")
P.wpin("two", "two-sided p-value (statistical term)")
P.v("2,000", N_PERM, note="permutations of the randomisation inference (code/13_relative_prices.py)")
P.cond("results_wave2.json records the same number of permutations", R2["rel_ri_permutations"] == N_PERM, R2["rel_ri_permutations"])
P.v("0.0005", 1 / N_PERM, note="'<0.0005': a p-value of zero of 2,000 permutations is printed as below 1/2,000 (code/42_tables_relative.py)")
P.v("0.9", BELOW09, label="share < 0.9 (notes)")
P.v("0.9", BELOW09, label="e^d < 0.9")
P.v("1", math.exp(0.0), label="share at 1 (notes)")
P.v("0.005", MASS_BAND, note="|d_c| < 0.005 (code/13_relative_prices.py)")
P.notation()

P = S("Income gradients of relative prices within firm and storefront. Slopes of Table")
P.v("1.96", snorm.ppf(0.975), note="97.5th percentile of the standard normal: 95% intervals")

P = S("Three results stand out.")
P.w("Three", len(re.findall(r"(?<![A-Za-z])(?:First|Second|Third), ", P.text)), note="First, Second and Third result")
f = P.sub("First, the relative prices of the AI tiers with large allowances", "(Appendix Table~\\ref{tab:cross_vendor}).")
f.w("nine", len(PAIRS_FF), note="frontier pairs of Table 3 (group_a = group_b = frontier in W8_relative_pairs.csv; rel_frontierpairs_n_pairs)")
f.cond("'measured as the higher tier relative to the firm's standard tier': in every frontier pair plan B is the firm's standard tier and plan A the higher tier (W8_relative_pairs.csv)",
       all(W8.set_index("pair").loc[k, "plan_b"] == NUMERAIRE[W8.set_index("pair").loc[k, "firm"]] for k in PAIRS_FF)
       and all(W1.loc[W8.set_index("pair").loc[k, "plan_a"], "us_price"] > W1.loc[W8.set_index("pair").loc[k, "plan_b"], "us_price"] for k in PAIRS_FF), len(PAIRS_FF))
f.v("0.022", R2["rel_frontierpairs_slope_min"], label="slopes between -0.022", note="ChatGPT Pro 500 relative to Plus (negative; rel_frontierpairs_slope_min)")
f.v("0.011", R2["rel_frontierpairs_slope_max"], label="and 0.011", note="X Premium Plus relative to SuperGrok (rel_frontierpairs_slope_max)")
f.cond("the bound keys are the min/max over the nine frontier pairs", abs(min(R2[f"rel_{k}_slope"] for k in PAIRS_FF) - R2["rel_frontierpairs_slope_min"]) < 1e-9
       and abs(max(R2[f"rel_{k}_slope"] for k in PAIRS_FF) - R2["rel_frontierpairs_slope_max"]) < 1e-9)
f.v("0.021", R2["rel_pro100_plus_slope"], label="ChatGPT Pro 100 relative to Plus (negative)")
f.v("0.007", R2["rel_pro200_plus_slope"], label="ChatGPT Pro 200 relative to Plus (negative)")
f.v("0.022", R2["rel_pro500_plus_slope"], label="ChatGPT Pro 500 relative to Plus (negative)")
f.v("0.008", R2["rel_sgplus_supergrok_slope"], label="SuperGrok Plus relative to SuperGrok (negative)")
f.v("0.0005", 1 / N_PERM, label="randomisation p < 0.0005 (Pro 100)", note="no permutation of 2,000 reached the observed slope: rel_pro100_plus_ri_p = 0, printed as below 1/2,000")
f.cond("Pro 100 and Pro 500 relative to Plus: randomisation p-value of zero (no permutation reached the slope)", R2["rel_pro100_plus_ri_p"] == 0 == R2["rel_pro500_plus_ri_p"])
f.v("0.0035", R2["rel_pro200_plus_ri_p"], label="randomisation p (Pro 200)")
f.v("0.0005", 1 / N_PERM, label="randomisation p < 0.0005 (Pro 500)")
f.v("0.11", R2["rel_sgplus_supergrok_ri_p"], label="randomisation p (SuperGrok Plus)")
f.cond("'these higher tiers are relatively dearer, not cheaper, in poorer storefronts': the four slopes are negative",
       all(R2[f"rel_{k}_slope"] < 0 for k in ("pro100_plus", "pro200_plus", "pro500_plus", "sgplus_supergrok")))
f.v("0.000", R2["rel_ultra_aipro_slope"], label="Google AI Ultra relative to AI Pro (0.00008)")
f.cond("SuperGrok Heavy relative to SuperGrok is 0.000 as well (one numeral for both pairs)", rnd(R2["rel_heavy_supergrok_slope"], 3) == Decimal("0.000"), R2["rel_heavy_supergrok_slope"])
f.v("20", MULT_ALLOW[1], note="allowance multiple in the plan name Claude Max 20x ('5' is auto-labelled after 'Max')")
f.v("0.009", R2["rel_max5_claudepro_slope"], label="Claude Max 5x relative to Pro")
f.v("0.007", R2["rel_max20_claudepro_slope"], label="Claude Max 20x relative to Pro")
f.v("0.011", R2["rel_xplus_supergrok_slope"], label="X Premium Plus relative to SuperGrok")
f.cond("'slightly cheaper': the three slopes are positive and below 0.02", all(0 < R2[f"rel_{k}_slope"] < 0.02 for k in ("max5_claudepro", "max20_claudepro", "xplus_supergrok")))
f.v("0.0015", R2["rel_max5_claudepro_ri_p"], label="randomisation p (Max 5x)")
f.v("0.0275", R2["rel_max20_claudepro_ri_p"], label="randomisation p (Max 20x)")
f.v("0.013", R2["rel_xplus_supergrok_ri_p"], label="randomisation p (X Premium Plus)")
f.cond("the nine frontier pairs are exactly the pairs the sentence names (Pro 100, Pro 200, Pro 500, SuperGrok Plus, AI Ultra, SuperGrok Heavy, Max 5x, Max 20x, X Premium Plus)",
       set(PAIRS_FF) == {"pro100_plus", "pro200_plus", "pro500_plus", "sgplus_supergrok", "ultra_aipro", "heavy_supergrok", "max5_claudepro", "max20_claudepro", "xplus_supergrok"})
f.wpin("two", "the two products of each pair (structural)")
f.v("45", 100 * min(R2[f"rel_{k}_mass_at1"] for k in PAIRS_FF), note="smallest mass at a relative price of one (|d| < 0.005) among the nine frontier pairs (ChatGPT Pro 500 relative to Plus, 0.454)")
f.v("95", 100 * max(R2[f"rel_{k}_mass_at1"] for k in PAIRS_FF), note="largest (SuperGrok Heavy vs SuperGrok, 0.953)")
f.w("three", N_FRONT_NUM, note="the three $19.99 frontier plans of the numeraire (FRONTIER in code/13_relative_prices.py)")
f.v("19.99", FRONTIER_US, note="U.S. price of the frontier numeraire (code/13_relative_prices.py)")
f.v("0.022", min(XV_SLOPES), note="smallest cross-vendor slope of the 13 $20-500 tiers under either numeraire (ChatGPT Pro 500 relative to ChatGPT Plus, -0.0219; Table E.10)")
f.v("0.003", max(XV_SLOPES), note="largest (Microsoft 365 Premium relative to the frontier median, 0.0031)")
f.v("20", np.median([us2[k] for k in STD]), label="$20-500 tiers (lower end)")
f.v("500", max(us2[k] for k in HIGH500), label="$20-500 tiers (upper end)")
f.w("six", N_VENDORS, note="vendors of the frontier tiers")
f.cond("the median relative price of the $20-500 tiers is exactly one in LMIC storefronts under both numeraires",
       all(R2[f"relplus_{k}_lmic_pct"] == 0 for k in XV_FRONT) and all(R2[f"relfront_{k}_lmic_pct"] == 0 for k in FRONT13))
f = P.sub("Second, the same firms localise their other subscriptions heavily.", "keep them at the default.")
f.v("0.20", R2["rel_ytprem_aipro_slope"])
f.v("0.09", R2["rel_ytprem_aipro_se_cr1"])
f.v("0.34", R2["rel_ytlite_aipro_slope"], label="YouTube Premium Lite relative to AI Pro")
f.v("0.08", R2["rel_ytlite_aipro_se_cr1"])
f.v("0.33", R2["rel_ytmusic_aipro_slope"])
f.v("0.07", R2["rel_ytmusic_aipro_se_cr1"])
f.w("three", len(W8[W8.plan_a.str.startswith("youtube") & (W8.plan_b == "gemini_pro")]), note="the three YouTube pairs of Table 3 (Premium, Premium Lite, Music, each relative to Google AI Pro)")
f.v("57", 100 * (1 - max(R2[f"rel_{k}_lmic_med"] for k in ("ytprem_aipro", "ytlite_aipro", "ytmusic_aipro"))), note="smallest LMIC discount of the three YouTube pairs: YouTube Premium relative to AI Pro, median relative price 0.43")
f.v("73", 100 * (1 - min(R2[f"rel_{k}_lmic_med"] for k in ("ytprem_aipro", "ytlite_aipro", "ytmusic_aipro"))), note="largest: YouTube Premium Lite 0.266 (YouTube Music 0.268)")
f.v("0.15", min(R2["rel_xprem_xplus_slope"], R2["rel_xprem_supergrok_slope"]), note="X Premium relative to X Premium Plus (0.150) or SuperGrok (0.158)")
f.v("0.16", max(R2["rel_xprem_xplus_slope"], R2["rel_xprem_supergrok_slope"]))
f.v("0.02", max(R2["rel_xprem_xplus_se_cr1"], R2["rel_xprem_supergrok_se_cr1"]), note="currency-clustered s.e. of both X Premium pairs (0.023, 0.024)")
f.cond("both X Premium pairs have a clustered s.e. that rounds to 0.02", rnd(R2["rel_xprem_xplus_se_cr1"], 2) == rnd(R2["rel_xprem_supergrok_se_cr1"], 2) == Decimal("0.02"))
f.v("55", 100 * (1 - R2["rel_xprem_supergrok_lmic_med"]), note="X Premium: median relative price 0.4545 in LMIC storefronts under both pairs (54.5% -> 55%)")
f.cond("X Premium's LMIC median is the same against X Premium Plus and against SuperGrok", R2["rel_xprem_xplus_lmic_med"] == R2["rel_xprem_supergrok_lmic_med"])
f.v("0.16", R2["rel_xbasic_sglite_slope"])
f.v("0.04", R2["rel_xbasic_sglite_se_cr1"])
f.v("50", 100 * (1 - R2["rel_xbasic_sglite_lmic_med"]))
f.v("0.011", R2["rel_m365pers_prem_slope"])
f.v("0.009", R2["rel_m365pers_prem_se_cr1"])
f.v("15", 100 * (1 - R2["rel_m365pers_prem_lmic_med"]))
_mhic = rel_long[(rel_long.pair == "m365pers_prem") & (rel_long.income_group == "High income")]
f.cond("'also cheaper in many rich ones': Personal is more than 10% cheaper relative to Premium than in the U.S. in more than a quarter of high-income storefronts (data/processed/wave2_relative_long.csv)",
       (_mhic.ln_rel < math.log(BELOW09)).mean() > 0.25, float((_mhic.ln_rel < math.log(BELOW09)).mean()), note="%d of %d high-income storefronts" % ((_mhic.ln_rel < math.log(BELOW09)).sum(), len(_mhic)))
f.pin("100", why="name of the item 'Google One 100 GB' (storage size)")
f.v("0.033", W2.loc["gemini_100gb", "slope"], note="U.S.-dollar slope of Google One 100 GB (Appendix Table E.9, W2_benchmarks.csv)")
f.v("0.029", W2.loc["m365_basic", "slope"], note="Microsoft 365 Basic (Table E.9)")
f.cond("'not localised either': the two storage plans have a median LMIC price ratio of one and dollar slopes below 0.10 (Table E.9)",
       all(W2.loc[k, "median_ratio_lmic"] == 1 and W2.loc[k, "slope"] < THR_SLOPE for k in ("gemini_100gb", "m365_basic")), W2.loc["gemini_100gb", "median_ratio_lmic"])
f.v("1.99", float(W2.loc["gemini_100gb", "us_price"]), note="'at $1.99': U.S. price of both storage plans (Google One 100 GB and Microsoft 365 Basic, W2_benchmarks.csv)")
f.cond("both storage plans are priced at $1.99 in the U.S.", W2.loc["gemini_100gb", "us_price"] == W2.loc["m365_basic", "us_price"] == 1.99)
f = P.sub("Third, localisation among AI products is confined to capped tiers", "U.S.-anchored ratio.")
f.v("0.104", R2["rel_go_plus_slope"])
f.v("0.007", R2["rel_go_plus_se_cr1"])
f.v("38", 100 * (1 - R2["rel_go_plus_lmic_med"]))
f.v("10", 100 * (1 - BELOW09), label="more than 10% cheaper")
f.v("80", 100 * R2["rel_go_plus_share_below09"])
f.v("0.08", R2["rel_cai_lite_plus_slope"])
f.v("0.03", R2["rel_cai_lite_plus_se_cr1"])
f.v("40", 100 * (1 - R2["rel_cai_lite_plus_lmic_med"]))
f.v("0.012", R2["rel_aiplus_aipro_slope"], label="Google AI Plus relative to AI Pro (negative)")
f.v("0.009", R2["rel_sglite_supergrok_slope"], label="SuperGrok Lite relative to SuperGrok (negative)")
f.cond("median relative price of one for Google AI Plus and SuperGrok Lite", R2["rel_aiplus_aipro_lmic_med"] == 1 == R2["rel_sglite_supergrok_lmic_med"])

P = S("Table~\\ref{tab:relative_stacked} pools the comparisons.")
P.v("0.20", R2["stacked_noai_gamma"])
P.wpin("two", "two-way clustered standard errors (statistical term)")
P.v("0.044", R2["stacked_noai_se"])
P.v("0.12", R2["stacked_smallai_gamma"])
P.v("0.051", R2["stacked_smallai_se"])
P.v("0.04", R2["stacked_capped_gamma"])
P.v("0.031", R2["stacked_capped_se"])
P.w("five", N_STACK_FIRMS, note="firms of the stacked regression (STACK in code/13_relative_prices.py)")
P.v("252,000", R2["stacked_ri_permutations"])
P.cond("the relabellings were enumerated exactly", bool(R2["stacked_ri_exact"]))
P.v("0.05", 100 * R2["stacked_noai_ri_p"], note="share of relabellings with a gap at least as large, no-allowance group (0.0476%; 120 of 252,000)")
P.v("0.006", 100 * R2["stacked_smallai_ri_p"], note="small-allowance group (0.0056%; 14 of 252,000)")
P.v("41", 100 * R2["stacked_capped_ri_p"], note="capped group (41.4%)")
P.cond("the randomisation p-values are the counts of relabellings divided by their number", all(abs(R2[f"stacked_{g}_ri_n_ge"] / R2["stacked_ri_permutations"] - R2[f"stacked_{g}_ri_p"]) < 1e-6 for g in ("noai", "smallai", "capped")))
P.v("0.10", R2["stacked_noai_gamma_usd"], note="no-allowance gap within the dollar storefronts (stacked_noai_gamma_usd)")
P.v("0.03", R2["stacked_noai_se_usd"], note="its two-way clustered s.e. (stacked_noai_se_usd)")
P.cond("the no- and small-allowance gradients are present within the dollar storefronts and larger within the local-currency storefronts",
       all(R2[f"stacked_{g}_gamma_usd"] > 0 and R2[f"stacked_{g}_gamma_lcu"] > R2[f"stacked_{g}_gamma_usd"] for g in ("noai", "smallai")), R2["stacked_noai_gamma_lcu"])
P.w("two", R2["applevel_ai_localise"], note="AI apps with at least one subscription item with a slope above 0.10 (applevel_ai_localise)")
P.w("eight", R2["applevel_ai_apps"], note="AI apps (class ai and ai_core) in the slope sample")
P.w("eight", R2["applevel_nonai_localise"], note="non-AI apps that localise at least one subscription")
P.v("21", R2["applevel_nonai_apps"])
P.cond("21 = the general subscription apps of the audit", R2["applevel_nonai_apps"] == N_NONAI)
P.v("0.67", R2["applevel_fisher_p"])

P = S("\\item \\emph{Notes:} OLS of $r_{ic}=\\ln(p_{ic}/P^{US}_i)$ on firm-by-storefront fixed effects")
P.v("22", R2["stacked_n_items"])
P.cond("22 = the items of STACK in code/13_relative_prices.py (Microsoft 365 Family dropped as a family variant)", R2["stacked_n_items"] == len(STACK_PLANS) == 22, len(STACK_PLANS))
P.w("five", N_STACK_FIRMS)
P.v("169", R2["stacked_n_storefronts"])
P.v("3,253", R2["stacked_n_obs"])
P.v("104", R2["stacked_n_storefronts_usd"])
P.v("65", R2["stacked_n_storefronts_lcu"])
P.cond("dollar and local-currency storefronts add up to the storefronts of the regression, and the observations likewise",
       R2["stacked_n_storefronts_usd"] + R2["stacked_n_storefronts_lcu"] == R2["stacked_n_storefronts"] and R2["stacked_n_obs_usd"] + R2["stacked_n_obs_lcu"] == R2["stacked_n_obs"])
_omit = re.search(r"The omitted group is the firm's AI tiers with large allowances \((.*?)\)\.", P.text).group(1)
P.cond("the omitted group lists the twelve frontier items of the stack (ChatGPT Plus, Pro 100, Pro 200, Pro 500; Google AI Pro, AI Ultra; X Premium Plus, SuperGrok, SuperGrok Plus, SuperGrok Heavy; Microsoft 365 Premium; Character.AI+)",
       sum(len(re.split(r", | and ", s)) for s in _omit.split("; ")) == sum(g == "frontier" for g in STACK_GROUP.values()), sum(g == "frontier" for g in STACK_GROUP.values()))
P.wpin("two", "two-way clustered (statistical term)")
P.v("252,000", R2["stacked_ri_permutations"])
P.notation()

# ================================================================================================ 5.2 income slopes of listed prices
P = S("Figure~\\ref{fig:prices} plots the local App Store price of ChatGPT Plus")
P.w("seventeen", N_T5, note="plans in the body of Table 5 (tab_wave2_plans.tex)")
P.w("nine", N_D1, note="plans in the body of Appendix Table E.1 (tab_local.tex)")
N_W1_PLANS = len({k for k in prices.plan.unique() if not k.endswith("_other")})         # the ten first-wave plans (gemini_plus_other collects the other Google AI Plus variants)
P.w("ten", N_W1_PLANS, note="plans of the three assistants in the first wave (data/processed/appstore_prices_long.csv, without the '_other' variants)")
P.w("three", N_CORE)
P.cond("the plan omitted from the first-wave table is Claude Max 20x", N_W1_PLANS - N_D1 == 1 and "Claude Max 20" not in (TAB / "tab_local.tex").read_text())
P.v("0.033", R2["claude_max20x_usd_slope"])
P.v("0.006", R2["claude_max20x_usd_se"])

# -- Figure 2 and Table 5
pc = prices[prices.price_usd.notna()].merge(panel.assign(storefront=panel.iso2.str.lower())[["storefront", "gni_atlas"]], on="storefront").dropna(subset=["gni_atlas"])
import statsmodels.formula.api as smf


def hc3_slope(plan):
    d = pc[pc.plan == plan].copy()
    d["ly"], d["lg"] = np.log(d.price_usd), np.log(d.gni_atlas)
    return float(smf.ols("ly ~ lg", d).fit(cov_type="HC3").params["lg"])


samePPP = csv("same_sample_ppp_comparison.csv").set_index("plan")
P = S("Local App Store prices of ChatGPT Plus and ChatGPT Go against income.")
P.dt("27 September 2026", d1)
P.v("0.23", R["plr_b"], note="slope on ln income of ln(PLR) = ln(Atlas / PPP income), 197 economies")

P = S("AI plans in U.S. dollars and relative to the platform's schedule, 16 October 2026")
P.dt("16 October 2026", d2)
P.notation()
P = S("Plan & price & $N$ & slope (s.e.) & slope (s.e.) & within $\\pm3\\%$ (\\%)", "ref.\\ (\\%) \\\\")
P.v("3", 100 * THR_WITHIN)
P.v("10", 100 * THR_BELOW)

P = S("\\item \\emph{Notes:} Monthly App Store prices on 16 October 2026 in storefronts other than the United States with income data and an estimated storefront multiplier")
P.dt("16 October 2026", d2)
P.v("161", R2["default_slope_n"], label="161 at most")
P.cond("161 is the largest N of Table 5", int(W1.loc[TAB5_PLANS, "n"].max()) == R2["default_slope_n"])
P.v("0.033", R2["default_slope"])
P.v("0.006", R2["default_slope_se"])
P.v("161", R2["default_slope_n"], label="N = 161")
P.v("10", 100 * THR_BELOW, label=">10% below")
P.v("0.10", -THR_BELOW, label="log deviation below -0.10")
P.v("100", PCT_CONV, note="percentage conversion 100 (e^d - 1) in code/12_default_panel.py")
P.v("1", PCT_ONE)
P.cond("the LMIC median column converts the median log deviation d to a percentage 100(e^d - 1)",
       abs(100 * (math.exp(R2["chatgpt_go_med_lmic_dev"]) - 1) - R2["chatgpt_go_med_lmic_pct"]) < 1e-3)
P.notation()

P = S("The standard and high-usage tiers of every vendor have nearly identical dollar prices across countries.")
f = P.sub("In the first wave the income slope is", "between 0.019 and 0.035;")
f.v("100", us2["chatgpt_pro100"], note="lowest price of the $100-250 tiers")
f.v("250", us1["claude_max20x"], note="highest price of the $100-250 tiers (Claude Max 20x, $249.99)")
f.v("0.039", R["loc_chatgpt_plus_b"])
f.v("0.006", R["loc_chatgpt_plus_se"])
f.v("0.026", R["loc_claude_pro_b"])
f.v("0.037", R["loc_gemini_pro_b"])
hi_w1 = [R["loc_chatgpt_pro5x_b"], R["loc_chatgpt_pro20x_b"], R["loc_claude_max5x_b"], R["loc_gemini_ultra_b"], hc3_slope("claude_max20x")]
f.v("0.019", min(hi_w1), note="smallest slope of the first-wave $100-250 tiers (Pro 5x, Pro 20x, Max 5x, Ultra; Max 20x recomputed, HC3)")
f.v("0.035", max(hi_w1))
f = P.sub("the second wave gives 0.016--0.039", "for the platform's schedule.")
f.v("0.016", min(R2[k + "_usd_slope"] for k in FRONT13), note="smallest second-wave dollar slope of the 13 $20 and $100-500 tiers of Table 5 (ChatGPT Pro 500, 0.0164)")
f.v("0.039", max(R2[k + "_usd_slope"] for k in FRONT13), note="largest (ChatGPT Plus, 0.0395)")
f.v("20", np.median([us2[k] for k in STD]), label="$20 tiers (second wave)")
f.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (lower end, second wave)")
f.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (upper end, second wave)")
f.w("six", N_VENDORS, note="vendors of the frontier tiers")
f.v("0.033", R2["default_slope"], label="the platform's schedule")
f = P.sub("For reference, the price-level proxy", "slope of one.")
f.v("0.228", R["plr_b"])
f.v("197", R["plr_n"])
f.v("0.243", samePPP.loc["chatgpt_go", "ppp_same_sample_beta"], note="same 164-economy sample as the ChatGPT Plus and Go price regressions")
f.v("164", samePPP.loc["chatgpt_go", "n"])
f = P.sub("The median local price of ChatGPT Plus is", "taxes.")
f.v("19.99", R["price_chatgpt_plus_UMIC"])
f.cond("the median is the same in the lower-middle- and low-income groups", R["price_chatgpt_plus_LMIC"] == R["price_chatgpt_plus_LIC"] == R["price_chatgpt_plus_UMIC"])
f.v("22.99", R["price_chatgpt_plus_HIC"])
f = P.sub("The dollar slopes above 0.10 belong to two capped AI tiers:")
f.v("0.10", THR_SLOPE, note="slope threshold (code/09b_wave2_items.py)")
ABOVE10 = [k for k in TAB5_PLANS if W1.loc[k, "usd_slope"] > THR_SLOPE] + [k for k in ("characterai_lite", "characterai_plus") if W1.loc[k, "usd_slope"] > THR_SLOPE]
f.w("two", len(ABOVE10), note="AI plans of Tables 5 and E.7 with a dollar slope above 0.10: " + ", ".join(ABOVE10))
f.cond("the two are ChatGPT Go and Character.AI Lite", set(ABOVE10) == {"chatgpt_go", "characterai_lite"})
f.v("0.143", R["loc_chatgpt_go_b"], label="Go slope, first wave")
f.cond("the second-wave slope is the same to three decimals", rnd(R2["chatgpt_go_usd_slope"], 3) == rnd(R["loc_chatgpt_go_b"], 3), R2["chatgpt_go_usd_slope"])
f.w("four", len(GROUPS), note="income groups")
f.v("9.05", R["price_chatgpt_go_HIC"])
f.v("5.99", R["price_chatgpt_go_UMIC"])
f.v("5.34", R["price_chatgpt_go_LMIC"])
f.v("4.99", R["price_chatgpt_go_LIC"])
f.v("4.16", go_usd["in"], note="India")
f.v("4.19", go_usd["id"], note="Indonesia")
f.v("0.12", R2["characterai_lite_usd_slope"], note="Character.AI Lite, dollar slope (Table E.7 reports the item-slope sample: 0.116)")
f.v("0.047", R2["m365_personal_usd_slope"])
f.v("4.99", R["price_gemini_plus_UMIC"])
f.w("three", len(GROUPS) - 1, note="the three non-high-income groups")
f.cond("flat at the same price in the three non-high-income groups", R["price_gemini_plus_UMIC"] == R["price_gemini_plus_LMIC"] == R["price_gemini_plus_LIC"] == 4.99)
f.v("0.018", R2["supergrok_lite_usd_slope"])

# ================================================================================================ 5.3 the platform's schedule: decomposition, validation and vintage
tie_rules = sorted({m.group(1) for k in R2 for m in [re.fullmatch(r"default_tie_([a-z]+)_slope", k)] if m})          # none, strict, fileorder, low, high
tie_untied = [r for r in tie_rules if r != "strict"]                          # the four treatments of 50/50 ties
go = pvd[(pvd.plan == "chatgpt_go") & pvd.dev_log.notna() & (pvd.gni > 0)]
go_at = go[go.dev_log.abs() <= THR_AT_DEFAULT]
ABOVE_UP = ["claude_pro", "claude_max5x", "claude_max20x", "perplexity_pro", "supergrok"]      # Claude Pro, Claude Max (5x and 20x), Perplexity Pro, SuperGrok
BELOW_DN = ["gemini_pro", "gemini_ultra", "m365_premium", "chatgpt_pro500"]                     # Google AI Pro, Google AI Ultra, Microsoft 365 Premium, ChatGPT Pro 500

P = S("The small positive slopes of the frontier tiers could be vendor pricing")
P.v("0.033", R2["default_slope"])
P.v("0.006", R2["default_slope_se"])
P.v("161", R2["default_slope_n"])
P.about("0.03", R2["default_slope"], 0.005, note="'a slope of about 0.03': rounds to the nearest hundredth")
P.v("0.026", min(R2[k + "_usd_slope"] for k in FRONTIER), note="smallest dollar slope of the nine frontier tiers of Section 5.2 (Claude Pro, Perplexity Pro)")
P.v("0.039", max(R2[k + "_usd_slope"] for k in FRONTIER), note="largest dollar slope of the nine frontier tiers (ChatGPT Plus)")

P = S("Deviation of listed prices from the platform's schedule, 16 October 2026.")
P.dt("16 October 2026", d2)
P.v("100", FIG_SCALE, note="the vertical axis is 100 x ln(listed / reference): code/31_figures_wave2.py")
P.w("three quarters", float(np.mean([W1.loc[k, "n_exact"] / W1.loc[k, "n"] for k in ("chatgpt_plus", "gemini_pro")])), tol=0.03,
    note="ChatGPT Plus 123 of 161 and Google AI Pro 121 of 159 storefronts have an observed modal price at their price point (0.76)")
P.cond("every storefront of ChatGPT Go and YouTube Premium uses the multiplier (no exact reference)", R2["chatgpt_go_n_exact"] == 0 == R2["youtube_premium_n_exact"])
P.notation()

P = S("\\paragraph{Frontier tiers.} Prediction P1 holds in the sense that")
P.v("20", np.median([us2[k] for k in STD]), label="$20 tiers")
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (lower end)")
P.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (upper end)")
P.w("six", N_VENDORS)
P.v("0.016", min(R2[k + "_dev_slope"] for k in FRONT13), note="smallest deviation slope: ChatGPT Pro 500 (negative)")
P.cond("the smallest deviation slope is ChatGPT Pro 500's and the largest ChatGPT Plus's",
       min(FRONT13, key=lambda k: R2[k + "_dev_slope"]) == "chatgpt_pro500" and max(FRONT13, key=lambda k: R2[k + "_dev_slope"]) == "chatgpt_plus")
P.v("0.004", R2["chatgpt_plus_dev_slope"])
P.v("95", 100 * (2 * snorm.cdf(snorm.ppf(0.975)) - 1), note="95% interval: estimate +/- 1.96 s.e.")
P.le("0.025", max(abs(R2[k + "_dev_slope"]) + snorm.ppf(0.975) * R2[k + "_dev_se"] for k in FRONT13),
     note="largest |slope| + 1.96 s.e. over the 13 frontier tiers (ChatGPT Pro 500: 0.0247)", label="every 95% interval within +/-0.025")
P.w("a quarter", 0.025 / R2["chatgpt_go_dev_slope"], tol=0.03, note="0.025 / 0.110 = 0.23")
_pv13 = pvd[pvd.plan.isin(FRONT13) & pvd.dev_log.notna() & (pvd.gni > 0)]
_medg = _pv13.groupby(["plan", "income_group"]).dev_log.median()
P.cond("the median deviation of each of the 13 frontier tiers is zero in low-, lower-middle- and upper-middle-income storefronts (med_lmic_dev of results_wave2.json; upper-middle from data/processed/wave2_plan_vs_default.csv)",
       all(R2[k + "_med_lmic_dev"] == 0 for k in FRONT13) and all(_medg[(k, g)] == 0 for k in FRONT13 for g in GROUPS[1:]))
_hic_med = {k: float(_medg[(k, "High income")]) for k in FRONT13}
P.w("seven", sum(v == 0 for v in _hic_med.values()), note="frontier tiers whose high-income median deviation is zero (wave2_plan_vs_default.csv): " + ", ".join(k for k, v in _hic_med.items() if v == 0))
P.v("13", len(FRONT13), note="the frontier tiers of Table 5: the $20 and $100-500 tiers of the six vendors")
P.le("0.04", max(abs(v) for v in _hic_med.values()), note="largest |high-income median deviation| among the rest: " + ", ".join(f"{k} {v:+.3f}" for k, v in _hic_med.items() if v != 0), label="within +/-0.04 for the rest")
P.v("3", 100 * THR_WITHIN, label="within 3% of the reference (Plus)")
P.v("87", 100 * R2["chatgpt_plus_within3"])
P.v("93", 100 * R2["chatgpt_plus_within3_exact"])
P.v("68", 100 * R2["chatgpt_plus_within3_extrap"])
P.v("108", R2["chatgpt_plus_clean_n"], note="storefronts with a clean multiplier and income data")
P.v("20", 100 * THR_CLEAN, note="spread threshold of a clean multiplier (code/12_default_panel.py)")
P.v("95", 100 * R2["chatgpt_plus_clean_within3"])
P.v("3", 100 * THR_WITHIN, label="within 3% (other frontier tiers)")
P.v("55", 100 * min(R2[k + "_within3"] for k in FRONT13 if k != "chatgpt_plus"), note="smallest within-3% share of the other 12 frontier tiers (Microsoft 365 Premium)")
P.v("73", 100 * max(R2[k + "_within3"] for k in FRONT13 if k != "chatgpt_plus"), note="largest (ChatGPT Pro 200)")
P.v("3", 100 * THR_WITHIN, label="more than 3% above")
P.cond("'above the extrapolated reference': none of Claude Pro, Claude Max, Perplexity Pro and SuperGrok has an exact (modal) reference anywhere (n_exact = 0)", all(R2[k + "_n_exact"] == 0 for k in ABOVE_UP))
P.v("25", 100 * min(R2[k + "_above3"] for k in ABOVE_UP), note="smallest share more than 3% above the reference among Claude Pro, Claude Max 5x and 20x, Perplexity Pro and SuperGrok (SuperGrok)")
P.v("37", 100 * max(R2[k + "_above3"] for k in ABOVE_UP), note="largest (Claude Max 5x)")
P.v("10", 100 * THR_BELOW, label="more than 10% above")
P.v("4", 100 * min(R2[k + "_above10"] for k in ABOVE_UP), note="smallest share more than 10% above (Perplexity Pro)")
P.v("15", 100 * max(R2[k + "_above10"] for k in ABOVE_UP), note="largest (Claude Max 20x)")
# the round-number check (code/12_default_panel.py, keys round_*): the two $20.00 plans of different vendors, Claude Pro and
# Perplexity Pro, listed at the same price in the taxed dollar storefronts (both at $25.00) and in the dollar storefronts whose tax factor is one (both at $22.00 in eight)
TAX_SF = sorted(mult[(mult.currency == "USD") & (mult.tax_factor > TAX_EMBED)].storefront)
TF1_SF = sorted(mult[(mult.currency == "USD") & ((mult.tax_factor - 1).abs() < 0.005)].storefront)
_p20 = pvd[pvd.plan.isin(["claude_pro", "perplexity_pro"]) & pvd.price_usd.notna()].pivot(index="storefront", columns="plan", values="price_usd").dropna()
_same20 = _p20[(_p20.claude_pro - _p20.perplexity_pro).abs() < 0.006]
_same20_tax, _same20_tf1 = _same20[_same20.index.isin(TAX_SF)], _same20[_same20.index.isin(TF1_SF)]
P.w("two", int((W1.loc[FRONT13, "us_price"] == 20.00).sum()), note="the two $20.00 plans among the frontier tiers: Claude Pro and Perplexity Pro (W1_wave2_plans.csv)")
P.v("20.00", us2["claude_pro"], note="U.S. price of Claude Pro (and of Perplexity Pro)")
P.cond("Claude Pro and Perplexity Pro are the two frontier tiers priced at $20.00 in the U.S.", set(W1.index[W1.us_price == 20.00]) & set(FRONT13) == {"claude_pro", "perplexity_pro"})
P.v("25.00", float(_same20_tax.claude_pro.round(2).mode().iloc[0]), note="the price at which both plans are listed in the 16 taxed dollar storefronts (data/processed/wave2_plan_vs_default.csv; round_usd16_both25_n)")
P.v("16", R2["round_usd16_both25_n"], label="both at $25.00 in all 16 taxed dollar storefronts")
P.cond("'in all 16': both plans are listed at the same price, $25.00, in every one of the 16 taxed dollar storefronts (keys round_usd16_n, round_usd16_both_n, round_usd16_both25_n; recomputed from the plan file)",
       R2["round_usd16_n"] == R2["round_usd16_both_n"] == R2["round_usd16_both25_n"] == R2["taxabs_n_storefronts"] == len(TAX_SF) == len(_same20_tax)
       == int((_same20_tax.claude_pro.round(2) == 25.00).sum()), len(TAX_SF))
P.v("22.00", float(_same20_tf1[_same20_tf1.claude_pro.round(2) == 22.00].claude_pro.round(2).iloc[0]), note="both plans at $22.00 in eight dollar storefronts whose panel tax factor is one (round_tf1_both22_n)")
P.w("eight", R2["round_tf1_both22_n"], note="dollar storefronts with a tax factor of one (|tax_factor - 1| < 0.005; 87 storefronts, round_tf1_usd_n) in which both plans are listed at $22.00")
P.cond("the round-number keys of results_wave2.json are reproduced from the plan and multiplier files: 87 dollar storefronts with a tax factor of one, both plans at the same price in 84, at $22.00 in 8 and at $20.00 in 73",
       R2["round_tf1_usd_n"] == len(TF1_SF) and R2["round_tf1_both_n"] == len(_same20_tf1) and R2["round_tf1_both22_n"] == int((_same20_tf1.claude_pro.round(2) == 22.00).sum()) == 8
       and R2["round_tf1_both20_n"] == int((_same20_tf1.claude_pro.round(2) == 20.00).sum()), R2["round_tf1_both_n"])
_pts99 = sum(abs(round(p * 100) % 100 - 99) < 1e-9 for p in US_PTS.index)
P.pin("99", why="the $X.99 price-point convention: %d of the %d U.S. price points of the default panel end in .99 ('almost all'), none is a round-dollar point" % (_pts99, len(US_PTS)))
P.cond("'the panel's items, almost all at $X.99 price points': more than 80% of the panel's U.S. price points end in .99 and none is a whole-dollar point (data/processed/wave2_default_items_long.csv)",
       not any(abs(p - round(p)) < 1e-9 for p in US_PTS.index) and _pts99 > 0.8 * len(US_PTS), len(US_PTS),
       note="points not ending in .99: " + ", ".join(f"{p:.2f}" for p in US_PTS.index if abs(round(p * 100) % 100 - 99) > 1e-9))
P.v("10", 100 * THR_BELOW, label="more than 10% below")
P.v("11", 100 * min(R2[k + "_below10"] for k in BELOW_DN), note="smallest share more than 10% below among Google AI Pro, Google AI Ultra, Microsoft 365 Premium and ChatGPT Pro 500")
P.v("16", 100 * max(R2[k + "_below10"] for k in BELOW_DN), note="largest (Google AI Pro)")
P.v("60", R2["chatgpt_go_dev_n_nonusd"], note="storefronts not priced in U.S. dollars in the deviation regressions (chatgpt_go_dev_n_nonusd = chatgpt_plus_dev_n_nonusd; the robustness paragraph is in Appendix E)")
P.v("16", R2["taxabs_n_storefronts"], label="the 16 dollar-priced storefronts")
P.v("5", 100 * (TAX_EMBED - 1), note="tax of more than 5%: tax_factor > 1.05")
P.v("19.99", us2["gemini_pro"], label="AI Pro at exactly $19.99")
P.v("15", R2["taxabs_gemini_pro_at_us"])
P.v("199.99", us2["gemini_ultra"])
P.v("8", R2["taxabs_gemini_ultra_at_us"], label="AI Ultra at the U.S. price in all 8")
P.cond("AI Ultra is offered in 8 of the 16 storefronts and listed at the U.S. price in all of them", R2["taxabs_gemini_ultra_n"] == R2["taxabs_gemini_ultra_at_us"] == 8)
P.pin("365", why="product name Microsoft 365 Premium")
P.v("19.99", us2["m365_premium"], label="365 Premium at $19.99")
P.v("10", R2["taxabs_m365_premium_at_us"])
P.v("11", R2["taxabs_chatgpt_plus_at_default"])
P.w("Ten", R2["taxabs_n_lmic_storefronts"], note="low- and lower-middle-income storefronts among the 16 taxed dollar storefronts (taxabs_n_lmic_storefronts)")
P.v("16", R2["taxabs_n_storefronts"], label="Ten of these 16 storefronts")
P.cond("the ten are the taxed dollar storefronts whose income group is low or lower-middle (data/processed/wave2_default_multiplier.csv)",
       int(mult[mult.storefront.isin(TAX_SF) & mult.income_group.isin(["Low income", "Lower-middle income"])].storefront.nunique()) == R2["taxabs_n_lmic_storefronts"], R2["taxabs_n_lmic_storefronts"])
P.v("19.99", us2["gemini_pro"], label="AI Pro at $19.99 in all ten")
P.w("ten", R2["taxabs_gemini_pro_at_us_lmic"], note="Google AI Pro at the U.S. price in all ten LMIC taxed dollar storefronts (taxabs_gemini_pro_at_us_lmic = taxabs_gemini_pro_n_lmic)")
P.cond("'in all ten': AI Pro is listed in all ten and at the U.S. price in all ten", R2["taxabs_gemini_pro_n_lmic"] == R2["taxabs_gemini_pro_at_us_lmic"] == R2["taxabs_n_lmic_storefronts"])
P.v("19.99", us2["chatgpt_plus"], label="Plus at $19.99 in five")
P.w("five", R2["taxabs_chatgpt_plus_at_us_lmic"], note="OpenAI lists Plus at the U.S. price in five of the ten (taxabs_chatgpt_plus_at_us_lmic)")

P = S("\\paragraph{Entry tiers.} Prediction P2 holds for ChatGPT Go.")
P.v("0.110", R2["chatgpt_go_dev_slope"])
P.v("0.006", R2["chatgpt_go_dev_se"], label="Go deviation s.e.")
P.v("14", 100 * R2["chatgpt_go_within3"])
P.v("3", 100 * THR_WITHIN, label="within 3% of the reference")
P.v("75", 100 * R2["chatgpt_go_below10"])
P.v("10", 100 * THR_BELOW, label="more than 10% below")
P.v("38", -R2["chatgpt_go_med_lmic_pct"])
P.v("98", 100 * R2["go_lmic_share_below10"])
P.v("50", R2["go_lmic_n"], note="low- and lower-middle-income storefronts with a Go listing and income data")
P.v("10", 100 * THR_BELOW, label="more than 10% below (LMIC)")
P.v("6", -100 * (math.exp(R2["go_hic_median_dev"]) - 1), note="median Go deviation in high-income storefronts as a percentage, 100(e^d - 1)")
P.v("0.5", 100 * THR_AT_DEFAULT, note="at the reference: |dev| <= 0.005 (code/12_default_panel.py)")
P.v("18", R2["go_exact_default_n"], note="storefronts at the reference, |dev| <= 0.005")
P.v("17", int((go_at.currency == "USD").sum()), note="of the %d storefronts at the reference priced in U.S. dollars (data/processed/wave2_plan_vs_default.csv)" % len(go_at))
P.cond("most of the storefronts at the reference are high-income economies (the text says 'most of them')",
       len(go_at) == R2["go_exact_default_n"] and (go_at.income_group == "High income").sum() / len(go_at) > 0.5,
       int((go_at.income_group == "High income").sum()),
       note="%d of %d are high-income; the others: %s"
            % ((go_at.income_group == "High income").sum(), len(go_at),
               ", ".join("%s (%s, %s)" % (c, g.split()[0].lower(), cur) for c, g, cur in zip(go_at[go_at.income_group != "High income"].storefront, go_at[go_at.income_group != "High income"].income_group, go_at[go_at.income_group != "High income"].currency))))
P.v("0.021", R2["m365_personal_dev_slope"])
P.v("0.007", R2["m365_personal_dev_se"])
P.v("15", -R2["m365_personal_med_lmic_pct"])
P.v("0.091", R2["characterai_lite_dev_slope"])
P.v("0.012", R2["characterai_lite_dev_se"])
P.v("40", -R2["characterai_lite_med_lmic_pct"])
P.w("two", len(PAIRS_CAPPED) - len(LOC_CAPPED), note="the two other capped AI tiers: Google AI Plus and SuperGrok Lite")
P.v("0.003", R2["gemini_plus_dev_slope"], label="Google AI Plus deviation slope (negative)")
P.v("0.016", R2["supergrok_lite_dev_slope"], label="SuperGrok Lite deviation slope (negative)")
P.cond("median deviation of zero for Google AI Plus and SuperGrok Lite in LMIC storefronts", R2["gemini_plus_med_lmic_dev"] == 0 == R2["supergrok_lite_med_lmic_dev"])
P.w("two", len(PAIRS_CAPPED) - len(LOC_CAPPED), note="capped tiers that are not localised")
P.w("four", len(PAIRS_CAPPED), note="capped AI tiers: ChatGPT Go, Google AI Plus, SuperGrok Lite, Character.AI Lite")

# the robustness paragraph of Appendix E (before Table E.14)
P = S("\\paragraph{Robustness of the deviation slopes (Section~\\ref{sec:decomp}).}")
P.le("0.0003", max(abs(W1.usd_slope_altfx - W1.usd_slope)), note="largest change of a dollar slope over the plans of W1 when the independent exchange rates are used")
P.v("0.040", R2["chatgpt_plus_usd_slope_altfx"])
P.v("0.143", R2["chatgpt_go_usd_slope_altfx"])
P.w("four", len(tie_untied), note="treatments of 50/50 ties in the revealed default: none, fileorder, low, high (strict is the separate majority rule)")
P.v("0.0325", min(R2[f"default_tie_{r}_slope"] for r in tie_untied))
P.v("0.0329", max(R2[f"default_tie_{r}_slope"] for r in tie_untied))
P.v("0.110", min(R2[f"default_tie_{r}_go_dev_slope"] for r in tie_untied))
P.v("0.111", max(R2[f"default_tie_{r}_go_dev_slope"] for r in tie_untied))
P.w("half", MODE_SHARE, note="the strict rule discards price points whose mode accounts for exactly half of the items")
P.v("0.027", R2["default_tie_strict_slope"])
P.v("147", R2["default_tie_strict_slope_n"])
P.v("0.110", R2["default_tie_strict_go_dev_slope"], label="Go slope under the strict rule")
P.lt("0.01", R2["default_tie_strict_plus_dev_slope"], note="Plus deviation slope under the strict rule")
P.v("60", R2["chatgpt_go_dev_n_nonusd"], note="storefronts not priced in U.S. dollars in the Go deviation regression")
P.cond("Plus has the same 60 non-dollar storefronts", R2["chatgpt_plus_dev_n_nonusd"] == R2["chatgpt_go_dev_n_nonusd"])
P.v("0.109", R2["chatgpt_go_dev_slope_nonusd"])
P.v("0.025", R2["chatgpt_go_dev_se_nonusd"])
P.v("0.000", R2["chatgpt_plus_dev_slope_nonusd"], label="Plus, non-dollar storefronts (-0.000)")
P.v("0.024", R2["chatgpt_plus_dev_se_nonusd"])
P.v("0.150", R2["chatgpt_go_dev_slope_popw"])
P.v("0.030", R2["chatgpt_go_dev_se_popw"])
P.v("0.000", R2["chatgpt_plus_dev_slope_popw"], label="Plus, population-weighted")
P.v("0.007", R2["chatgpt_plus_dev_se_popw"])
P.lt("0.0002", HC3_MAXDIFF, note="largest |HC3 - HC1| deviation standard error over the 17 plans of Table 5 (dev_se_hc3 against dev_se in W1_wave2_plans.csv)", label="|HC3 - HC1| < 0.0002 (Table 5)")

# -- validation
COINC_BAND = grab(SRC14, r'ex\["at_modal"\] = ex\.dev_log\.abs\(\) <= ([0-9.]+)', "coincidence band")            # 0.005
P05, P95 = (float(x) for x in re.findall(r"lower_quantile\(half_slopes, (0\.\d+)\)\)\)", SRC14)[:2])            # 0.05, 0.95
WEAK6 = re.findall(r'\("([a-z]{2})", 1\)', SRC14)                                                              # in, br, eg, ug, ng, tr
P = S("\\paragraph{Validation of the schedule.}")
P.wpin("five", "the five checks the paragraph walks through: rebuild, income slope under alternative rules, leave-one-app-out, split half, coincidence with the vendors' listings (structural)")
P.cond("rebuilding the ladder and the multipliers from the panel's items reproduces the shipped files exactly",
       R2["val_rebuild_max_logdiff"] == 0 and R2["val_rebuild_ladder_diff"] == 0 and R2["val_rebuild_n"] == R2["default_multiplier_storefronts"], R2["val_rebuild_n"])
P.v("0.0327", R2["val_slope_main"])
P.cond("the main-rule slope of the validation equals the schedule slope of code/12", R2["val_slope_main"] == R2["default_slope"] and R2["val_slope_main_n"] == R2["default_slope_n"])
P.v("0.0272", R2["val_slope_strict"])
P.cond("the strict-rule slope equals the tie-rule sensitivity of code/12", abs(R2["val_slope_strict"] - R2["default_tie_strict_slope"]) < 1e-6)
P.v("0.0331", R2["val_slope_sub"])
P.v("0.029", R2["val_loo_slope_min"])
P.v("0.035", R2["val_loo_slope_max"])
P.v("300", N_SPLITS)
P.cond("results_wave2.json records 300 splits", R2["val_split_reps"] == N_SPLITS, R2["val_split_reps"])
P.wpin("two", "the two halves of a split (structural)")
P.v("0.021", R2["val_split_slope_p05"])
P.v("0.041", R2["val_split_slope_p95"])
P.v("5", 100 * P05, note="5th percentile of the half-sample slopes (code/14_default_validation.py)")
P.v("95", 100 * P95, note="95th percentile")
P.v("117", R2["val_coinc_chatgpt_plus_exact"])
P.v("126", R2["val_coinc_chatgpt_plus_rows"])
P.v("73", R2["val_coinc_gemini_pro_exact"])
P.v("124", R2["val_coinc_gemini_pro_rows"])
P.v("67", R2["val_coinc_m365_premium_exact"])
P.v("125", R2["val_coinc_m365_premium_rows"])
P.v("33", R2["val_coinc_anom_storefronts"])
P.v("20", 100 * (ANOM_FX - 1), note="departure from exchange-rate parity by more than 20%: |ln(tax factor)| > ln 1.2 (code/14_default_validation.py)")
P.v("24", R2["val_coinc_anom_exact"])
P.v("69", R2["val_coinc_anom_rows"])
P.cond("the six weak storefronts named are India, Brazil, Egypt, Uganda, Nigeria and Turkiye (WEAK of code/14)", WEAK6 == ["in", "br", "eg", "ug", "ng", "tr"], len(WEAK6))
P.v("0.33", R2["val_weak6_median_share_min"], note="smallest median modal share among the six weak storefronts (Turkiye)")
P.v("0.50", R2["val_weak6_median_share_max"], note="largest (Uganda)")
P.cond("no price point of a frontier plan has a unique mode in the six weak storefronts", R2["val_weak6_frontier_exact_points"] == 0 and all(R2[f"val_weak_{s}_frontier_exact_points"] == 0 for s in WEAK6))
P.cond("Nigeria and Turkiye have no multiplier", "val_weak_ng_multiplier" not in R2 and "val_weak_tr_multiplier" not in R2 and not set(mult.storefront) & {"ng", "tr"})
P.v("8.00", us2["chatgpt_go"])
P.cond("no panel item uses the $8.00 price point", 8.00 not in set(US_PTS.index) and R2["chatgpt_go_n_exact"] == 0)
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (lower end)")
P.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (upper end)")
P.cond("the $100-500 tiers are extrapolated everywhere (n_exact = 0)", all(R2[k + "_n_exact"] == 0 for k in HIGH500))

P = S("\\item \\emph{Notes:} Panel of 30 small-developer apps")
P.v("30", R2["default_apps"])
P.v("28", R2["default_apps"] - R2["default_panel_apps_without_priced_subscription"], note="apps with a priced subscription item (default_panel_apps_without_priced_subscription = 2 of 30)")
_dus = ditems[(ditems.storefront == "us") & (ditems.price_local > 0)]
P.cond("of the two apps without a priced subscription item, one lists only a consumable in the U.S. and one no priced item at all (data/processed/wave2_default_items_long.csv)",
       R2["default_apps"] - _dus.app.nunique() == 1 and _dus.app.nunique() - _dus[_dus.type == "subscription"].app.nunique() == 1
       and R2["val_loo_apps"] == _dus.app.nunique(), _dus.app.nunique(), note="29 apps have a priced item of any type (val_loo_apps), 28 a priced subscription")
P.dt("16 October 2026", d2)
P.v("300", N_SPLITS)
P.v("20261016", SPLIT_SEED, note="seed of the split-half test (code/14_default_validation.py)")
P.v("0.5", 100 * COINC_BAND, note="listed within 0.5% of the modal price: |dev| <= 0.005")
P.notation()

# -- vintage
VINT_FRONT = ["chatgpt_plus", "chatgpt_pro200", "claude_pro", "claude_max20x", "gemini_pro", "gemini_ultra", "perplexity_pro", "supergrok", "supergrok_heavy", "m365_premium"]
P = S("\\paragraph{Vintage.} Apple does not refresh the generated price")
_n_impl = len(re.findall(r"should be ", P.text[:P.text.index("The first two hold and the third largely")]))
P.w("two", _n_impl - 1, note="'the first two hold and the third largely': the three implications of the previous sentence ('should be centred', 'should be larger', 'should be rare'), of which the first two hold")
P.cond("the three implications are three", _n_impl == 3, _n_impl)
P.cond("first implication, centred on zero: the pooled median deviation is zero and the pooled income slope is within one storefront-clustered s.e. of zero",
       R2["vint_frontier_median_dev"] == 0 and abs(R2["vint_frontier_slope"]) < R2["vint_frontier_se_sf"], R2["vint_frontier_slope"])
P.cond("second implication, larger where the currency moved more: the coefficient of the absolute deviation on the FX range is positive and more than two storefront-clustered s.e. above zero",
       R2["vint_frontier_absdev_fx"] > 2 * R2["vint_frontier_absdev_fx_se_sf"], R2["vint_frontier_absdev_fx"])
P.cond("third implication holds 'largely': most but not all dollar-storefront rows are within 3% of the reference (81%)",
       0.5 < R2["vint_frontier_within3_usd"] < 1, R2["vint_frontier_within3_usd"])
P.w("ten", len(VINT_FRONT), note="frontier plans pooled in the vintage test (code/15_vintage_test.py)")
P.v("1,489", R2["vint_frontier_n"])
P.cond("the pooled rows are the ten plans' rows", R2["vint_frontier_n"] == sum(R2[f"vint_{k}_n"] for k in VINT_FRONT))
P.v("0.0014", R2["vint_frontier_slope"], label="pooled income slope (negative)")
P.v("0.0028", R2["vint_frontier_se_sf"], note="standard error clustered by storefront (vint_frontier_se_sf)")
P.cond("the pooled median deviation is zero", R2["vint_frontier_median_dev"] == 0)
P.dt("March 2024", FX_DATES[0], note="first exchange-rate snapshot (6 March 2024)")
P.v("0.54", R2["vint_frontier_absdev_fx"])
P.v("0.23", R2["vint_frontier_absdev_fx_se_sf"], note="clustered by storefront (vint_frontier_absdev_fx_se_sf)")
P.v("81", 100 * R2["vint_frontier_within3_usd"])
P.v("3", 100 * VINT_BAND, note="within 3%: |dev| <= 0.03 (code/15_vintage_test.py)")
P.v("41", 100 * R2["vint_frontier_within3_stable"])
P.v("10", 100 * (FX_STABLE - 1), note="stable: currency moved by at most ln 1.1")
P.v("22", 100 * R2["vint_frontier_within3_moved"])
P.v("30", 100 * (FX_MOVED - 1), note="moved: by more than ln 1.3")
P.v("0.007", R2["vint_frontier_slope_ctrl"], label="frontier slope with the FX control (negative)")
P.v("0.007", R2["vint_frontier_se_ctrl_sf"], label="its storefront-clustered s.e.", note="vint_frontier_se_ctrl_sf, 0.0066")
P.v("0.108", R2["vint_go_slope_ctrl"])
P.v("0.010", R2["vint_go_se_ctrl_sf"], note="ChatGPT Go, one row per storefront: the storefront-clustered s.e. equals the HC1 s.e. (0.0097)")

# -- other channels
P = S("\\paragraph{Other channels.}")
P.pin("15", "30", why="Apple's commission rates (platform policy)")
P.v("5", 100 * XCH_BAND, label="within 5% (ChatGPT)", note="|ln(Play / App Store)| <= 0.05 (code/16_cross_channel.py)")
P.v("22", R2["xch_play_chatgpt_within5_n"])
P.v("25", R2["xch_play_chatgpt_same_currency"])
P.v("20", R2["xch_play_chatgpt_exact_n"], note="same-currency countries in which the lowest Play item is 'identical' to the App Store Go price, |ln difference| < 0.005 in code/16 (xch_play_chatgpt_exact_n; 19 equal to the cent)")
P.cond("median log difference zero (ChatGPT on Play against the App Store Go price)", R2["xch_play_chatgpt_median"] == 0)
P.v("37", 100 * (1 - R2["xch_play_chatgpt_lmic_ratio"]), note="lowest ChatGPT item in dollars relative to the U.S. price, median over the LMIC countries with a storefront: 0.63")
P.v("5", 100 * XCH_BAND, label="within 5% (Claude)")
P.v("12", R2["xch_play_claude_within5_n"], note="Claude's lowest Play item within 5% of the App Store Pro price (xch_play_claude_within5_n)")
P.v("25", R2["xch_play_claude_same_currency"], label="12 of 25 (Claude)")
P.v("1.05", R2["xch_play_claude_lmic_ratio"])
P.pin("365", why="product name Microsoft 365 Personal and Premium ('for 365 Personal': the auto-label covers 'Microsoft 365' only)")
P.v("5", 100 * XCH_BAND, label="within 5% (Microsoft)")
P.v("49", R2["xch_ms_web_vs_app_premium_n"], note="'each within 5% of the App Store prices in all 49 same-currency countries': 49 comparisons for Premium and 49 for Personal, all within 5%")
P.v("37", R2["xch_ms_web_vs_app_premium_exact_n"], note="'identical to the cent in 37 of 49': |web - App Store| < 0.005 in the storefront's currency (xch_ms_web_vs_app_premium_exact_n = _personal_exact_n)")
P.v("49", R2["xch_ms_web_vs_app_personal_n"], label="37 of 49")
P.cond("37 to the cent for Personal as well; 'median difference zero' for both plans", R2["xch_ms_web_vs_app_personal_exact_n"] == R2["xch_ms_web_vs_app_premium_exact_n"]
       and R2["xch_ms_web_vs_app_premium_median"] == 0 == R2["xch_ms_web_vs_app_personal_median"])
P.cond("all 49 comparisons of both plans are within 5%, median log difference zero",
       R2["xch_ms_web_vs_app_premium_within5"] == 1 == R2["xch_ms_web_vs_app_personal_within5"] and R2["xch_ms_web_vs_app_personal_n"] == R2["xch_ms_web_vs_app_premium_n"] == 49
       and R2["xch_ms_web_vs_app_premium_within5_n"] == R2["xch_ms_web_vs_app_personal_within5_n"] == 49)
P.v("0.082", R2["xch_ms_slope"])
P.v("0.018", R2["xch_ms_slope_se"])
P.v("31", -R2["xch_ms_lmic_pct"], note="India is the only LMIC country with a web price (xch_ms_lmic_n = 1)")
P.cond("India is the only low- or lower-middle-income country with a Microsoft web price", R2["xch_ms_lmic_n"] == 1)
P.cond("India's App Store ratio is also 31% below the U.S. ratio ('on both channels'): Microsoft 365 Personal relative to Premium in the Indian storefront",
       abs(round(100 * (math.exp(rel_long[(rel_long.pair == "m365pers_prem") & (rel_long.storefront == "in")].ln_rel.iloc[0]) - 1)) - round(R2["xch_ms_lmic_pct"])) == 0,
       float(100 * (math.exp(rel_long[(rel_long.pair == "m365pers_prem") & (rel_long.storefront == "in")].ln_rel.iloc[0]) - 1)))
S("The small-developer panel separates the two.").wpin("two", "vendor pricing and the platform's conversion (structural)")
S("the slopes of the half-samples lie between").wpin("half", "half-samples of the split-half test (each half holds 14 or 15 of the 29 apps; name of the check)")
P = S("\\item \\emph{Notes:} Panel of 30 small-developer apps")
P.wpin("half", "split-half test (name of the check)")
P.wpin("two", "the two halves of a split (structural)")
S("of the App Store Go price in 22 of the 25 countries where the two stores").wpin("two", "the two stores compared: Google Play and the App Store (structural)")

# ================================================================================================ 5.4 the within-storefront ratio and the dollar increment
pp = prices[prices.plan.isin(["chatgpt_plus", "chatgpt_go"]) & prices.price_local.notna()].pivot(index="storefront", columns="plan", values="price_local").dropna()
pp["ratio"] = pp.chatgpt_plus / pp.chatgpt_go
pp["g"] = panel.assign(storefront=panel.iso2.str.lower()).set_index("storefront").income_group.reindex(pp.index)
w1_ratio = {SH[g]: float(pp[pp.g == g].ratio.median()) for g in GROUPS}
wr = csv("within_storefront_price_ratios.csv").set_index("comparison")
mm = csv("matched_menu_currency_sensitivity.csv", PU).set_index("specification")
INCR_PAIRS = sorted({m.group(1) for k in R2 for m in [re.fullmatch(r"incr_(.+)_slope", k)] if m})          # the five pairs of Table 7
INCR_FRONT = ["pro200_plus", "aipro_aiplus"]                                                               # increments called flat in the text (Pro 200 over Plus, AI Pro over AI Plus); 365 Premium over Personal is quoted separately

P = S("Because both plans are listed in the same storefront under the same currency and tax rule")
P.v("2.5", PG["US"])
P.v("2.9", PG["HIC"])
P.v("3.3", PG["UMIC"])
P.v("3.8", PG["LMIC"])
P.v("4.0", PG["LIC"])
P.cond("the wave-1 medians of the Plus-to-Go ratio equal the wave-2 medians in all four income groups (identical in both waves)",
       all(abs(w1_ratio[k] - PG[k]) < 1e-5 for k in ("HIC", "UMIC", "LMIC", "LIC")) and abs(us1["chatgpt_plus"] / us1["chatgpt_go"] - PG["US"]) < 1e-5,
       w1_ratio["LIC"])
P.v("167", R2["plusgo_ratio_n"])
P.v("0.104", wr.loc["ChatGPT Go / Plus", "slope"], note="slope of ln(Go/Plus) on ln(GNI): the sign convention of the pipeline is Go over Plus")
P.v("0.007", wr.loc["ChatGPT Go / Plus", "se_currency_cluster"])
P.v("164", wr.loc["ChatGPT Go / Plus", "n"])
P.v("0.104", -wr.loc["ChatGPT Go / Plus", "slope"], label="-0.104 for the Plus-to-Go ratio")
P.cond("on the common sample the ratio slope equals the difference between the Go and Plus slopes",
       abs(wr.loc["ChatGPT Go / Plus", "slope"] - (R["loc_chatgpt_go_b"] - R["loc_chatgpt_plus_b"])) < 1e-6,
       R["loc_chatgpt_go_b"] - R["loc_chatgpt_plus_b"])
P.v("0.113", mm.loc["USD only", "slope"])
P.v("102", mm.loc["USD only", "n"])
P.v("0.112", mm.loc["Exclude USD", "slope"])
P.v("0.125", mm.loc["Exclude USD and EUR", "slope"])

P = S("The ChatGPT Go-to-Plus price ratio within storefronts.")
P.dt("27 September 2026", d1)
P.dt("16 October", d2)

P = S("The ratio rises as income falls under every regime of the model")
P.w("two", N_PAIR_PLANS, note="the two plans of the increment: ChatGPT Plus and Go (W12_increment.csv)")
P.wpin("two", "the two measurements of Table 7: relative to the schedule increment and in dollars relative to the U.S. increment (structural)")
P.wpin("two", "the two plans' schedule prices (structural)")
P.v("4", 100 * (R2["incr_plus_go_med_hic"] - 1), note="median ratio of the Plus-Go dollar gap to the schedule gap, high-income storefronts (1.035)")
P.v("17", 100 * (R2["incr_plus_go_med_umic"] - 1), note="upper-middle-income (1.168)")
P.v("25", 100 * (R2["incr_plus_go_med_lmic"] - 1), note="lower-middle-income (1.250); low-income 1.251 rounds to the same 25%")
P.cond("the low-income median also rounds to 25% wider", round(100 * (R2["incr_plus_go_med_lic"] - 1)) == 25, R2["incr_plus_go_med_lic"])
P.v("0.047", R2["incr_plus_go_slope"])
P.v("0.005", R2["incr_plus_go_se"])
P.v("161", R2["incr_plus_go_n"])
P.v("11.99", us2["chatgpt_plus"] - us2["chatgpt_go"], note="U.S. increment: $19.99 - $8.00")
P.v("0.010", R2["incrusd_plus_go_slope"])
P.v("0.007", R2["incrusd_plus_go_se"])
P.v("163", R2["incrusd_plus_go_n"])
P.wpin("two", "the two normalisations (structural)")
P.cond("the difference between the two normalisations is the schedule's own slope (within 0.005)",
       abs((R2["incrusd_plus_go_slope"] - R2["incr_plus_go_slope"]) - R2["default_slope"]) < 0.005, R2["incrusd_plus_go_slope"] - R2["incr_plus_go_slope"])
P.v("0.059", R2["incr_caiplus_lite_slope"])
P.v("0.012", R2["incr_caiplus_lite_se"])
P.w("two", len({W12.loc["pro200_plus", "high"], W12.loc["pro200_plus", "low"]}), note="'two frontier tiers': the two plans of the Pro 200 over Plus increment (W12_increment.csv)")
P.cond("Pro 200 and Plus are frontier tiers of the stack, and neither AI Pro nor AI Plus is localised (median LMIC deviation zero, Table 5)",
       STACK_GROUP["chatgpt_pro200"] == STACK_GROUP["chatgpt_plus"] == "frontier" and R2["gemini_pro_med_lmic_dev"] == 0 == R2["gemini_plus_med_lmic_dev"])
P.cond("the increments called flat are flat relative to the schedule: |slope| < 0.02 and within 2 s.e. of zero for Pro 200 over Plus and AI Pro over AI Plus",
       all(abs(R2[f"incr_{k}_slope"]) < 0.02 and abs(R2[f"incr_{k}_slope"]) < 2 * R2[f"incr_{k}_se"] for k in INCR_FRONT), max(abs(R2[f"incr_{k}_slope"]) for k in INCR_FRONT))
P.pin("365", why="product name Microsoft 365 Premium")
P.cond("'whose lower plan is moderately localised': Microsoft 365 Personal's median LMIC deviation from the schedule is negative but above -0.25 (-15%)",
       -0.25 < R2["m365_personal_med_lmic_dev"] < 0, R2["m365_personal_med_lmic_pct"])
P.v("15", 100 * (R2["incr_m365prem_pers_med_lmic"] - 1), note="median ratio of the Premium-Personal dollar gap to the schedule gap in lower-middle-income storefronts (1.15; low-income 1.15 as well)")
P.cond("the low-income median of the Microsoft increment ratio is also 15% wider", round(100 * (R2["incr_m365prem_pers_med_lic"] - 1)) == 15, R2["incr_m365prem_pers_med_lic"])
P.v("0.014", R2["incr_m365prem_pers_slope"], label="365 Premium over Personal, slope (negative)")
P.v("0.008", R2["incr_m365prem_pers_se"])
P.cond("Table 7 has these five pairs", set(INCR_PAIRS) == set(INCR_FRONT) | {"plus_go", "caiplus_lite", "m365prem_pers"}, len(INCR_PAIRS))
P.notation()

P = S("\\item \\emph{Notes:} Left: OLS of $\\ln[(p_{H,c}-p_{L,c})/(P^D_{H,c}-P^D_{L,c})]$")
P.notation()

# ================================================================================================ 5.5 affordability
N_QUINT = len([c for c in panel.columns if re.fullmatch(r"q\d_share", c)])
QSHARE = 100 / N_QUINT
hh_uplift = {k: 100 * (R["aabhh_p20_" + k] / R["aab_p20_" + k] - 1) for k in ("HIC", "UMIC", "LMIC", "LIC")}
POL_SRC = (ROOT / "extensions" / "policy_counterfactuals.py").read_text()
COVERED = grab(POL_SRC, r'd\["sub_cost_gni"\] = ([0-9.]+) \* \(d.pop1564', "covered share of the working-age population")
P = S("With frontier prices at the U.S.-anchored level everywhere, burdens are set by income.")
P.v("20", STD_PRICE, label="Figure 5 shows the $20 plan")
P.v("20", STD_PRICE, label="At a uniform $20")
P.v("0.65", R["aab_p20_HIC"])
P.v("3.09", R["aab_p20_UMIC"])
P.v("8.73", R["aab_p20_LMIC"])
P.v("28.9", R["aab_p20_LIC"])
P.v("45", R["ratio_aab20_LIC_HIC"], note="median burden of the low-income group over that of the high-income group")
P.v("0.75", R["laab_chatgpt_plus_HIC"], note="tax-inclusive local first-wave price of ChatGPT Plus, median burden")
P.v("3.27", R["laab_chatgpt_plus_UMIC"])
P.v("8.89", R["laab_chatgpt_plus_LMIC"])
P.v("28.9", R["laab_chatgpt_plus_LIC"])
P.v("20", STD_PRICE, label="the $20 tier meets the benchmark")
P.v("2", BENCH, label="2% benchmark")
P.cond("the $20 tier meets the benchmark in every high-income economy, in no lower-middle- or low-income economy", R["share_meets2pct_p20_HIC"] == 1.0 and R["share_meets2pct_p20_LMIC"] == 0.0 == R["share_meets2pct_p20_LIC"])
P.v("22", 100 * R["share_meets2pct_p20_UMIC"])
P.v("113", R["n_countries_aab20_gt2"])
P.v("201", R["n_econ_gni"])
P.v("60", 100 * R["share_wapop_aab20_gt2"])
P.v("0.40", R["aabppp_p20_HIC"])
P.v("1.20", R["aabppp_p20_UMIC"])
P.v("3.38", R["aabppp_p20_LMIC"])
P.v("10.7", R["aabppp_p20_LIC"])
P.w("five", round(R["aabppp_p20_LIC"] / BENCH), note="PPP-indexed low-income burden over the 2% benchmark, rounded (5.3)")
P.w("poorest fifth", 1 / N_QUINT, note="one of the five survey quintiles")
P.v("20", STD_PRICE, label="$20 plan for the poorest fifth")
P.v("1.6", R["aab20_q1_HIC"])
P.v("33", R["aab20_q1_LMIC"])
P.v("73", R["aab20_q1_LIC"])
P.w("richest fifth", 1 / N_QUINT)
P.v("98", 100 * R["share_top20_gt2_LMIC"])
P.cond("the richest fifth fails the benchmark in every low-income economy with survey data", R["share_top20_gt2_LIC"] == 1.0)
_laab_lmic = {k[5:-5]: v for k, v in R.items() if k.startswith("laab_") and k.endswith("_LMIC") and k != "laab_cheapest_LMIC"}     # median LMIC burden at the local price, by first-wave plan
P.lt("3", max(R["laab_chatgpt_go_LMIC"], R["laab_gemini_plus_LMIC"]), note="the 3% threshold of the sentence; the larger of the two entry-tier burdens in the median lower-middle-income economy (Go 2.58, AI Plus 2.15)", label="entry tiers below 3%")
P.cond("'Only the entry tiers fall below 3%': every other first-wave plan's median LMIC burden at the local price is above 3% (Appendix Table E.4, laab_<plan>_LMIC)",
       all(v > 3 for k, v in _laab_lmic.items() if k not in ("chatgpt_go", "gemini_plus")) and set(_laab_lmic) >= {"chatgpt_plus", "claude_pro", "gemini_pro", "gemini_ultra"}, min(v for k, v in _laab_lmic.items() if k not in ("chatgpt_go", "gemini_plus")))
P.v("2.6", R["laab_chatgpt_go_LMIC"])
P.cond("ChatGPT Go is the localised entry tier and Google AI Plus is not (median LMIC deviation from the schedule: Go -0.47, AI Plus 0)", R2["chatgpt_go_med_lmic_dev"] < -0.3 and R2["gemini_plus_med_lmic_dev"] == 0, R2["chatgpt_go_med_lmic_dev"])
P.v("4.99", us1["gemini_plus"], note="U.S. App Store price of Google AI Plus")
P.v("2.1", R["laab_gemini_plus_LMIC"], note="Google AI Plus at its local price, median burden in the lower-middle-income group: 2.146, printed to one decimal")
P.v("7.2", R["laab_chatgpt_go_LIC"], note="'both cost 7.2%': Go in the median low-income economy (7.214)")
P.cond("Google AI Plus also costs 7.2% in the median low-income economy (same $4.99 median price)", rnd(R["laab_gemini_plus_LIC"], 1) == rnd(R["laab_chatgpt_go_LIC"], 1) == Decimal("7.2"), R["laab_gemini_plus_LIC"])
P.v("20", STD_PRICE, label="bringing the $20 tier to the benchmark")
P.v("35", pol.loc["Upper-middle income", "sub_rate"])
P.v("77", pol.loc["Lower-middle income", "sub_rate"])
P.v("93", pol.loc["Low income", "sub_rate"])
P.w("three", len(GROUPS) - 1, note="the three poorer income groups")
P.v("84", pol.loc["Upper-middle income", "sub_usd"])
P.v("185", pol.loc["Lower-middle income", "sub_usd"])
P.v("223", pol.loc["Low income", "sub_usd"])
P.v("0.08", pol.loc["Upper-middle income", "sub_cost"])
P.v("0.43", pol.loc["Lower-middle income", "sub_cost"])
P.v("1.55", pol.loc["Low income", "sub_cost"])
P.w("one tenth", COVERED, note="share of the working-age population covered (extensions/policy_counterfactuals.py)")
P.v("0.143", POLJ["beta_go"], note="entry-tier exponent of the policy counterfactual (extensions/policy_counterfactuals.py reads loc_chatgpt_go_b of results.json: the first-wave slope, 0.1435; the second-wave slope is 0.1430)")
P.v("0.033", R2["default_slope"], label="which includes the schedule's 0.033")
P.v("20", STD_PRICE, label="localising the $20 tier")
P.v("14.8", POLJ["entry_LIC"])
P.v("0.110", POLJ["beta_go_dev"], note="deviation slope of ChatGPT Go used by the entry-deviation schedule (= chatgpt_go_dev_slope)")
P.cond("the policy counterfactual's deviation exponent is the Go deviation slope of code/12", POLJ["beta_go_dev"] == R2["chatgpt_go_dev_slope"])
P.v("17.3", POLJ["entry_dev_LIC"])
P.v("2", BENCH, label="the 2% benchmark is a convention")
P.cond("subsidy rate = 100 max(0, 1 - y/12,000) at the group's median GNI per capita equals the shipped sub_rate",
       all(abs(100 * max(0, 1 - R["median_gni_" + SH[g]] / R["threshold_gni_for_2pct_p20"]) - pol.loc[g, "sub_rate"]) < 0.2 for g in GROUPS[1:]))

# -- Table 8 header and notes, Figure 5
S("Affordability of the \\$20 tier and of the localised entry tier by income group (medians)").v("20", STD_PRICE)
P = S(" & & \\multicolumn{6}{c}{\\$20 plan, annual price as \\% of}", "Subsidy (\\%) \\\\")
P.v("20", STD_PRICE, label="$20 plan (annual price)")
P.v("20", STD_PRICE, label="$20 plan (benchmark columns)")
P.v("2", BENCH, label="2% benchmark")
P.v("20", QSHARE, label="Poorest 20%")
P.v("20", QSHARE, label="Richest 20%")

P = S("\\item \\emph{Notes:} Medians across the economies of each group of $1200p/y\\times100$.")
P.v("1200", AAB_MONTHS * AAB_PCT, note="12 months x 100 in aab() of code/20_analysis.py")
P.v("100", AAB_PCT, note="percent factor of aab()")
P.v("20", STD_PRICE, label="the $20 columns")
P.v("20", STD_PRICE, label="a uniform $20 reference price")
_nostore_gni = sorted(c for c in redir1 if c in panel.set_index(panel.iso2.str.lower()).index and panel.set_index(panel.iso2.str.lower()).loc[c, "gni_atlas"] > 0)
P.v("31", len(_nostore_gni), note="economies with GNI per capita whose storefront code redirects to the U.S. store (45 redirected codes, of which %d have income data)" % len(_nostore_gni))
P.cond("the 45 redirected codes are the 'No store' economies of Appendix Table E.4 (store_none shares times group sizes)",
       round(sum(R[f"store_none_{g}"] * R[f"n_store_{g}"] for g in ("HIC", "UMIC", "LMIC", "LIC"))) == len(redir1), len(redir1))
P.v("2025", int(gni.gni_atlas_year.mode().iloc[0]))
P.v("182", R["n_econ_gni2025"])
P.v("2022", int(non25.min()))
P.v("2024", int(non25.max()))
P.v("19", R["n_econ_gni"] - R["n_econ_gni2025"])
P.v("62", R["nprice_chatgpt_plus_HIC"], label="Plus local: 62")
P.v("51", R["nprice_chatgpt_plus_UMIC"], label="Plus local: 51")
P.v("36", R["nprice_chatgpt_plus_LMIC"], label="Plus local: 36")
P.v("15", R["nprice_chatgpt_plus_LIC"], label="Plus local: 15")
P.w("fifth", 1 / N_QUINT, note="poorest and richest of the five survey quintiles")
P.v("20", QSHARE, label="survey share relative to 20%")
P.v("163", R["n_dist"])
P.v("62", R["nprice_chatgpt_go_HIC"], label="entry tier: 62")
P.v("51", R["nprice_chatgpt_go_UMIC"], label="entry tier: 51")
P.v("36", R["nprice_chatgpt_go_LMIC"], label="entry tier: 36")
P.v("15", R["nprice_chatgpt_go_LIC"], label="entry tier: 15")
P.v("20", STD_PRICE, label="Above: the $20 burden")
P.v("2", BENCH, label="exceeds 2%")
P.v("20", STD_PRICE, label="Subsidy: the $20 price")
P.v("100", AAB_PCT, label="subsidy formula: 100")
P.v("12,000", R["threshold_gni_for_2pct_p20"], note="income at which a $20 plan costs exactly 2% of GNI per capita")
P.notation()

P = S("Burden of a \\$20 plan across the income distribution.")
P.v("20", STD_PRICE, label="$20 plan")
P.v("20", STD_PRICE, label="$20/month plan")
P.v("20", QSHARE, label="relative to 20%")
P.v("2", BENCH, label="2% broadband benchmark")

# ================================================================================================ 6. the public usage indicators
A20 = (ROOT / "code" / "20_analysis.py").read_text()
N_BOOT = int(grab(A20, r"\bB = ([0-9]+); diffs = \[\]", "bootstrap replications"))
BOOT_LO, BOOT_HI = (float(x) for x in re.search(r"np\.percentile\(diffs, \[([0-9.]+), ([0-9.]+)\]\)", A20).groups())
D1T = pd.read_csv(ROOT / "output" / "tables" / "D1_two_margins_sample.csv", keep_default_na=False)
gdp_rep = pd.read_csv(ROOT / "data" / "raw" / "anthropic" / "anthropic_gdp_elasticity_replication.csv").set_index("release")
gap_loo = csv("gradient_gap_leave_one_out.csv")
xprov = csv("cross_provider_gradient_robustness.csv").set_index("specification")
N_AUI_WINDOWS = len(aui_n)
N_IND = len([k for k in ("tm_ms_b", "tm_aui_b") if k in R])                     # the two usage indicators of the two-margin analysis
SHARE_USE = float(np.median([R["ai_among_online_" + k] for k in ("UMIC", "LMIC", "LIC")]))          # share of the eligible who use AI in the three non-high-income groups
PI_STAR = brentq(lambda pi: bstar(SHARE_USE, pi) - R["loc_chatgpt_plus_b"], 0.5, 0.99999)             # beta* = observed standard-tier slope
ctrl_cols = [f"ms_c{k}" for k in (2, 3, 4, 5)]
g3 = [R[f"growth_pct_median_{k}"] for k in ("HIC", "UMIC", "LMIC")]

P = S("The model's demand side implies that, with a free tier in every market")
P.w("two", N_IND, note="Microsoft AI User Share and Anthropic AI Usage Index (keys tm_ms_b, tm_aui_b)")
f = P.sub("Any use is moderately income-graded:", "from the high- to the low-income group.")
f.v("0.370", R["ms_log_cs_b"])
f.v("0.021", R["ms_log_cs_se"])
f.cond("'unchanged by controls': the elasticity with controls (columns (2)-(5) of Appendix Table D.2) stays within 0.02 of 0.370",
       all(abs(R[f"{c}_b"] - R["ms_log_cs_b"]) < 0.02 for c in ctrl_cols), min(R[f"{c}_b"] for c in ctrl_cols))
f.wpin("quarter", "second quarter of 2026 = the last period of the Microsoft series (ms_q2_2026)")
f.v("2026", int(MS_COLS[-1][-4:]), label="second quarter of 2026")
f.cond("the last period of the Microsoft series is the second quarter (panel column ms_q2_2026)", MS_COLS[-1].startswith("ms_q2_"), 0)
f.v("32.3", R["ms_q2_2026_median_cs_HIC"])
f.v("18.8", R["ms_q2_2026_median_cs_UMIC"])
f.v("12.0", R["ms_q2_2026_median_cs_LMIC"])
f.v("7.6", R["ms_q2_2026_median_cs_LIC"])
f = P.sub("Per-capita activity on one frontier assistant is twice as income-graded:", "Appendix Table~\\ref{tab:twomargins}.")
f.w("twice", R["tm_ratio"], tol=0.1, note="ratio of the Claude to the any-use elasticity is 1.92")
f.v("96", R["n_two_margins"])
f.v("0.711", R["tm_aui_b"])
f.v("0.036", R["tm_aui_se"])
f.v("0.371", R["tm_ms_b"])
f.v("0.026", R["tm_ms_se"])
f.v("0.340", R["tm_diff_b"])
f.v("0.034", R["tm_diff_se"])
P.w("two", N_IND, note="the two indicators")
P.cond("the common sample contains as many low-income economies as the text says (one)", R["tm_n_LIC"] == WORDS[re.search(r"contains (\w+) low-income economy", P.text).group(1)], R["tm_n_LIC"])
P.v("20", STD_PRICE, label="the $20 tier's slope")
P.w("nine in ten", PI_STAR, tol=0.05, note="share of users who pay at which beta* falls to the observed standard-tier slope (Proposition A.1); see Appendix A")
P.notation()

# ================================================================================================ 7. discussion, 8. conclusion, declarations
sub_poor = [pol.loc[g] for g in GROUPS[1:]]                     # the three poorer income groups
P = S("The price evidence is consistent with the model's predictions:")
_four = P.text.split("Four explanations therefore remain side by side, and the evidence speaks to each differently. ", 1)[1].split(" The cross-section cannot separate these.")[0]
P.w("Four", len(re.findall(r"(?<!U\.S)\. ", _four + " ")), note="'Four explanations': the four sentences between 'Four explanations therefore remain side by side' and 'The cross-section cannot separate these' "
                                                           "(inference-cost share with an override cost; cross-border arbitrage; a uniform-dollar policy; segmented demand)")
P.v("19.99", us2["gemini_pro"], note="'the overrides to $19.99 in taxed dollar storefronts': the U.S. price of the $20 tiers that Google, Microsoft and OpenAI list in the taxed dollar storefronts (Appendix Table E.13)")
P.cond("overrides to the U.S. price exist in the taxed dollar storefronts (Google AI Pro in 15 of 16, Microsoft 365 Premium in 10, ChatGPT Plus in 5)",
       R2["taxabs_gemini_pro_at_us"] > 0 and R2["taxabs_m365_premium_at_us"] > 0 and R2["taxabs_chatgpt_plus_at_us"] > 0, R2["taxabs_gemini_pro_at_us"])
P.v("3", GO_GAP_LO, note="ChatGPT Go sustained $3-4 below its U.S. price (Section 3)")
P.v("4", GO_GAP_HI)
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (lower end)")
P.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (upper end)")
P.v("20", STD_PRICE, label="not the $20 tiers")
P.v("161", R2["chatgpt_go_n"], note="storefronts with income data in the ChatGPT Go deviation regression")
P.v("20.99", us2["youtube_premium"], note="U.S. App Store price of YouTube Premium (W1_wave2_plans.csv)")
P.v("19.99", us2["gemini_pro"], label="Google AI Pro at $19.99")
P.v("57", 100 * (1 - R2["rel_ytprem_aipro_lmic_med"]), note="YouTube Premium relative to Google AI Pro, median relative price 0.43 in LMIC storefronts (Table 3, rel_ytprem_aipro_lmic_med)")

P = S("Three implications follow for the debate on access to generative AI")
P.w("Three", len(re.findall(r"(?<![A-Za-z])(?:First|Second|Third), ", P.text)), note="First, Second and Third implication")
P.v("5", min(us1["gemini_plus"], us1["chatgpt_go"]), note="entry tiers: Google AI Plus $4.99")
P.v("8", max(us1["gemini_plus"], us1["chatgpt_go"]), note="entry tiers: ChatGPT Go $8.00")
P.cond("cheap tiers exist in most poorer markets: more than half of the lower-middle- and low-income storefronts list ChatGPT locally",
       R["store_local_chatgpt_LMIC"] > 0.5 and R["store_local_chatgpt_LIC"] > 0.5, R["store_local_chatgpt_LIC"])
P.lt("3", max(R["laab_chatgpt_go_LMIC"], R["laab_gemini_plus_LMIC"]), label="entry-tier burdens below 3% (Go 2.58, Google AI Plus 2.15)")
P.cond("'whose cheapness there comes from a low U.S. price point rather than from localisation': Google AI Plus has the lowest U.S. price of the first-wave plans and a median LMIC deviation of zero",
       us1["gemini_plus"] == min(us1[k] for k in us1.index if not k.endswith("_other")) and R2["gemini_plus_med_lmic_dev"] == 0, us1["gemini_plus"])
P.v("20", STD_PRICE, label="the $20 frontier tier")
P.v("29", R["aab_p20_LIC"])
P.gt("13", R["aab20_q5_LIC"], note="burden of the $20 plan at the mean resources of the richest fifth, low-income median (13.05%)")
P.w("richest fifth", 1 / N_QUINT)
P.v("20", STD_PRICE, label="applying the localisation to the $20 tier")
P.v("14.8", POLJ["entry_LIC"])
P.v("17.3", POLJ["entry_dev_LIC"])
P.w("seven", round(POLJ["entry_LIC"] / BENCH), note="14.8% over the 2% benchmark = 7.4")
P.w("nine", round(POLJ["entry_dev_LIC"] / BENCH), note="17.3% over the 2% benchmark = 8.6")
P.v("20", STD_PRICE, label="bringing the $20 tier to the benchmark")
P.v("84", min(r.sub_usd for r in sub_poor))
P.v("223", max(r.sub_usd for r in sub_poor))
P.w("three", len(sub_poor), note="the three poorer income groups")
P.v("0.08", min(r.sub_cost for r in sub_poor))
P.v("1.55", max(r.sub_cost for r in sub_poor), note="largest subsidy cost of the three poorer groups, low income 1.5499% of GNI (policy_counterfactuals_groups.csv sub_cost), as printed in Section 5.5")
P.w("a tenth", COVERED)
P.w("half", R["decomp_share_connect"], tol=0.02, note="49% of the use gradient coincides with the connectivity gradient")

P = S("The audit observes listed prices in one distribution channel on two days 19 days apart")
P.w("two", N_WAVES, note="audit days")
P.v("19", R2["days_between_waves"])
P.v("8", us2["chatgpt_go"], note="the AI vendors' $8 price point")
P.v("20", STD_PRICE, label="$20 price point")
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 price points (lower end)")
P.v("500", max(us2[k] for k in HIGH500), label="$100-500 price points (upper end)")
P.w("six", len(WEAK6), note="lower-income storefronts in which the schedule is weak (upper block of Appendix Table E.12)")

P = S("Generative-AI assistants are priced as a global product with a local entry ramp.")
P.w("Two", N_WAVES, note="audits")
P.v("20", STD_PRICE)
P.v("100", min(us2[k] for k in HIGH500))
P.v("500", max(us2[k] for k in HIGH500))
P.v("0.016", min(R2[k + "_dev_slope"] for k in FRONT13), note="smallest deviation slope of the 13 frontier tiers (ChatGPT Pro 500, negative), as in the introduction and Section 5.3")
P.v("0.004", max(R2[k + "_dev_slope"] for k in FRONT13), note="largest deviation slope (ChatGPT Plus)")
P.v("38", -R2["chatgpt_go_med_lmic_pct"])
P.w("two and a half", PG["US"], tol=0.01, note="Plus-to-Go price ratio in the United States: 2.49875")
P.w("four times", PG["LIC"], tol=0.01, note="Plus-to-Go ratio in the median low-income storefront: 4.006")

P = S("A versioning model in which inference cost leaves little profit at stake")
P.v("0.65", R["aab_p20_HIC"])
P.v("29", R["aab_p20_LIC"])

for _p in ([S("\\paragraph{Declaration of generative AI")] if ANON_COPY else          # the anonymised copy keeps one branch of the \ifanon switch
           [S("\\ifanon\n\\paragraph{Declaration of generative AI", "full responsibility for the content of the publication."),
            S("\\else\n\\paragraph{Declaration of generative AI", "full responsibility for the content of the publication.")]):
    _p.wpin("two", "earlier versions of the paper on which an AI review tool gave feedback (declaration)")
if not ANON_COPY:          # the archive sentence is in the identified manuscript only; the anonymised package has no archive record
    zen = json.load(open(ROOT / "extensions" / "zenodo_record.json"))
    P = S("\\paragraph{Data availability.} All data are publicly available. The replication package (raw extracts, page archive fingerprints, code and outputs) is archived")
    P.pin(VERSION, why="version of the replication package that accompanies this manuscript (the version of the paper)")
    P.wpin("two", "the two page archives deposited with the record of version 3.1 (structural)")
    P.pin("2.1", "2.0", why="version labels of earlier replication packages in the record (the versions of the paper)")
    P.v("1.8", float(zen["metadata"]["version"]), note="version of the first archive deposit (extensions/zenodo_record.json)")

# ================================================================================================ Appendix A: the model
TM_SRC = (ROOT / "checks" / "verify_tier_model.py").read_text()
SIM = (PU / "sim_output.txt").read_text()                                                   # output of checks/sim_check.py
zgrid = np.linspace(-8, 8, 4001)
lam_prime_sup = float(np.max(hazard(zgrid) * (hazard(zgrid) - zgrid)))                                    # sup of lambda' on a grid: < 1


def sim_block(s, lL, lH):
    """the block of sim_output.txt for the calibration (s, cost share of the entry price, cost share of the frontier increment)"""
    a = SIM.index(f"calibration s={s}, cost share of entry price lL={lL}, of frontier increment lH={lH}")
    b = SIM.find("\n-- ", a + 10)
    return SIM[a:b if b > 0 else len(SIM)]


def sim_row(block, y):
    """the row of the income grid (unconstrained pL*, dH*, pH*, ratio; pinned pLo, ...; gains gL, gH, ratio)"""
    m = re.search(r"^\s*%s \|\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\|\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\|\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+|nan)" % re.escape(y), block, re.M)
    return [float(x) for x in m.groups()]


SIMB = sim_block("1.0", "0.25", "0.5")                                                      # the calibration of the text: s = 1, cost shares 1/4 and 1/2
SIM_Y02 = sim_row(SIMB, "0.20")
SIM_Y01 = sim_row(SIMB, "0.10")
SIM_EL = re.search(r"at y=0\.2: beta_L=([\d.]+), beta_dH=([\d.]+), beta_H\(level\)=([\d.]+)", SIMB)
SIM_LH = {float(m.group(1)): float(m.group(2)) for m in re.finditer(r"lH=([\d.]+) \(convex costs True\): y=0\.5: ratio [\d.]+, [^;]*; y=0\.2: ratio ([\d.]+)", SIM)}   # ratio gH/gL at y = 0.2 by frontier cost share
_tf = mult.set_index("storefront").tax_factor

P = S("\\paragraph{Conventions.} Storefronts (markets) are indexed by")
P.cond("the tax factor (multiplier / exchange rate) is one in the median storefront (data/processed/wave2_default_multiplier.csv, 164 storefronts)", abs(_tf.median() - 1) < 1e-9, float(_tf.median()))
P.v("0.98", _tf.quantile(0.05), note="5th percentile of the tax factor (pandas default interpolation)")
P.v("1.29", _tf.quantile(0.95), note="95th percentile")
P.w("nine tenths", 0.9, note="the 5th-95th percentile band holds nine tenths of the storefronts with a multiplier")
P.v("0.46", _tf.min(), note="smallest tax factor")
P.cond("the extremes are Egypt (minimum) and Colombia (maximum)", _tf.idxmin() == "eg" and _tf.idxmax() == "co", float(_tf.max()))
P.v("1.57", _tf.max(), note="largest tax factor")
P.v("0.033", R2["default_slope"])
P.notation()
S("\\subsection{Demand: four options and nested thresholds}").w("four", N_OPT, note="non-use, free, entry and frontier tier")
S("Consider a connected individual in market $c$ choosing among non-use").notation()
P = S("The service levels are theoretical objects")
P.w("three", N_THR, note="adjacent pairwise comparisons give the thresholds tau/q_F, p_L/(q_L-q_F), (p_H-p_L)/(q_H-q_L)")
P.notation()
P = S("the thresholds are nested and each option is chosen on an interval of valuations:")
P.w("four", N_OPT, note="the upper envelope of four lines: the utilities of the four options")
P.w("three", N_OPT - 1, note="menu without the entry tier: non-use, free and frontier tier")
P.notation()
S("Let $\\kappa_c$ be the population share with the connectivity").notation()
P = S("If participation costs vary as $\\tau_c\\propto y_c^\\lambda$")
P.w("three", len(set(re.findall(r"\\varepsilon_([A-Z])=", TEX[TEX.index("\\varepsilon_D=\\varepsilon_\\kappa"):TEX.index("\\label{eq:income_gradients}")]))),
    note="the three gradients of equation (A.5): epsilon_D, epsilon_P, epsilon_H")
P.notation()
S("Within the strict nested-threshold regime, define $h(z)=\\phi(z)/\\Phi(z)$").notation()
S("\\varepsilon_D=\\varepsilon_\\kappa+\\frac{h(z_{D,c})}{s}", "\\label{eq:income_gradients}").notation()
S("Uniform pricing of every tier ($\\beta_L=\\beta_H=0$) gives").notation()
P = S("Differentiating the logarithms of equation")
P.w("three", len(set(re.findall(r"\\varepsilon_([A-Z])=", TEX[TEX.index("\\varepsilon_D=\\varepsilon_\\kappa"):TEX.index("\\label{eq:income_gradients}")]))),
    note="orders the three gradients")
P.notation()

P = S("The threshold $\\beta^*$ depends on how far the two margins sit in the tail of the valuation distribution.")
P.w("two", len(set(re.findall(r"h\(z_\{([A-Z]),c\}\)", TEX[TEX.index("\\beta^*\\equiv1-h(z_{D,c})/h(z_{L,c})"):TEX.index("\\beta^*\\equiv1-h(z_{D,c})/h(z_{L,c})") + 60]))),
    note="margins whose tail positions enter beta* = 1 - h(z_D)/h(z_L): use and payment")
pay_a = int(re.search(r"and (\d+)\\% of users pay", P.text).group(1)) / 100
pay_c = int(re.search(r"when (\d+)\\% pay", P.text).group(1)) / 100
share_text = int(re.search(r"when (\d+)\\% of the eligible use AI", P.text).group(1)) / 100
P.v("23", 100 * SHARE_USE, note="share of the eligible who use AI: ratio of AI users to internet users in the non-high-income groups (23.0%)")
P.pin("10", why="scenario: share of users who pay")
P.v("0.44", bstar(share_text, pay_a), note="beta* = 1 - h(z_D)/h(z_L) with Phi(z_D) = 0.23 and Phi(z_L) = 0.10 x 0.23")
P.w("a quarter", 0.25, note="scenario: a quarter of users pay")
P.v("0.34", bstar(share_text, 0.25))
P.pin("1", why="scenario: share of users who pay")
P.v("0.58", bstar(share_text, pay_c))
P.cond("checks/results/sim_output.txt reports the same beta* values (0.4427, 0.3411, 0.5781)",
       all(abs(float(re.search(r"beta\* with 23%% using and %d%% of users paying = ([\d.]+)" % q, SIM).group(1)) - bstar(share_text, q / 100)) < 5e-4 for q in (10, 25, 1)))
P.v("20", STD_PRICE, label="the $20 tier")
P.v("0.026", R2["claude_pro_usd_slope"], note="Claude Pro dollar slope (0.026 in both waves)")
P.v("0.04", R["loc_chatgpt_plus_b"], note="first-wave ChatGPT Plus income slope (0.039)")
P.w("nine in ten", PI_STAR, tol=0.05, note="paid share of users at which beta* equals the observed Plus slope: 0.91 (sim_output.txt: 0.9085)")
P.cond("sim_output.txt gives the same paid share (0.9085) at which beta* = 0.04", abs(float(re.search(r"paying share of users is ([\d.]+)", SIM).group(1)) - PI_STAR) < 0.01, PI_STAR)
P.notation()

S("\\paragraph{Bridge to the activity index.}").notation()
S("\\varepsilon_m=\\theta_c(\\varepsilon_P-\\varepsilon_D),\\qquad \\theta_c\\equiv", "\\label{eq:bridge}").notation()
P = S("In the nested regime the vendor's profit is the sum of its profits on two price increments")
P.w("two", N_OPT - 2, note="the two paid increments")
P.notation()
S("Suppose that $\\ln\\tilde v$ has a differentiable, strictly increasing hazard rate").notation()
S("\\item The profit $(\\Delta p-\\Delta c)[1-G(x)]$ is strictly quasi-concave").notation()
S("\\beta\\equiv\\frac{\\partial\\ln\\Delta p^*}{\\partial\\ln y_c}=\\frac{\\xi}{\\xi+\\ell}=1-\\ell\\rho", "\\label{eq:beta_supply_app}").notation()
P = S("where $\\rho$ is the rate at which the optimal increment passes through its marginal cost")
P.v("1", beta_ln(0.0, 1.0), note="beta(L = 0) = 1 (equation A.8)", label="beta = 1 when the cost increment is zero")
P.lt("1", beta_ln(0.25, 1.0), note="beta(L = 0.25) < 1 (equation A.8)", label="beta < 1 when the cost increment is positive")
P.notation()
S("\\item If tier-$k$ valuations scale as $v=y_c^{\\sigma_k}\\tilde v$").notation()
S("\\item For lognormal valuations, $\\ln\\tilde v\\sim N(m,s^2)$, the conditions of (i) and (ii) hold").notation()
S("\\beta=\\frac{z^*+h(z^*)}{z^*+2h(z^*)-s},", "\\label{eq:beta_lognormal}").notation()
P = S("which equals one at $\\ell=0$, decreases strictly in $\\ell$ and tends to zero as $\\ell\\to1$.")
P.notation()
# the proof of Proposition A.2: single digits in in-line and display mathematics
for _snip in ["(i) Write $\\Delta p=\\Delta q\\,y_cx$ and the profit as", " \\frac{d\\ln\\varpi(x)}{dx}=\\frac{1-(1-\\hat c/x)\\,\\eta(x)}{x-\\hat c}.",
              "The numerator is strictly decreasing in $x$", " \\beta=1+\\frac{\\partial\\ln x^*}{\\partial\\ln y_c}", "(ii) Along the optimum,",
              "(iii) With $v=y_c^{\\sigma_k}\\tilde v$ the normalised increment", "(iv) For $\\ln\\tilde v\\sim N(m,s^2)$, $1-G(x)=\\Phi(z)$",
              " \\xi=\\frac{d\\Lambda}{d\\ln x}=\\frac{s\\,h'(z)}{h(z)^2}", "where $1+z[z+h(z)]>0$ is immediate for $z\\ge0$"]:
    S(_snip).notation()
P = S("For $s=1$ the elasticity is 0.63 at a cost share of one quarter")
s_a = float(re.search(r"For \$s=([0-9.]+)\$", P.text).group(1))
s_b = float(re.search(r"for \$s=([0-9.]+)\$", P.text).group(1))
P.pin("1", why="dispersion s = 1 of the illustration (input of the recomputation)")
for (word, L_), pr in zip((("one quarter", 0.25), ("one half", 0.5), ("four fifths", 0.8)), ("0.63", "0.30", "0.05")):
    P.w(word, L_, note="marginal-cost share L (input of the recomputation)")
    P.v(pr, beta_ln(L_, s_a), note=f"beta(L = {L_}, s = {s_a}) from (A.8)")
P.pin("0.7", why="dispersion s = 0.7 of the illustration (input of the recomputation)")
for pr, L_ in zip(("0.76", "0.44", "0.09"), (0.25, 0.5, 0.8)):
    P.v(pr, beta_ln(L_, s_b), note=f"beta(L = {L_}, s = {s_b}) from (A.8)")
P.cond("beta(L, s) is decreasing in L on a grid of 100 cost shares, for s = 0.3, 0.7, 1, 1.5 and 2",
       all(np.all(np.diff([beta_ln(L_, s_) for L_ in np.linspace(0, 0.99, 100)]) < 0) for s_ in (0.3, 0.7, 1.0, 1.5, 2.0)))
P.cond("sim_output.txt quotes the same six values", all(abs(float(x) - beta_ln(L_, s_)) < 5e-3 for s_, line in ((1.0, "s=1.0"), (0.7, "s=0.7"))
                                                        for x, L_ in zip(re.search(line + r": ([\d.]+), ([\d.]+), ([\d.]+)", SIM).groups(), (0.25, 0.5, 0.8))))

# -- the menu
S("The vendor earns $-c_F$ on a free user").notation()
S("\\Pi_c=M_c\\kappa_c\\Big[-c_F\\Phi(z_{D,c})", "\\label{eq:menu_profit}").notation()
P = S("with $\\Delta p_{H,c}=p_{H,c}-p_{L,c}$, $\\Delta c_L=c_L-c_F$ and $\\Delta c_H=c_H-c_L$.")
P.w("two", N_OPT - 2, note="the sum of two increment problems")
P.notation()
S("Maintain the assumptions of Proposition~\\ref{prop:supply}(i)--(ii).").notation()
P = S("\\item The optimal menu is nested in every market and consists of the two optimal increments")
P.w("two", N_OPT - 2, note="the two optimal increments")
P.notation()
S("\\item For any entry price in the nested region, the frontier price that maximises").notation()
S(" \\beta_H=\\frac{p^*_{L,c}}{p^*_{H,c}}\\,\\beta_L", "\\label{eq:beta_level}").notation()
P = S("where $\\beta_L$ and $\\beta_{\\Delta H}$ are the elasticities")
P.w("two", N_OPT - 2, note="the two increments")
P.notation()
S("\\item $\\beta_L>\\beta_{\\Delta H}>0$.").notation()
S("\\item If the listed frontier price does not vary with income").notation()
S("\\item If the frontier price is held at a level").notation()
for _snip in ["Write \\eqref{eq:menu_profit} as $M_c\\kappa_c[-c_F\\Phi(z_{D,c})+A_c(p_{L,c})+B_c(\\Delta p_{H,c})]$",
              "(i) Both increments face the same distribution of", "(ii) Given $p_{L,c}$, $\\Pi_c$ depends on", "(iii) By Proposition~\\ref{prop:supply}(ii), $\\beta$ is the same",
              "(v) Let $p_L<p^*_{L,c}$."]:
    S(_snip).notation()

P = S("In a lognormal example calibrated so that the optimum in the reference market is")
P.v("8", us1["chatgpt_go"], note="entry price of the calibration: the U.S. price of ChatGPT Go (sim_check.py)")
P.v("20", STD_PRICE, note="frontier price of the calibration")
P.cond("sim_output.txt calibrates the reference market at pL* = 8 and pH* = 20", sim_row(SIMB, "1.00")[0] == 8.0 and sim_row(SIMB, "1.00")[2] == 20.0)
P.pin("1", why="dispersion s = 1 of the calibration (sim_check.py)")
_cal = re.search(r"calibration s=([\d.]+), cost share of entry price lL=([\d.]+), of frontier increment lH=([\d.]+)", SIMB)
P.w("one quarter", float(_cal.group(2)), note="cost share of the entry price in the calibration (lL in sim_output.txt)")
P.w("one half", float(_cal.group(3)), note="cost share of the frontier increment (lH)")
P.w("fifth", float(re.search(r"^\s*(0\.20) \|", SIMB, re.M).group(1)), note="a market with a fifth of the reference income: the row y = 0.20 of the income grid of sim_output.txt")
P.v("12.7", SIM_Y02[2], note="unconstrained frontier price pH* at y = 0.20 (sim_output.txt)")
P.v("37", 100 * (1 - SIM_Y02[2] / 20), note="100 (1 - 12.66 / 20)")
P.v("4.1", 8 - SIM_Y02[0], note="8 - pL*(0.2) = 8 - 3.88: the lower entry price passed through")
P.v("3.2", 12 - SIM_Y02[1], note="12 - dH*(0.2) = 12 - 8.78: the lower optimal increment")
P.v("0.28", float(SIM_EL.group(1)), note="beta_L at y = 0.2 (sim_output.txt)")
P.v("0.12", float(SIM_EL.group(2)), note="beta_dH at y = 0.2")
P.v("0.17", float(SIM_EL.group(3)), note="beta_H (level) at y = 0.2")

# -- the constraints
P = S("Proposition~\\ref{prop:menu}(iv) shows that a localised entry tier combined with a frontier tier")
P.wpin("two", "the two candidate constraints: the override cost and arbitrage (structural)")
S("\\emph{The override cost.} The listed price is the default unless the vendor overrides it").notation()
S("\\item $G_{L,c}$ and $G_{H,c}$ are proportional to the eligible population").notation()
S("\\item A consumer who buys tier $k$ at home buys the same tier in $c$ if and only if").notation()
S("(i) By \\eqref{eq:menu_profit}, $\\Pi_c/(M_c\\kappa_c)$ depends on the storefront only through").w("four", len(re.search(r"compares four options \((.*?)\)", TEX).group(1).split(", ")), note="the four options the vendor compares, enumerated in the sentence: no override, entry tier only, frontier tier only, both")
S("(i) By \\eqref{eq:menu_profit}, $\\Pi_c/(M_c\\kappa_c)$ depends on the storefront only through").notation()
P = S("Proposition~\\ref{prop:constraints} assigns the two candidates different roles.")
P.wpin("two", "the two candidates (structural)")
P.v("3", GO_GAP_LO, note="ChatGPT Go listed $3-4 below its U.S. price")
P.v("4", GO_GAP_HI)
P.v("20", STD_PRICE, label="a $20 tier")
P.v("15", 100 * _g_lo / STD_PRICE, note="$3 on $20")
P.v("20", 100 * _g_hi / STD_PRICE, note="$4 on $20", label="15-20%")
P.v("0.6", 100 * _g_lo / max(us2[k] for k in HIGH500), note="$3 on $500 (0.6%)")
P.v("4", 100 * _g_hi / min(us2[k] for k in HIGH500), note="$4 on $100")
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers")
P.v("500", max(us2[k] for k in HIGH500))
P.v("20", STD_PRICE, label="not the $20 tiers")
P.wpin("quarter", "'by up to about a quarter': the tax factor's excess over one in the taxed storefronts (see the unresolved entry on 1.27 above and the report)")
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (footnote)")
P.v("500", max(us2[k] for k in HIGH500), label="$100-500 tiers (footnote, upper end)")
P.v("20", STD_PRICE, label="the override cost and the $20 tiers")
P.v("8", 100 * SIM_Y02[-1], note="gH/gL at y = 0.2 in the calibration (0.081)")
P.w("fifth", float(re.search(r"^\s*(0\.20) \|", SIMB, re.M).group(1)), note="a fifth of the reference income: the row y = 0.20 of the income grid of sim_output.txt")
P.v("3", 100 * SIM_Y01[-1], note="gH/gL at y = 0.1 (0.031)")
P.w("tenth", float(re.search(r"^\s*(0\.10) \|", SIMB, re.M).group(1)), note="a tenth of the reference income: the row y = 0.10")
P.w("fifth", float(re.search(r"y=(0\.2): ratio", SIM).group(1)), note="at a fifth of the reference income: the y = 0.2 entries of the cost-share lines of sim_output.txt")
P.v("2.6", SIM_LH[0.3], note="gH/gL at y = 0.2 for a frontier cost share of 0.3 (sim_output.txt)")
P.v("0.49", SIM_LH[0.4])
P.v("0.08", SIM_LH[0.5])
P.v("0.007", SIM_LH[0.6])
P.pin("0.3", "0.4", "0.5", "0.6", why="frontier-increment cost shares of the illustration (inputs of checks/sim_check.py)")
P.cond("the four cost shares named are those of sim_output.txt", set(SIM_LH) >= {0.3, 0.4, 0.5, 0.6})
P.notation()
S("The pass-through of Proposition~\\ref{prop:menu}(ii) rests on the marginal frontier subscriber's alternative").wpin("two", "the two tiers serving separate segments (structural)")
S("The pass-through of Proposition~\\ref{prop:menu}(ii) rests on the marginal frontier subscriber's alternative").notation()

# -- predictions and Table A.1
P = S("Table~\\ref{tab:regimes} collects the predictions of the model by the constraint that binds")
P.w("Three", len(re.findall(r"\((P[123])\)", P.text)), note="P1, P2 and P3, the predictions the paragraph confronts with listed prices")
P.v("0.047", R2["incr_plus_go_slope"])
P.v("0.005", R2["incr_plus_go_se"])
P.v("161", R2["incr_plus_go_n"])
P.v("25", 100 * (R2["incr_plus_go_med_lmic"] - 1), note="median ratio of the increment to the schedule increment in lower-middle-income storefronts (low-income 1.251 rounds to the same)")
P.v("0.010", R2["incrusd_plus_go_slope"], label="in dollars relative to the U.S. increment (negative)")
P.v("0.007", R2["incrusd_plus_go_se"])
P.v("0.033", R2["default_slope"], note="the schedule's own tax slope")
P.cond("'both normalisations reject that benchmark': the dollar-increment slope is below the schedule slope by more than two s.e., and the schedule-relative slope is negative by more than two s.e.",
       R2["incrusd_plus_go_slope"] + 2 * R2["incrusd_plus_go_se"] < R2["default_slope"] and R2["incr_plus_go_slope"] + 2 * R2["incr_plus_go_se"] < 0, R2["incrusd_plus_go_slope"])
P.v("0.059", R2["incr_caiplus_lite_slope"], note="Character.AI+ over Character.AI Lite (corrected from the stale -0.21 of the draft; see the report)")
P.v("0.012", R2["incr_caiplus_lite_se"])
P.notation()
S("Frontier deviation from the default & falls as income falls").notation()
S("Entry deviation & slope $\\beta_L\\in(0,1)$").notation()
P = S("Consistent with the audit & no (increment) & largely;")
P.cond("'largely; not the overrides to the U.S. price in taxed dollar storefronts': some frontier tiers are listed at the U.S. price in the taxed dollar storefronts (Appendix Table E.13)",
       R2["taxabs_gemini_pro_at_us"] + R2["taxabs_m365_premium_at_us"] + R2["taxabs_chatgpt_plus_at_us"] > 0, R2["taxabs_gemini_pro_at_us"])
P.v("100", min(us2[k] for k in HIGH500), label="$100-500 tiers (Table A.1)")
P.v("500", max(us2[k] for k in HIGH500))
_simF = {m.group(1) + "|" + m.group(2): (float(m.group(3)), float(m.group(4)), int(m.group(5)))
         for m in re.finditer(r"^(\w+) - (\w+): slope of ln\(increment / default increment\) on ln GNI = ([+-][\d.]+) \(HC1 ([\d.]+)\), N=(\d+)", SIM, re.M)}
P.cond("checks/results/sim_output.txt (section F, read-only replication data) reproduces the increment slopes of results_wave2.json for Plus over Go and Character.AI+ over Lite",
       abs(_simF["chatgpt_plus|chatgpt_go"][0] - R2["incr_plus_go_slope"]) < 5e-5 and _simF["chatgpt_plus|chatgpt_go"][2] == R2["incr_plus_go_n"]
       and abs(_simF["characterai_plus|characterai_lite"][0] - R2["incr_caiplus_lite_slope"]) < 5e-5 and abs(_simF["characterai_plus|characterai_lite"][1] - R2["incr_caiplus_lite_se"]) < 5e-5,
       _simF["characterai_plus|characterai_lite"][0])
P = S("\\item \\emph{Notes:} Deviations are $\\ln(p_{k,c}/P^D_{k,c})$")
P.v("0.004", R2["chatgpt_plus_dev_slope"])
P.v("0.110", R2["chatgpt_go_dev_slope"])
P.v("0.047", R2["incr_plus_go_slope"])
P.v("0.005", R2["incr_plus_go_se"])

P = S("For a service priced in dollars, the burden relative to income at market exchange rates")
P.v("12", AAB_MONTHS, label="12 p / y^PPP")
P.v("12", AAB_MONTHS, label="12 (p PLR) / y")
P.wpin("three", "definition of the World Bank Atlas method (three-year average of exchange rates)")
P.v("3.1", 100 * R["plr_vs_gdp_absdiff_median"])
P.v("90", [int(m.group(1)) for k in R for m in [re.fullmatch(r"plr_vs_gdp_absdiff_p(\d+)", k)] if m][0], note="percentile of the absolute difference (results.json key plr_vs_gdp_absdiff_p90)")
P.v("8.3", 100 * R["plr_vs_gdp_absdiff_p90"])
P.v("197", R["plr_vs_gdp_n"])
P.v("0.228", R["plr_b"])
P.v("0.224", R["plr_gdp_b"])
P.notation()
S("because $\\Pr(v\\ge T_{k,c})=1-\\Phi(-z_{k,c})=\\Phi(z_{k,c})$.").notation()
S("\\item A consumer who buys tier $k$ at home buys the same tier in $c$ if and only if").wpin("two", "the two storefronts of an arbitrage pair (structural)")
S("\\item If prices are free of arbitrage and the entry tier is listed").wpin("two", "the two storefronts of an arbitrage pair (structural)")

# ================================================================================================ Appendix B: data construction
import ast
import collections

# the shipped parsing functions of code/09_appstore_prices.py, applied to the raw wave-1 records
_ns = {"np": np, "re": re, "collections": collections}
for _node in ast.parse((ROOT / "code" / "09_appstore_prices.py").read_text()).body:
    if isinstance(_node, ast.FunctionDef) and _node.name in ("parse_price", "plan_of", "monthly"):
        exec(compile(ast.Module([_node], []), "09_appstore_prices.py", "exec"), _ns)
_rates = json.load(open(sorted((ROOT / "data" / "raw" / "fx").glob("er_api_usd_*.json"))[-1]))["rates"]
_cells = []
for _r in raw1:
    if _r.get("http_status") != 200 or not _r.get("iap"):
        continue
    _m = re.search(r"apps\.apple\.com/([a-z]{2})/", _r.get("final_url") or "")
    if not _m or _m.group(1) != _r["storefront"]:
        continue
    _by = collections.defaultdict(list)
    for _name, _ps in _r["iap"]:
        _pl = _ns["plan_of"](_r["app"], _name)
        if _pl:
            _by[_pl].append(_ns["parse_price"](_ps))
    for _pl, _vals in _by.items():
        _vals = [x for x in _vals if np.isfinite(x)]
        if _vals:
            _cells.append((_r["storefront"], _pl, _ns["monthly"](_vals)[0] / _rates[_r.get("currency")]))
_cells = pd.DataFrame(_cells, columns=["storefront", "plan", "usd"])
_cells["rel"] = _cells.usd / _cells.plan.map(_cells[_cells.storefront == "us"].set_index("plan").usd)
N_ANNUAL_ONLY = int((_cells.rel >= 5).sum())                                # cells where only an annual variant was listed
st_codes = collections.Counter()
for _r in raw1:
    _m = re.search(r"apps\.apple\.com/([a-z]{2})/", _r.get("final_url") or "")
    st_codes["notfound" if _r["http_status"] == 404 else "local" if (_r["http_status"] == 200 and _m and _m.group(1) == _r["storefront"])
             else "redirected" if _r["http_status"] == 200 else "error"] += 1
ann = csv("chatgpt_annual_filter_sensitivity.csv", PU)
nm = csv("chatgpt_name_matching_scope.csv", PU)
cutoffs = sorted(int(c) for c in ann.annual_filter_cutoff.unique())
bj = [x for _r in raw1 if _r["storefront"] == "bj" and _r["app"] == "gemini" for x in _r["iap"]]
amb = prices[prices.n_distinct_monthly > 1]
WAVE2_README = (ROOT / "data" / "raw" / "appstore_wave2" / "README.md").read_text()
WEB_README = (ROOT / "data" / "raw" / "web" / "README.md").read_text()
OS_SRC = (ROOT / "code" / "00_download_sources.sh").read_text()
AEI_FACTOR = float(re.search(r"uniformly scaled by ([0-9.]+)", DD).group(1))

P = S("\\paragraph{Replication package.} The package contains the raw extracts")
P.pin("507", "316", why="commit 507c316 of the Microsoft dataset (code/00_download_sources.sh pins the full hash 507c31611c...)")
P.cond("code/00_download_sources.sh downloads the Microsoft data at a commit that starts with 507c316", "ai-diffusion-report/507c316" in OS_SRC)

P = S("\\paragraph{App Store audit, wave 1.}")
P.dt("27 September 2026", d1)
P.v("6448311069", APPS["chatgpt"]["id"], note="App Store id of ChatGPT (apps_v3.json, code/02_scrape_appstore_prices.py)")
P.v("6473753684", APPS["claude"]["id"])
P.v("6477489729", APPS["gemini"]["id"])
P.w("two", next(iter({len(r["storefront"]) for r in raw1})), note="two-letter codes")
P.v("217", len(panel))
P.v("654", len(raw1), note="218 codes x 3 assistants")
P.v("500", st_codes["local"])
P.v("135", st_codes["redirected"])
P.v("19", st_codes["notfound"])
P.v("135", st_codes["redirected"], label="the 135 redirects")
P.v("45", len(redir1), note="codes that redirect to the U.S. store (135 requests / 3 assistants)")
P.v("19", st_codes["notfound"], label="19 pages 'not found'")
P.w("Four", N_ANNUAL_ONLY, note="storefront-plan cells with only an annual variant: relative price to the U.S. at least 5 (code/09_appstore_prices.py applied to the raw records)")
P.w("three", R["price_ambiguous_cells"], note="cells with two different candidate prices")
P.w("two", int(amb.n_distinct_monthly.max()), note="distinct candidate prices in the ambiguous cells (n_distinct_monthly)")
_gp = {sf: collections.Counter(i[1] for x in raw1 if x["storefront"] == sf and x["app"] == "gemini" for i in x["iap"] if i[0].startswith("Google AI Pro"))
       for sf in ("in", "tr")}
P.cond("Google AI Pro in India and Turkiye: five listings, four at the modal price and one at a lower price (raw records)",
       all(sorted(c.values()) == [1, 4] for c in _gp.values())
       and bool((amb[(amb.storefront.isin(["in", "tr"])) & (amb.plan == "gemini_pro")].price_local_min_candidate
                 < amb[(amb.storefront.isin(["in", "tr"])) & (amb.plan == "gemini_pro")].price_local).all()),
       int(amb[(amb.storefront == "in") & (amb.plan == "gemini_pro")].n_variants.iloc[0]))
P.w("five", int(amb[(amb.storefront == "in") & (amb.plan == "gemini_pro")].n_variants.iloc[0]), note="listings of Google AI Pro in India and Turkiye (n_variants of the price table)")
_bj_tb = collections.Counter(int(m.group(1)) for x in bj for m in [re.search(r"Google AI Pro \((\d+) TB\)", x[0])] if m)
_bj_other = sorted(set(_bj_tb) - {_bj_tb.most_common(1)[0][0]})
P.cond("Benin lists one Google AI Pro variant (in TB) alongside the standard (modal) plan", len(_bj_other) == 1, len(_bj_other))
P.v("10", _bj_other[0], note="storage tier of the Benin variant ('Google AI Pro (10 TB)'); the standard plan is the modal 5 TB listing")
P.cond("the three cells are Google AI Pro in India, Turkiye and Benin", set(zip(amb.storefront, amb.plan)) == {("in", "gemini_pro"), ("tr", "gemini_pro"), ("bj", "gemini_pro")})
P.v("0.0001", R["price_ambiguous_max_dbeta"], note="largest change of a slope when the lowest listed price is used")
P.cond("a single surviving candidate price in every ChatGPT Go, ChatGPT Plus and Claude Pro cell",
       (nm.n_surviving_candidates == 1).all() and (prices[prices.plan.isin(["chatgpt_go", "chatgpt_plus", "claude_pro"])].n_distinct_monthly == 1).all(),
       len(nm))
P.w("three", cutoffs[0], note="annual-price exclusion cutoffs of the sensitivity file: 3, 5 and 8 times the lowest listed price")
P.w("five", cutoffs[1])
P.w("eight", cutoffs[2])
P.cond("the cutoffs select the same listings (selected price identical across cutoffs in every cell) and 5 is the pipeline's cutoff",
       ann.groupby(["iso3", "plan"]).selected_price_local.nunique().max() == 1 and ANNUAL_CUT in cutoffs and ann.exact_match.all(), len(ann))
P.v("162", min(W1_BY_APP), note="first-wave samples by app, U.S. included")
P.v("165", max(W1_BY_APP))
P.cond("the first-wave samples (U.S. included) differ by one from the second-wave samples of the same plans (which exclude it): 164 vs 163 (ChatGPT), 162 vs 161 (Claude), 165 vs 164 (Google AI Pro)",
       R["loc_chatgpt_plus_n"] - int(W1.loc["chatgpt_plus", "n_all"]) == 1 and R["loc_claude_pro_n"] - int(W1.loc["claude_pro", "n_all"]) == 1
       and R["loc_gemini_pro_n"] - int(W1.loc["gemini_pro", "n_all"]) == 1)

P = S("\\paragraph{App Store audit, wave 2, and the page archive.}", "keeping the listing with more storefronts.")   # the paragraph spans the \ifanon block
P.dt("16 October 2026", d2)
P.v("34", R2["wave2_apps"])
P.v("218", n_codes)
P.v("7,412", R2["wave2_requests"])
P.v("429", max([r.get("http_status") for r in raw2 if r.get("http_status") == 429] or [0]), note="HTTP status of the retried rate-limit answers in the raw records")
P.w("three", N_CORE, note="full pages archived for the three assistants (apps of class ai_core)")
ARCH_FILES = int(re.search(r"\((\d+) MB\):\n([\d,]+) gzipped files for the ([\d,]+) pages with HTTP 200", WAVE2_README).group(2).replace(",", ""))
ARCH_PAGES = int(re.search(r"\((\d+) MB\):\n([\d,]+) gzipped files for the ([\d,]+) pages with HTTP 200", WAVE2_README).group(3).replace(",", ""))
ARCH_MB = int(re.search(r"\((\d+) MB\):\n([\d,]+) gzipped files for the ([\d,]+) pages with HTTP 200", WAVE2_README).group(1))
ARCH_FULL = int(re.search(r"the (\d+) full pages of ChatGPT, Claude and Gemini", WAVE2_README).group(1))
if not ANON_COPY:                                   # the identified branch of the \ifanon block names the archive record of version 3.1
    P.pin(VERSION, why="version of the archive record that holds the deposited page archive")
for _branch in range(1 if ANON_COPY else 2):        # both branches of the \ifanon block carry the same counts (the anonymised copy keeps one)
    P.v("12,860", ARCH_FILES, note="files of the deposited page archive (data/raw/appstore_wave2/README.md; snip, snip_default_panel and html entries)")
    P.v("12,225", ARCH_PAGES, note="pages with HTTP 200 covered by the archive (= 7,218 + 5,007, data/raw/appstore_wave2/README.md)")
    P.v("200", 200, note="HTTP status of a page that was returned")
    P.v("109", ARCH_MB, note="size of the deposited page archive (README)")
    P.v("635", ARCH_FULL, note="full pages of the three assistants in the archive (README); the hashes of all of them match the parsed records")
P.cond("the 12,225 pages are the 7,218 pages of the 34 apps plus the 5,007 pages of the default panel", ARCH_PAGES == R2["wave2_pages_200"] + R2["default_pages"], ARCH_PAGES)
P.v("20", MULT_ALLOW[1], note="former plan name ChatGPT Pro 20x")
P.w("five", ANNUAL_CUT, note="variants priced at five or more times the lowest are excluded (code/09b_wave2_items.py)")
P.w("ten", R2["wave2_list_max_items"], note="the product page lists at most ten purchases")
P.w("three", GUARD_K, note="the guard's multiple (GUARD_K of code/09b_wave2_items.py)")
P.w("three", GUARD_K, note="the same multiple of the U.S. price for single-variant listings without a multiplier")
P.v("151", R2["guard_flagged_cells"])
P.v("21,938", R2["guard_cells_considered"])
P.v("157", R2["guard_flagged_cells_all"], note="flagged cells before the income restriction")
P.v("14", R2["guard_flagged_items"])
_w6b = pd.read_csv(ROOT / "output" / "tables" / "W6b_annual_guard_cells.csv", keep_default_na=False, na_values=[""])
P.cond("W6b_annual_guard_cells.csv lists flagged cells of 14 items (151 with income data, 157 in all)",
       _w6b.groupby(["app", "name"]).ngroups == R2["guard_flagged_items"] and len(_w6b) == R2["guard_flagged_cells_all"]
       and int(_w6b.in_regressions.sum()) == R2["guard_flagged_cells"], len(_w6b))
P.v("129", int(guard_top.n_flagged.sum()), note="flagged cells of the five items with at least five flagged cells (36 + 36 + 35 + 16 + 6)")
P.pin("100", why="name of the item 'Gemini 100 GB plan'")
P.wpin("two", "two apps (structural)")
P.wpin("two", "two spellings (structural)")
P.w("five", R2["wave2_dedup_dropped_n"], note="items dropped by the de-duplication")
P.v("152", R2["wave2_item_slopes_n"])

P = S("\\paragraph{Estimated platform schedule.}")
P.v("30", R2["default_apps"])
P.w("three", MIN_ITEMS_POINT, note="items per price point (wave2_common.py: min_items = 3)")
P.w("half", MODE_SHARE, note="the mode must account for at least half of the items at the point")
P.v("1,551", R2["default_ladder_points"])
P.v("2,414", R2["default_ladder_entries"])
P.v("22", R2["default_ladder_tied_points"], note="two-way ties at exactly one half")
P.w("two", round(1 / MODE_SHARE), note="a tie at exactly one half is between 1 / 0.5 = 2 prices")
P.w("one half", MODE_SHARE)
P.v("2.99", POINT_MIN_USD)
P.w("three", MIN_POINTS_MULT, note="points per multiplier (wave2_common.py)")
P.v("164", R2["default_multiplier_storefronts"])
P.v("0.2", THR_CLEAN)
P.v("111", R2["default_clean_storefronts"])
P.v("108", R2["chatgpt_plus_clean_n"], note="clean storefronts with income data")
P.v("0.0325", min(R2[f"default_tie_{r}_slope"] for r in tie_untied))
P.v("0.0329", max(R2[f"default_tie_{r}_slope"] for r in tie_untied))
P.v("0.110", min(R2[f"default_tie_{r}_go_dev_slope"] for r in tie_untied))
P.v("0.111", max(R2[f"default_tie_{r}_go_dev_slope"] for r in tie_untied))
P.w("half", MODE_SHARE, note="the strict rule discards cells whose mode accounts for exactly half of the items")
P.v("0.027", R2["default_tie_strict_slope"])
P.v("0.110", R2["default_tie_strict_go_dev_slope"], label="Go slope under the strict rule")
_mt = mult.set_index("storefront").join(panel.assign(storefront=panel.iso2.str.lower()).set_index("storefront")[["region"]])
_eu = _mt[(_mt.region == "Europe & Central Asia") & (_mt.currency != "USD")]
P.cond("the tax factor is one in the median U.S.-dollar storefront", abs(_mt[_mt.currency == "USD"].tax_factor.median() - 1) < 1e-9, _mt[_mt.currency == "USD"].tax_factor.median())
_cn = panel.set_index(panel.iso2.str.lower()).country_wb
P.cond("the tax factor is above one in every non-USD storefront of Europe and Central Asia", bool((_eu.tax_factor > 1).all()), _eu.tax_factor.min())
P.v("34", len(_eu), note="storefronts of Europe and Central Asia not denominated in U.S. dollars (data/processed/wave2_default_multiplier.csv joined to country_panel.csv region)")
_in = _eu[(_eu.tax_factor.round(2) >= 1.19) & (_eu.tax_factor.round(2) <= 1.36)]
_out = _eu.drop(_in.index).sort_values("tax_factor")
P.v("31", len(_in), note="of them with a tax factor (multiplier / fx) in 1.19--1.36 after rounding to two decimals")
P.v("1.19", _in.tax_factor.min(), note="smallest tax factor inside the range (Czechia)")
P.v("1.36", _eu.tax_factor.max(), note="Norway; largest tax factor among the non-USD storefronts of Europe and Central Asia")
P.cond("the exceptions are Romania, Cyprus and Montenegro", sorted(_cn[c] for c in _out.index) == ["Cyprus", "Montenegro", "Romania"], len(_out))
P.v("1.05", _out.tax_factor.min(), note="Romania")
P.v("1.12", _out.tax_factor.max(), note="Cyprus and Montenegro (same EUR multiplier)")
P.w("six", R2["vint_fx_dates"], note="exchange-rate snapshots of the vintage test")
P.dt("March 2024", FX_DATES[0])
P.dt("October 2026", FX_DATES[-1])

_pools = collections.defaultdict(list)
_ms = pd.read_csv(ROOT / "data" / "raw" / "ms_repo" / "data" / "AI_Diffusion_Q22026_Update.csv", encoding="latin-1")
for _econ, _key in zip(_ms.Economy, _ms.iloc[:, 1:].astype(str).agg("|".join, axis=1)):
    _pools[_key].append(_econ)
_pools = [v for v in _pools.values() if len(v) > 1]
P = S("\\paragraph{Microsoft region-imputed economies.}")
_seg = re.search(r"Six pools with identical four-period series: (.*?)\. These 36", P.text).group(1).split("; ")
_sizes = []
for _s_ in _seg:
    _s_ = re.sub(r"^and ", "", _s_)
    _par = re.search(r"\((.*?)\)", _s_)
    _extra = re.search(r"\) and ([A-Z][A-Za-z ]+)$", _s_)
    _sizes.append(len(_par.group(1).split(", ")) + (1 if _extra else 0) if _par else len(re.split(r", | and ", _s_)))
P.w("Six", len(_pools), note="groups of economies with identical series in the Microsoft file")
P.w("four", _ms.shape[1] - 1, note="periods of the Microsoft series: H1 2025, H2 2025, Q1 2026, Q2 2026")
P.cond("the pools listed in the text have the sizes of the groups of identical series in the Microsoft file",
       sorted(_sizes) == sorted(len(v) for v in _pools), sum(len(v) for v in _pools))
P.v("36", sum(len(v) for v in _pools))
P.v("217", len(panel))
P.v("217", len(panel), label="Taiwan added to those 217")
P.v("145", n_ms_matched, note="Microsoft economies matched to World Bank economies")
P.v("147", n_ms_total)
P.v("142", R["n_ms_all"], note="with income data")
P.v("111", n_ms_total - n_ms_pooled, note="country-specific economies (147 less the 36 pooled)")
_ms_inc = panel.dropna(subset=["ms_q2_2026"])
_ms_inc = _ms_inc[_ms_inc.gni_atlas > 0]
P.v("109", int((_ms_inc.ms_region_imputed == 0).sum()), note="country-specific economies with income data (country_panel.csv)")
P.cond("109 is the estimation sample of the cross-sectional regressions (decomp_total_n, ms_n_cs)", R["decomp_total_n"] == int((_ms_inc.ms_region_imputed == 0).sum()), R["decomp_total_n"])
P.v("33", int((_ms_inc.ms_region_imputed == 1).sum()), note="region-imputed economies with income data")
P.v("36", n_ms_pooled, label="33 of the 36 region-imputed economies")
P.cond("109 + 33 = 142 economies with income data", int((_ms_inc.ms_region_imputed == 0).sum()) + int((_ms_inc.ms_region_imputed == 1).sum()) == R["n_ms_all"])

P = S("\\paragraph{Anthropic windows and samples.}")
P.dt("April", T_APR, note="calendar month of the June 2026 release (published indices)")
P.dt("May 2026", T_MAY)
P.dt("August", T_AUG, note="window of 4-11 August 2025")
P.dt("November 2025", T_NOV, note="window of 13-20 November 2025")
P.dt("February 2026", T_FEB, note="window of 5-12 February 2026")
P.dt("August 2025", T_AUG, note="published values of the release of 15 September 2025")
P.v("0.843", AEI_FACTOR, note="common scaling factor of the published August 2025 values (Anthropic data dictionary)")
P.v("165", min(recomputed_n))
P.v("169", max(recomputed_n))
P.v("157", min(w["n_all"] for w in aui_w[:2]))
P.v("161", max(w["n_all"] for w in aui_w[:2]))
P.v("200", MIN_CONV)
P.v("114", min(R["aui_aug25_n"], R["aui_nov25_n"], R["aui_feb26_n"]))
P.v("115", max(R["aui_aug25_n"], R["aui_nov25_n"], R["aui_feb26_n"]))
P.v("2025", T_AUG.year, label="2025 windows")
P.dt("February 2026", T_FEB, note="window of 5-12 February 2026")
P.v("113", min(R["aui_apr26_n"], R["aui_may26_n"]))
P.v("120", max(R["aui_apr26_n"], R["aui_may26_n"]))
P.dt("April", T_APR, note="calendar month of the June 2026 release")
P.dt("May 2026", T_MAY)
P.v("141", min(w["n_comparison"] for w in aui_w[:2]))
P.v("145", max(w["n_comparison"] for w in aui_w[:2]))
P.v("109", aui_w[2]["n_comparison"], note="comparison economies of the February-May 2026 window (published May index)")
P.dt("February", T_FEB, note="February-May 2026 window: start")
P.dt("May 2026", T_MAY, note="February-May 2026 window: end")
P.dt("May", T_MAY, note="whose May value is the published index")
P.cond("Appendix B: the August 2025 published values are scaled by one common factor (data dictionary)", AEI_FACTOR < 1, AEI_FACTOR)

# ---- Table B.1 (hand-written): releases of the Anthropic Economic Index, from the data dictionary
DD_ROWS = {m.group(1): m.group(0) for m in re.finditer(r"\| (release_\d{4}_\d\d_\d\d) \|[^\n]*", DD)}
T = S("Release & Window & Sample & Accounts and products & Publication rule", "\\bottomrule")
rows_tex = [l for l in T.text.split("\n") if re.match(r"\d+ [A-Z][a-z]{2} \d{4} &", l)]
for rel, line in zip(("release_2025_09_15", "release_2026_01_15", "release_2026_03_24", "release_2026_06_26"), rows_tex):
    ry, rm, rd = (int(x) for x in rel.split("_")[1:])
    row = DD_ROWS[rel]
    R_ = S(line[:34], " \\\\")
    m = re.match(r"(\d+) ([A-Z][a-z]{2}) (\d{4}) & ", line)
    R_.dt(f"{m.group(1)} {m.group(2)} {m.group(3)}", pd.Timestamp(ry, rm, rd), note=f"release date of {rel} (data dictionary)")
    if rel != "release_2026_06_26":
        w = re.search(r"(\d{4})-(\d\d)-(\d\d) to (\d{4})-(\d\d)-(\d\d)", row)
        y0, m0, d0, y1, m1, d1_ = (int(x) for x in w.groups())
        mw = re.search(r"& (\d+)--(\d+) ([A-Z][a-z]{2}) (\d{4}) & about 1 million", line)
        R_.dt(f"{mw.group(1)}--{mw.group(2)} {mw.group(3)} {mw.group(4)}", pd.Timestamp(y0, m0, d0), pd.Timestamp(y1, m1, d1_),
              note="sample window (data dictionary)")
        R_.v("1", ONE_M / 1e6, note="about 1 million conversations (data dictionary: 1M conv.)")
        R_.w("million", ONE_M)
        if rel == "release_2025_09_15":
            R_.v("200", MIN_CONV, note="publication rule: at least 200 sampled conversations")
    else:
        mm_ = re.search(r"calendar months (\w+) and (\w+) (\d{4}) & fixed number of conversations per hour, (\d+) ([A-Z][a-z]{2})--(\d+) ([A-Z][a-z]{2}) (\d{4})", line)
        wins = sorted(set(zip(june.date_start, june.date_end)))
        R_.cond("two calendar months", len(wins) == 2, len(wins))
        R_.dt(mm_.group(1), T_APR, note="calendar month of the June 2026 release (data dictionary)")
        R_.dt(f"{mm_.group(2)} {mm_.group(3)}", T_MAY)
        sm = re.search(r"sampled (\d+) ([A-Z][a-z]{2})[–-](\d+) ([A-Z][a-z]{2}) (\d{4})", row)
        R_.dt(f"{mm_.group(4)} {mm_.group(5)}", pd.Timestamp(int(sm.group(5)), MONTH_ABBR.index(sm.group(2)), int(sm.group(1))),
              note="start of the fixed-rate sampling (data dictionary, report chapter 1)")
        R_.dt(f"{mm_.group(6)} {mm_.group(7)} {mm_.group(8)}", pd.Timestamp(int(sm.group(5)), MONTH_ABBR.index(sm.group(4)), int(sm.group(3))),
              note="end of the sampling")
        R_.pin_rest(why="no further number")
T.pin_rest(why="no further number in the hand-written table")

P = S("\\begin{tablenotes}[flushleft]\\footnotesize\\item Notes: From the data documentation of each release")
P.dt("August 2025", T_AUG)
P.dt("November 2025", T_NOV)
P.dt("February 2026", T_FEB)
P.dt("April", T_APR)
P.dt("May 2026", T_MAY)

# ================================================================================================ Appendix C: prices in other channels
_w15b = csv("W15b_play_countries.csv", ROOT / "output" / "tables")
_cl = _w15b[(_w15b.app == "Claude") & _w15b.compared]
_nc = _w15b[(_w15b.app == "ChatGPT") & ~_w15b.compared & (_w15b.country != "us")]
MS_N_PRICED = int(re.search(r"prices\s+were found in (\d+) locales", WEB_README).group(1))
MS_N_404 = int(re.search(r"(\d+)\s+locale paths returned HTTP 404", WEB_README).group(1))
MS_N_NOPRICE = len(re.search(r"\. ([a-z\-]+ and [a-z\-]+) returned HTTP 200 without prices", WEB_README).group(1).split(" and "))
P = S("The audit observes one channel.")
P.w("Two", len({k.split("_")[1] for k in R2 if k.startswith("xch_")}), note="the two extracts of code/16_cross_channel.py: the Microsoft web store (xch_ms_*) and Google Play (xch_play_*)")
P.dt("16 October 2026", d2)

P = S("\\paragraph{Microsoft's web store.}")
P.v("107", MS_N_PRICED + MS_N_404 + MS_N_NOPRICE, note="locale paths tried: 63 with prices + 42 HTTP 404 + 2 pages without prices (ru-ru, en-lb), data/raw/web/README.md")
P.v("63", R2["xch_ms_locales"])
P.cond("the README's locale count equals the pipeline's", MS_N_PRICED == R2["xch_ms_locales"])
P.v("57", R2["xch_ms_countries"])
P.wpin("two", "several countries appear under two locales (structural)")
P.v("42", MS_N_404, note="locale paths that returned no page (HTTP 404), data/raw/web/README.md")
P.w("three", int(pd.read_csv(ROOT / "data" / "raw" / "web" / "ms365_web_prices.csv", keep_default_na=False)["product"].nunique()), note="the three plans of the web store: Personal, Family, Premium (data/raw/web/ms365_web_prices.csv)")
P.v("54", R2["xch_ms_slope_n"])
P.v("0.082", R2["xch_ms_slope"])
P.v("0.018", R2["xch_ms_slope_se"])
P.v("31", -R2["xch_ms_lmic_pct"])
P.cond("India is the only LMIC country with a web price (xch_ms_lmic_n = 1)", R2["xch_ms_lmic_n"] == 1)
P.v("9", -R2["xch_ms_hic_pct"], note="median of the Personal / Premium ratio relative to the U.S. in high-income countries (-9.0%)")
P.v("5", 100 * XCH_BAND, note="within 5%: |ln ratio| <= 0.05")
P.v("49", R2["xch_ms_web_vs_app_premium_n"], label="all 49 countries for both plans")
P.cond("'all 49 ... for both plans': every comparison of each plan is within 5%, 49 each", R2["xch_ms_web_vs_app_premium_within5_n"] == R2["xch_ms_web_vs_app_premium_n"] == 49
       and R2["xch_ms_web_vs_app_personal_within5_n"] == R2["xch_ms_web_vs_app_personal_n"] == 49)
P.v("98", R2["xch_ms_web_vs_app_premium_n"] + R2["xch_ms_web_vs_app_personal_n"], note="comparisons of both plans: 49 + 49")
P.v("0.000", R2["xch_ms_web_vs_app_premium_median"], note="median log difference (Premium; Personal likewise 0)")
P.cond("the median log difference is zero for Personal as well", R2["xch_ms_web_vs_app_personal_median"] == 0)
P.v("37", R2["xch_ms_web_vs_app_premium_exact_n"], note="identical to the cent (|web - App Store| < 0.005 in the storefront's currency, code/16): 37 for Premium and 37 for Personal")
P.v("49", R2["xch_ms_web_vs_app_premium_n"], label="37 of 49 for each plan")
P.cond("37 of 49 for each plan", R2["xch_ms_web_vs_app_personal_exact_n"] == R2["xch_ms_web_vs_app_premium_exact_n"] == 37 and R2["xch_ms_web_vs_app_personal_n"] == 49)
P.v("0.5", 100 * MS_WITHIN05, note="within 0.5%: |ln(web / App Store)| < 0.005 (code/16_cross_channel.py)")
P.v("45", R2["xch_ms_web_vs_app_premium_within05_n"], note="countries within 0.5% (45 for Premium and 45 for Personal; xch_ms_web_vs_app_*_within05_n)")
P.cond("45 within 0.5% for Personal as well", R2["xch_ms_web_vs_app_personal_within05_n"] == R2["xch_ms_web_vs_app_premium_within05_n"] == 45)
_w15 = pd.read_csv(ROOT / "output" / "tables" / "W15_cross_channel.csv", keep_default_na=False, na_values=[""]).set_index("statistic")
P.v("4.3", R2["xch_ms_web_vs_app_personal_maxgap_pct"], note="widest gap, Personal, percent of the App Store price (xch_ms_web_vs_app_personal_maxgap_pct)")
P.v("2.4", R2["xch_ms_web_vs_app_premium_maxgap_pct"], note="widest gap, Premium")
P.cond("the widest gap of both plans is Sweden (note of the maxgap rows of W15_cross_channel.csv: 'se')",
       _w15.loc["ms_web_vs_app_personal_maxgap", "note"] == "se" == _w15.loc["ms_web_vs_app_premium_maxgap", "note"], 0,
       note="not identical to the cent: " + str(_w15.loc["ms_web_vs_app_premium_exact", "note"]))
P.wpin("two", "the two channels (structural)")

P = S("\\paragraph{Google Play.}")
P.v("8.00", us2["chatgpt_go"], note="the lowest ChatGPT item in the U.S. equals the App Store price of ChatGPT Go (W15b_play_countries.csv)")
P.v("20.00", us2["claude_pro"], note="the lowest Claude item in the U.S. is the Pro price")
P.v("30", R2["xch_play_gemini_n"], label="Gemini: no range in any of the 30 countries")
P.cond("Gemini shows no range in any country", R2["xch_play_gemini_with_range"] == 0)
P.v("25", R2["xch_play_chatgpt_same_currency"], label="25 of the 30 countries")
P.v("30", R2["xch_play_countries"], label="of the 30 countries")
P.cond("the countries not compared are Argentina, Ukraine and Kenya (dollar-priced storefronts) and Bangladesh (no storefront)",
       set(_nc.country) == {"ar", "ua", "ke", "bd"} and set(_nc[_nc.app_store_storefront].country) == {"ar", "ua", "ke"}
       and all(_nc[_nc.app_store_storefront].app_store_currency == "USD") and list(_nc[~_nc.app_store_storefront].country) == ["bd"], len(_nc))
P.v("5", 100 * XCH_BAND, label="within 5% (ChatGPT)")
P.v("22", R2["xch_play_chatgpt_within5_n"])
P.v("25", R2["xch_play_chatgpt_same_currency"], label="22 of the 25 countries")
_cg = _w15b[(_w15b.app == "ChatGPT") & _w15b.compared]
P.v("0.5", 100 * XCH_EXACT, note="'within the 0.5% band of the stability comparison': code/16's identical band, |ln(Play / App Store)| < 0.005")
P.cond("the identical band of code/16 equals the stability tolerance of code/09b (0.005), as the text says", XCH_EXACT == STAB_TOL, STAB_TOL)
P.v("20", R2["xch_play_chatgpt_exact_n"], note="'identical to it ... in 20': same-currency countries whose lowest Play item is within 0.5% of the App Store Go price (xch_play_chatgpt_exact_n)")
P.cond("20 of the 25 compared countries are within the band (W15b_play_countries.csv), a subset of the within-5% ones",
       R2["xch_play_chatgpt_exact_n"] <= R2["xch_play_chatgpt_within5_n"] and abs(R2["xch_play_chatgpt_exact"] - R2["xch_play_chatgpt_exact_n"] / R2["xch_play_chatgpt_same_currency"]) < 1e-9
       and int((_cg.log_diff.abs() < XCH_EXACT).sum()) == R2["xch_play_chatgpt_exact_n"], R2["xch_play_chatgpt_exact"])
P.v("19", int((_cg.log_diff.abs() < 1e-9).sum()), note="'19 to the cent': compared countries whose lowest Play item equals the App Store Go price exactly (W15b_play_countries.csv)")
P.v("39.99", float(_cg[_cg.country == "br"].play_min.iloc[0]), note="Brazil: lowest ChatGPT item on Google Play in BRL (W15b_play_countries.csv; 'R$39.99 against R$39.90' = Play against App Store, as in Table C.2)")
P.v("39.90", float(_cg[_cg.country == "br"].app_store_price.iloc[0]), note="Brazil: App Store price of ChatGPT Go in BRL")
P.cond("Brazil is the one country within the band but not equal to the cent", list(_cg[(_cg.log_diff.abs() >= 1e-9) & (_cg.log_diff.abs() < XCH_EXACT)].country) == ["br"])
P.v("0.000", R2["xch_play_chatgpt_median"])
P.dt("15 October 2026", FX_DATES[-1], note="exchange rates of the fawazahmed0 snapshot usd_2026-10-15.json (code/16_cross_channel.py)")
P.v("0.63", R2["xch_play_chatgpt_lmic_ratio"])
P.v("0.64", R2["xch_play_chatgpt_lmic_ratio_wb"])
P.cond("the same discount as the App Store: ChatGPT Go's median LMIC ratio to the U.S. price is 0.62 in the App Store (Table 3) and 0.63 on Play (within 0.02)",
       abs(R2["xch_play_chatgpt_lmic_ratio"] - R2["rel_go_plus_lmic_med"]) < 0.02, R2["rel_go_plus_lmic_med"])
P.v("5", 100 * XCH_BAND, label="within 5% (Claude)")
P.v("12", R2["xch_play_claude_within5_n"])
P.v("25", R2["xch_play_claude_same_currency"], label="12 of 25 countries")
P.v("0.45", _cl.log_diff.min(), note="smallest log difference of Claude's lowest Play item against the App Store Pro price (W15b_play_countries.csv), negative")
P.v("0.13", _cl.log_diff.max(), note="largest")
P.v("1.05", R2["xch_play_claude_lmic_ratio"])

P = S("\\paragraph{What the check does and does not show.}", "of the page it was parsed from." + ("" if ANON_COPY else "\n\\fi"))   # the paragraph spans the \ifanon block (resolved in the anonymised copy)
P.w("two", len(LOC_AI), note="the two localised AI tiers, ChatGPT Go and Character.AI Lite (AI plans whose deviation rises with income)")
P.cond("of the two localised AI tiers only ChatGPT is among the apps collected on Google Play (data/raw/web/play_iap_ranges.csv)",
       set(LOC_AI) == {"chatgpt_go", "characterai_lite"} and "ChatGPT" in PLAY_APPS_COLLECTED and not any("character" in a.lower() for a in PLAY_APPS_COLLECTED), len(PLAY_APPS_COLLECTED))
P.wpin("two", "the two channels (structural)")
P.v("5", 100 * XCH_BAND, note="'the two channels agree within 5%': every Microsoft comparison is within 5%")
P.cond("'usually to the cent': more than half of the comparisons of each plan are identical to the cent (37 of 49)", R2["xch_ms_web_vs_app_premium_exact"] > 0.5 and R2["xch_ms_web_vs_app_personal_exact"] > 0.5, R2["xch_ms_web_vs_app_premium_exact"])
P.v("487", int(re.search(r"\(`web/raw/`, (\d+) files:", WEB_README).group(1)), note="raw pages of both extracts (data/raw/web/README.md)")
P.v("77", int(re.search(r"a README and SHA256SUMS; (\d+) MB\)", WEB_README).group(1)), note="size of the deposited archive (README)")
P.cond("the 487 raw pages are 107 Microsoft locale pages + 362 Google Play pages + 17 probe pages + 1 locale selector (README)",
       sum(int(x) for x in re.search(r"(\d+) Microsoft 365 locale pages, (\d+)\nGoogle Play pages, (\d+) Microsoft probe pages and (\d+) locale selector", WEB_README).groups()) == 487, 487)
for _branch in range(1 if ANON_COPY else 2):        # both branches of the \ifanon block carry the sentence (the anonymised copy keeps one)
    P.wpin("two", "the two extracts (structural)")

S("Cross-channel comparison of listed prices, 16 October 2026").dt("16 October 2026", d2)
P = S("\\begin{tablenotes}[flushleft]\\footnotesize\\item Notes: Microsoft rows: monthly web prices from")
P.v("63", R2["xch_ms_locales"])
P.v("57", R2["xch_ms_countries"])
P.v("100", PCT_CONV, note="100 (e^m - 1) percent (code/16_cross_channel.py pct())")
P.v("1", PCT_ONE)
P.wpin("two", "where the two (the Play page and the storefront) share a currency (structural)")
P.dt("15 October 2026", FX_DATES[-1])
S("Google Play's lowest in-app price and the App Store price, ChatGPT and Claude, 16 October 2026").dt("16 October 2026", d2)
S("\\begin{tablenotes}[flushleft]\\footnotesize\\item Notes: Upper block: ChatGPT, against the App Store price of ChatGPT Go").dt("15 October 2026", FX_DATES[-1])

# ================================================================================================ Appendix D: the public usage indicators
from scipy.stats import t as st_t

cpg = csv("cross_provider_gradient_robustness.csv").set_index("specification")


def ci_level(lo, hi, se, df=None):
    """coverage (per cent) implied by an interval [lo, hi] around the estimate with standard error se: the normal reference,
    or the t distribution with df degrees of freedom"""
    hw = (hi - lo) / 2 / se
    return 100 * (2 * (st_t.cdf(hw, df) if df else snorm.cdf(hw)) - 1)


P = S("\\paragraph{Any use.} On country-specific estimates")
P.v("8.3", R["ms_lev_cs_b"], note="percentage points per log point of GNI per capita, country-specific estimates")
P.v("0.370", R["ms_log_cs_b"])
P.v("0.021", R["ms_log_cs_se"])
P.v("0.71", R["ms_log_cs_r2"])
P.v("0.336", R["ms_log_all_b"])
P.v("0.367", R["ms_log_collapsed_b"])
P.v("0.355", min(R[f"{c}_b"] for c in ctrl_cols), note="elasticity with controls, columns (2)-(5) of Appendix Table D.2")
P.v("0.367", max(R[f"{c}_b"] for c in ctrl_cols))
P.pin("3", "4", why="column numbers (3)-(4) of Appendix Table D.2, the specifications with the urbanisation control")
P.cond("urbanisation is significant at 5% in columns (3) and (4) and loses significance in column (5); no other control reaches 1.96 standard errors",
       R["ms_c3_urban_p"] < 0.05 and R["ms_c4_urban_p"] < 0.05 and R["ms_c5_urban_p"] > 0.05
       and all(abs(R[f"ms_c{k}_{v}_b"] / R[f"ms_c{k}_{v}_se"]) < 1.96 for k in (2, 3, 4, 5) for v in ("internet_pct", "tertiary_enrol", "age65_pct", "fx_online_merchant_pay")
               if f"ms_c{k}_{v}_b" in R), R["ms_c3_urban_p"])
P.about("0.04", 0.5 * (R["ms_c3_urban_p"] + R["ms_c4_urban_p"]), 0.005, note="p-values of urbanisation in columns (3) and (4): 0.039 and 0.043")
P.wpin("half", "first half of 2025 = the first period of the Microsoft series")
P.v("2025", int(MS_COLS[0][-4:]), label="first half of 2025")
P.wpin("quarter", "second quarter of 2026 = the last period of the Microsoft series")
P.v("2026", int(MS_COLS[-1][-4:]), label="second quarter of 2026")
P.w("three", len(g3), note="the three higher income groups")
P.v("21", min(g3))
P.v("26", max(g3))
P.v("5.5", R["gain_pp_median_HIC"], note="median gain in the user share, percentage points, H1 2025 to Q2 2026 (gain_pp_median_HIC; Figure D.1b)")
P.v("3.7", R["gain_pp_median_UMIC"])
P.v("2.0", R["gain_pp_median_LMIC"])
P.v("0.9", R["gain_pp_median_LIC"])
P.v("0.026", R["conv_log_b"])
P.v("0.011", R["conv_log_se"])
P.v("1.37", R["conv_pp_b"])
P.v("0.13", R["conv_pp_se"])
P.notation()

dsamp = panel.dropna(subset=["ms_q2_2026", "internet_pct"])
dsamp = dsamp[(dsamp.ms_region_imputed == 0) & dsamp.gni_atlas.notna()]
P = S("\\paragraph{The accounting split.} Define the ratio $R_c=D_c/I_c$")
P.pin("15", "64", why="age band of the Microsoft AI User Share (population 15-64)")
P.v("109", R["decomp_total_n"])
P.cond("no ratio D/I exceeds one in the estimation sample", len(dsamp) == R["decomp_total_n"] and (dsamp.ms_q2_2026 / dsamp.internet_pct).max() <= 1.0,
       (dsamp.ms_q2_2026 / dsamp.internet_pct).max())
P.v("0.182", R["decomp_connect_b"])
P.v("0.189", R["decomp_cond_b"])
P.v("0.371", round(R["decomp_connect_b"], 3) + round(R["decomp_cond_b"], 3), note="sum of the two rounded components")
P.v("0.370", R["decomp_total_b"])
P.v("49", 100 * R["decomp_share_connect"])
P.v("0.05", R["ms_lnI_cond_b"])
P.v("0.20", R["ms_lnI_cond_se"])
P.v("21", 100 * R["share_connect_gap_UMIC"])
P.v("49", 100 * R["share_connect_gap_LMIC"])
P.v("67", 100 * R["share_connect_gap_LIC"])
P.w("three", R["ms_n_cs_LIC"], note="low-income economies with country-specific Microsoft data")
P.v("37.5", 100 * R["ai_among_online_HIC"])
P.v("22.7", 100 * R["ai_among_online_UMIC"])
P.v("23.6", 100 * R["ai_among_online_LMIC"])
P.v("23.0", 100 * R["ai_among_online_LIC"])
P.v("0.03", R["di_nonhic_b"])
P.v("0.06", R["di_nonhic_se"])
P.w("three", R["ms_n_cs_LIC"], note="the low-income row contains three economies")
P.notation()

P = S("\\paragraph{Per-capita Claude activity.} Anthropic's own report documents an income gradient of Claude activity near 0.7")
P.about("0.7", gdp_rep.loc["release_2025_09_15", "elasticity"], 0.05, note="Anthropic's Sept-2025 report (the replication file of the release gives 0.69)")
P.v("96", R["n_two_margins"], note="economies covered by both indicators (the common sample)")
P.v("42", R["tm_n_HIC"])
P.v("33", R["tm_n_UMIC"])
P.v("20", R["tm_n_LMIC"])
_rw = re.search(r"one low-income economy, ([A-Z][a-z]+)\)", P.text).group(1)
P.cond("the one low-income economy of the common sample is the one named in the text (Rwanda; D1_two_margins_sample.csv)", list(D1T[D1T.grp == "LIC"].country_wb) == [_rw] and R["tm_n_LIC"] == WORDS["one"], R["tm_n_LIC"])
P.cond("the group counts add up to the common sample", R["tm_n_HIC"] + R["tm_n_UMIC"] + R["tm_n_LMIC"] + R["tm_n_LIC"] == R["n_two_margins"], R["n_two_margins"])
P.v("0.340", R["tm_diff_b"])
P.w("two", N_IND, note="the two elasticities")
P.v("0.034", R["tm_diff_se"])
P.v("95", BOOT_HI - BOOT_LO, note="percentile bootstrap interval: 2.5th to 97.5th percentile (code/20_analysis.py)")
P.v("0.27", R["tm_diff_boot_lo"])
P.v("0.40", R["tm_diff_boot_hi"])
P.v("0.50", R["tm_logit_ms_b"])
P.v("0.71", R["tm_aui_b"], label="AUI elasticity, log-odds row")
P.v("0.33", R["tm_ms_nonhic_b"])
P.v("0.69", R["tm_aui_nonhic_b"])
P.v("0.31", R["tm_ms_ctl_b"])
P.v("0.55", R["tm_aui_ctl_b"])
P.v("0.38", R["tm_ms_2025_b"])
P.v("0.62", R["tm_aui_2025_b"])
P.v("0.36", R["tm_ms_allms_b"])
P.v("0.73", R["tm_aui_allms_b"])
P.v("0.266", xprov.loc["Region fixed effects", "difference"])
P.v("0.232", xprov.loc["Internet, education, urbanisation", "difference"])
P.v("0.329", gap_loo.gradient_gap.min())
P.v("0.351", gap_loo.gradient_gap.max())
P.v("111", R["aui_common_n"])
P.w("five", N_AUI_WINDOWS, note="Anthropic windows: Aug 2025, Nov 2025, Feb 2026, Apr 2026, May 2026")
f = P.sub("0.676 in August 2025", "August 2025")                  # each elasticity is tied to the month printed next to it
f.v("0.676", R["aui_common_aug25_b"])
f.dt("August 2025", T_AUG, note="first Anthropic window (4-11 August 2025)")
f = P.sub("0.741 in February 2026", "February 2026")
f.v("0.741", R["aui_common_feb26_b"])
f.dt("February 2026", T_FEB, note="Anthropic window of 5-12 February 2026")
P.v("0.064", R["aui_change_aug25_feb26_b"])
P.v("0.018", R["aui_change_aug25_feb26_se"])
f = P.sub("0.734 in May 2026", "May 2026")
f.v("0.734", R["aui_common_may26_b"])
f.dt("May 2026", T_MAY, note="last Anthropic window (May 2026)")

S("Income gradient of generative-AI use (Microsoft AI User Share, Q2 2026)").v("2026", int(MS_COLS[-1][-4:]))
P = S("\\item \\emph{Notes:} OLS with HC3 standard errors in parentheses.")
P.v("65", AGE_UP, note="population share aged 65 and above (WDI series SP.POP.65UP.TO.ZS in code/10_build_dataset.py)")
P = S("Diffusion dynamics.")
P.w("three", R["ms_n_cs_LIC"], note="low-income economies with country-specific Microsoft estimates")
P.v("2025", int(MS_COLS[0][-4:]), label="H1 2025")
P.v("2026", int(MS_COLS[-1][-4:]), label="Q2 2026")
P = S("\\item \\emph{Notes:} OLS with HC3 standard errors. Controls measured in percent; Findex 2025 for digital payments.")
P.v("2025", FINDEX_EDITION, note="edition named in code/10_build_dataset.py")
S("Accounting split of the AI-use gap into internet use and the AI-to-internet-user ratio (country-specific estimates, Q2 2026)").v("2026", int(MS_COLS[-1][-4:]))
P = S("\\item \\emph{Notes:} $\\ln D = \\ln I + \\ln(D/I)$")
P.pin("15", "64", why="age band of the Microsoft AI User Share (population 15-64)")
P.w("three", R["ms_n_cs_LIC"], note="the low-income row rests on three economies")
P.notation()
P = S("Accounting split of the log gap in AI use relative to the high-income group")
P.v("2026", int(MS_COLS[-1][-4:]), label="Q2 2026")
P.w("three", R["ms_n_cs_LIC"])
P = S("Income gradients in two differently measured AI-use indicators.")
P.w("two", N_IND, note="Microsoft AI User Share and Anthropic AI Usage Index")
P.v("2026", int(MS_COLS[-1][-4:]), label="Q2 2026")
P.dt("May 2026", T_MAY, note="last Anthropic window (May 2026)")
P.v("96", R["n_two_margins"])
P = S("\\item \\emph{Notes:} Cells are OLS slopes on log GNI per capita in common samples;")
P.v("2,000", N_BOOT)
P.v("42", R["tm_n_HIC"])
P.v("33", R["tm_n_UMIC"])
P.v("20", R["tm_n_LMIC"])
P.cond("the main sample comprises as many low-income economies as the text says (one)",
       R["tm_n_LIC"] == WORDS[re.search(r"and (\w+) low-income economy", P.text).group(1)], R["tm_n_LIC"])
P.v("54", R["tm_ms_nonhic_n"], note="economies of the common sample outside the high-income group")
S("Sensitivity of the difference between the two usage-indicator income elasticities").w("two", N_IND)
S("Specification & Difference & HC3 SE & 95\\% interval & $N$").v(
    "95", ci_level(cpg.loc["Baseline", "difference_ci_low"], cpg.loc["Baseline", "difference_ci_high"], cpg.loc["Baseline", "difference_HC3_SE"]))
P = S("\\item Notes: Dependent variable is $\\ln(AUI/D)$")
P.w("two", N_IND)
P.v("96", cpg.loc["Baseline", "n"], note="common economies of the baseline")
P.cond("every interval of the table is difference +/- 1.96 s.e. (95%, normal reference)",
       all(abs(ci_level(r.difference_ci_low, r.difference_ci_high, r.difference_HC3_SE) - 95) < 1e-4 for _, r in cpg.iterrows()), 95.0)
S("Common sample ($N=111$)").v("111", R["aui_common_n"])
P = S("\\item \\emph{Notes:} OLS of log AUI on log GNI per capita (2025) with HC3 standard errors;")
P.v("2025", int(gni.gni_atlas_year.mode().iloc[0]), label="GNI vintage")
P.v("200", MIN_CONV)
P.dt("Aug 2025", T_AUG, note="first window of the economies with at least 200 sampled conversations (4-11 August 2025)")
P.dt("Feb 2026", T_FEB, note="last window of the economies with at least 200 sampled conversations (5-12 February 2026)")
P.dt("Apr", T_APR, note="published values: calendar month April 2026")
P.dt("May 2026", T_MAY, note="published values: calendar month May 2026")
P.w("five", len(aui_n), note="windows of the Anthropic index: Aug 2025, Nov 2025, Feb 2026, Apr 2026, May 2026")
P.dt("Aug 2025", T_AUG, note="change from the August 2025 window")
P.dt("Feb 2026", T_FEB, note="to the February 2026 window")
P.v("0.064", R["aui_change_aug25_feb26_b"])
P.v("0.018", R["aui_change_aug25_feb26_se"])
P.dt("Feb", T_FEB, note="second change: from the February 2026 window")
P.dt("May 2026", T_MAY, note="to the May 2026 window")
P.v("0.006", R["aui_change_feb26_may26_b"])
P.v("0.016", R["aui_change_feb26_may26_se"])
P.cond("the two changes are estimated on the common sample of all five windows (N = 111 economies, 222 observations in the pooled regression)",
       R["aui_change_aug25_feb26_n"] == 2 * R["aui_common_n"] == R["aui_change_feb26_may26_n"], R["aui_change_aug25_feb26_n"])

# ================================================================================================ Appendix E: additional tables
sl = islopes                                                                                    # item slopes (code/09b)
lpr = csv("local_price_robustness.csv").set_index("plan")
mmc = csv("matched_menu_currency_sensitivity.csv", PU).set_index("specification")
thr = csv("burden_threshold_sensitivity.csv")
vint = csv("burden_vintage_sensitivity.csv")
PANEL_COLS = " ".join(panel.columns)
MBB_GB = int(re.search(r"mbb_(\d)gb_pct_gni_latest_official", PANEL_COLS).group(1))             # size of the data-only basket in GB
MBB_USD_YEAR = int(re.search(r"mbb_\dgb_usd_(\d{4})", PANEL_COLS).group(1))                     # year of the dollar price of the basket
MBB_YEAR = int(gni.mbb_2gb_latest_year.mode().iloc[0])                                          # year of the selected (latest official) basket
W5 = pd.read_csv(ROOT / "output" / "tables" / "W5_item_classes.csv", keep_default_na=False, na_values=[""]).set_index(["item_class", "type"])
W2 = pd.read_csv(ROOT / "output" / "tables" / "W2_benchmarks.csv", keep_default_na=False, na_values=[""])
TAXABS_TOL = grab(SRC12, r"at_us = \(t\.price_usd / t\.us_price - 1\)\.abs\(\) < ([0-9.]+)", "tax-absorption tolerance")   # 0.006 (code/12 computes at_us on its own line)
MIN_CLASS = int(grab((ROOT / "code" / "41_tables_wave2.py").read_text(), r"\nMIN_CLASS = (\d+)", "rows needed for a within-3% class of Table E.13"))
W1_LISTINGS = int((prices.price_local.notna() & ~prices.plan.str.endswith("_other")).sum())   # first-wave listings of the ten plans

P = S("Tables~\\ref{tab:local} to~\\ref{tab:store} report the first-wave estimates")
P.notation()

# -- Table E.1: local prices by plan
P = S("Local prices and localisation slopes by plan, first wave (27 September 2026)")
date_is(P, d1, "27", "September", "2026", note="fetch date of the first wave")
P = S("\\item \\emph{Notes:} Monthly App Store prices, 27 September 2026, tax-inclusive except in the U.S. and Canada;")
date_is(P, d1, "27", "September", "2026", note="fetch date of the first wave")
P.v("0.228", R["plr_b"], note="slope on ln income of ln(PLR), the Atlas-over-PPP income ratio, across the economies with both incomes")
P.v("0.014", R["plr_se"])
P.v("197", R["plr_n"])
P.v("0.243", samePPP.loc["chatgpt_go", "ppp_same_sample_beta"], note="same 164-economy sample as the ChatGPT Plus and Go price regressions")
_prop = np.polyfit(np.log(gni.gni_atlas), np.log(STD_PRICE * gni.gni_atlas / POLJ["y_us"]), 1)[0]
P.v("1", _prop, note="slope of ln(p) on ln(y) for the proportional schedule p = 20 y / y_US (recomputed)")
P.v("2025", int(gni.gni_atlas_year.mode().iloc[0]), note="economies whose GNI per capita is the 2025 vintage")
P.v("0.149", lpr.loc["chatgpt_go", "beta_2025"], note="Go slope on the economies with 2025 income (local_price_robustness.csv)")
P.v("0.046", lpr.loc["chatgpt_plus", "beta_2025"])
P.cond("the 2025-income restriction keeps 155 of the 164 economies for both plans (the same sample)",
       lpr.loc["chatgpt_go", "n_2025"] == lpr.loc["chatgpt_plus", "n_2025"], lpr.loc["chatgpt_go", "n_2025"])

# -- Table E.2: price slopes under alternative standard errors
S("Plan or ratio & Slope & HC3 SE & Currency SE & Cluster 95\\% CI & $N$").v(
    "95", ci_level(lpr.loc["chatgpt_go", "cluster_t_ci_low"], lpr.loc["chatgpt_go", "cluster_t_ci_high"], lpr.loc["chatgpt_go", "se_currency_cluster"],
                   int(lpr.loc["chatgpt_go", "currency_clusters"]) - 1),
    note="level of the t(G-1) interval around the Go slope; the same level for the other rows (checked in the notes passage)")
P = S("\\item Notes: All outcomes are in logs. Currency-clustered CR1 errors")
_rows = [(k, lpr.loc[k]) for k in ("chatgpt_go", "chatgpt_plus", "claude_pro", "gemini_pro")]
P.cond("each interval of the table is estimate +/- t(0.975, G-1) x cluster s.e. at the 95% level",
       all(abs(ci_level(r.cluster_t_ci_low, r.cluster_t_ci_high, r.se_currency_cluster, int(r.currency_clusters) - 1) - 95) < 1e-6 for k, r in _rows)
       and abs(ci_level(wr.loc["ChatGPT Go / Plus", "cluster_t_ci_low"], wr.loc["ChatGPT Go / Plus", "cluster_t_ci_high"],
                        wr.loc["ChatGPT Go / Plus", "se_currency_cluster"], int(wr.loc["ChatGPT Go / Plus", "currency_clusters"]) - 1) - 95) < 1e-6, 95.0)
P.v("39", lpr.loc["chatgpt_go", "currency_clusters"], note="currency clusters of the ChatGPT Go regression")
P.cond("the same number of clusters for ChatGPT Go, ChatGPT Plus, Claude Pro and the Go / Plus ratio",
       all(int(lpr.loc[k, "currency_clusters"]) == int(lpr.loc["chatgpt_go", "currency_clusters"]) for k in ("chatgpt_plus", "claude_pro"))
       and int(wr.loc["ChatGPT Go / Plus", "currency_clusters"]) == int(lpr.loc["chatgpt_go", "currency_clusters"]), int(lpr.loc["chatgpt_go", "currency_clusters"]))
P.v("40", lpr.loc["gemini_pro", "currency_clusters"], note="Google AI Pro, the exception")
_cs = pc[pc.plan == "chatgpt_plus"].currency.value_counts()
P.v("102", _cs["USD"], note="USD storefronts in the 164-economy sample")
P.v("25", _cs["EUR"], note="euro storefronts")
P.v("37", int((_cs == 1).sum()), note="currencies used by a single storefront")
P.cond("USD, EUR and the singleton currencies make up the 164-economy sample and the 39 clusters", _cs["USD"] + _cs["EUR"] + (_cs == 1).sum() == _cs.sum() == int(lpr.loc["chatgpt_plus", "n"])
       and len(_cs) == int(lpr.loc["chatgpt_plus", "currency_clusters"]), len(_cs))
P.w("two", len(wr.index[0].split(" / ")), note="plans of the ratio (ChatGPT Go / Plus)")
P.cond("the clustered interval of ChatGPT Plus includes zero", lpr.loc["chatgpt_plus", "cluster_t_ci_low"] < 0 < lpr.loc["chatgpt_plus", "cluster_t_ci_high"],
       lpr.loc["chatgpt_plus", "cluster_t_ci_low"])
P.cond("the clustered interval of the Go slope excludes zero", lpr.loc["chatgpt_go", "cluster_t_ci_low"] > 0, lpr.loc["chatgpt_go", "cluster_t_ci_low"])
P.notation()

# -- Table E.3: the Go-to-Plus ratio by currency sample
S("Sample & Slope & HC3 SE & HC3 95\\% interval & $N$").v(
    "95", ci_level(mmc.loc["All matched storefronts", "hc3_ci_low"], mmc.loc["All matched storefronts", "hc3_ci_high"], mmc.loc["All matched storefronts", "se_HC3"]),
    note="level of the normal-reference HC3 interval")
P = S("\\item Notes: OLS of the log Go-to-Plus listing ratio on log Atlas GNI per capita, first wave.")
P.cond("every HC3 interval of the table is slope +/- 1.96 s.e. (95%, normal reference)",
       all(abs(ci_level(mmc.loc[k, "hc3_ci_low"], mmc.loc[k, "hc3_ci_high"], mmc.loc[k, "se_HC3"]) - 95) < 1e-4
           for k in ("All matched storefronts", "USD only", "Exclude USD", "Exclude USD and EUR")), 95.0)
P.cond("no low-income economy remains in the non-USD samples", mmc.loc[["Exclude USD", "Exclude USD and EUR"], "low_income_n"].eq(0).all(),
       mmc.loc["Exclude USD", "low_income_n"])

# -- Table E.4: storefront availability
P = S("\\item \\emph{Notes:} All 217 World Bank economies.")
P.v("217", len(panel))
P.cond("the rows of the table cover all 217 economies", sum(R[f"n_store_{g}"] for g in ("HIC", "UMIC", "LMIC", "LIC")) == len(panel),
       sum(R[f"n_store_{g}"] for g in ("HIC", "UMIC", "LMIC", "LIC")))
P.v("12", AAB_MONTHS)
P.v("100", AAB_PCT)

# -- Table E.5: burden by income quintile and comparison with mobile broadband
S("Burden of a \\$20 plan by income quintile, and comparison with mobile broadband (medians)").v("20", STD_PRICE)
P = S(" & & \\multicolumn{3}{c}{\\$20 plan, \\% of quintile mean income}")
P.v("20", STD_PRICE)
P = S("Income group & $N$ & Poorest 20\\% & Middle 20\\% & Richest 20\\% & 2 GB, \\% GNI p.c. & broadband")
P.v("20", QSHARE, label="Poorest 20%")
P.v("20", QSHARE, label="Middle 20%")
P.v("20", QSHARE, label="Richest 20%")
P.v("2", MBB_GB, note="size of the data-only basket (panel column mbb_2gb_pct_gni_latest_official)")
_q = gni[gni.q1_share.notna()]
_sy = _q.groupby("income_group").dist_year.median()
P = S("\\item \\emph{Notes:} Quintile shares $s_{cq}\\in(0,1)$ from the latest household survey in WDI")
P.v("2021", _sy.min(), note="smallest group median of the survey year")
P.v("2023", _sy.max(), note="largest group median of the survey year")
P.v("0.2", 1 / N_QUINT, note="a quintile holds one fifth of the population: mean income = y x share / 0.2")
P.v("2", MBB_GB, note="ITU data-only basket of 2 GB per month")
P.v("2024", MBB_YEAR, note="latest official year of the 2 GB basket (204 of 206 economies)")
P.v("20", STD_PRICE)
P.v("2024", MBB_USD_YEAR, note="year of the dollar price of the basket (panel column mbb_2gb_usd_2024)")
P.cond("the 2 GB basket is the data-only mobile-broadband basket of the ITU file (code/05_itu_price_baskets.py: i271mb_2GB_GNI)",
       "i271mb_2GB_GNI" in (ROOT / "code" / "05_itu_price_baskets.py").read_text(), 2)
P.notation()

# -- Table E.6: share of economies and population above alternative benchmarks
_wld = pd.read_csv(ROOT / "data" / "raw" / "wb" / "wb_indicators_long.csv", keep_default_na=False, na_values=[""])
_wld = _wld[(_wld.indicator == "SP.POP.1564.TO") & (_wld.iso3 == "WLD") & (_wld.year == 2025)].value.iloc[0]
S("Share of economies and population above alternative benchmarks, \\$20 plan").v("20", STD_PRICE)
P = S("\\item Notes: 201 economies. Population is ages 15--64;")
P.v("201", R["n_econ_gni"])
_age = re.search(r"SP\.POP\.(\d\d)(\d\d)\.TO", SRC10)
P.v("15", int(_age.group(1)), note="age band of the population weights (WDI series SP.POP.1564.TO used in code/10_build_dataset.py)")
P.v("64", int(_age.group(2)))
P.v("98.6", 100 * gni.pop1564.sum() / _wld, note="working-age population of the 201 economies over the WDI world aggregate (SP.POP.1564.TO, WLD, 2025)")
P.v("2", BENCH, note="the 2% row is the broadband benchmark")
P.cond("the thresholds table has a 2% row", (thr.threshold_pct == BENCH).any(), BENCH)
_t25 = thr[(thr["sample"] == "2025 only") & (thr.monthly_price_usd == 20) & (thr.threshold_pct == BENCH)].iloc[0]
P.v("182", R["n_econ_gni2025"])
P.cond("the 2025-vintage sample of the threshold file has 182 economies", int(_t25.n) == R["n_econ_gni2025"], _t25.n)
P.v("2025", int(gni.gni_atlas_year.mode().iloc[0]))
P.v("60.0", 100 * _t25.covered_working_age_share_above)
P.v("2", BENCH, label="at 2%")
_v25 = vint[vint["sample"] == "2025 only"].set_index("income_group").median_burden20
P.w("four", len(GROUPS), note="income groups")
P.v("0.67", _v25["High income"])
P.v("3.09", _v25["Upper-middle income"])
P.v("8.87", _v25["Lower-middle income"])
P.v("28.9", _v25["Low income"])

# -- Table E.7 (tab:policy): alternative price schedules and the subsidy
S("Burden of the \\$20 tier under alternative price schedules, and the subsidy required under uniform pricing").v("20", STD_PRICE)
S(" & & \\multicolumn{5}{c}{Median burden, \\% of GNI per capita} & \\multicolumn{3}{c}{Subsidy to the 2\\% benchmark (medians)}").v("2", BENCH)
P = S("\\item Notes: Burden $=1200p/y$ with $y$ GNI per capita (Atlas).")
P.v("1200", AAB_MONTHS * AAB_PCT)
P.v("20", STD_PRICE, label="schedules anchored at the U.S. price")
P.v("20", STD_PRICE, label="entry-slope schedule")
P.v("0.143", POLJ["beta_go"], note="exponent of the entry-slope schedule: extensions/policy_counterfactuals.py reads loc_chatgpt_go_b of results.json (the first-wave slope, 0.1435)")
P.cond("the exponent is the first-wave slope of results.json", POLJ["beta_go"] == R["loc_chatgpt_go_b"], R["loc_chatgpt_go_b"])
P.v("0.143", R2["chatgpt_go_usd_slope"], note="the second-wave Go dollar slope (0.1430) rounds to the same value", label="0.143 in the second wave as well")
P.v("0.033", R2["default_slope"])
P.v("20", STD_PRICE, label="entry-deviation schedule")
P.v("0.110", POLJ["beta_go_dev"], note="exponent of the entry-deviation schedule (chatgpt_go_dev_slope)")
P.v("20", STD_PRICE, label="price-level schedule")
P.v("20", STD_PRICE, label="proportional schedule")
P.v("100", AAB_PCT, label="subsidy rate in per cent")
P.v("12,000", R["threshold_gni_for_2pct_p20"], note="income at which the $20 plan costs exactly 2% of GNI per capita")
P.v("0,240", AAB_MONTHS * STD_PRICE, note="annual price of the $20 plan: the dollar subsidy is max(0, 240 - 0.02 y)")
P.v("0.02", BENCH / 100, note="the benchmark share of income")
P.w("one tenth", COVERED, note="share of the working-age population covered (extensions/policy_counterfactuals.py)")
_ba = re.search(r"SP\.POP\.(\d\d)(\d\d)\.TO", SRC10)
P.v("15", int(_ba.group(1)), label="age band, lower end")
P.v("64", int(_ba.group(2)), label="age band, upper end")
P.v("20", STD_PRICE, label="the $20 column of Table 8")
P.v("113", POLJ["n_econ_need_subsidy"], note="economies whose burden at the uniform $20 price exceeds 2%")
P.cond("113 equals the number of economies above the benchmark in the burden data", POLJ["n_econ_need_subsidy"] == R["n_countries_aab20_gt2"], R["n_countries_aab20_gt2"])
P.v("57", POLJ["pop_share_above2_b_entry"], note="entry-slope schedule (56.9%); the entry-deviation schedule gives 57.1%, 'each leave 57%'")
P.cond("the entry-deviation schedule also leaves 57% of the covered working-age population above the benchmark", round(POLJ["pop_share_above2_b_entry_dev"]) == 57, POLJ["pop_share_above2_b_entry_dev"])
P.v("41", POLJ["pop_share_above2_b_plr"])
P.v("60", POLJ["pop_share_above2_b_uniform"])
P.notation()

# -- Table E.8 (tab:classes): product classes
P = S("Income slopes of local prices by product class, 16 October 2026")
P.dt("16 October 2026", d2)
P.notation()
S("Product class & Items & Median slope & Interquartile range & Slope $>0.10$ (\\%)").v("0.10", THR_SLOPE)
P = S("\\item \\emph{Notes:} 130 of the 147 items listed with a U.S. price in at least 60 storefronts after de-duplication")
P.v("130", int(W5.n.sum()) - int(W5.loc[("ai_bundle", "subscription"), "n"]) - int(W5.loc[("nonai", "consumable"), "n"]) - int(W5.loc[("ai_feature", "consumable"), "n"])
    - int(W5.loc[("ai_core", "subscription"), "n"]) - int(W5.loc[("ai_core", "consumable"), "n"]) - int(W5.loc[("ai", "subscription"), "n"]) - int(W5.loc[("ai", "consumable"), "n"]),
    note="rows of Table E.8: non-AI subscriptions 70, AI-feature subscriptions 15, AI subscriptions 28, AI consumables 17 (W5_item_classes.csv; ai_core and ai are the parts of ai_all)")
P.v("147", R2["wave2_item_slopes_n_after"], note="items in the slope sample after the de-duplication")
P.v("60", MIN_STORES_ITEM)
P.w("four", int(W5.loc[("ai_bundle", "subscription"), "n"]), note="the four Microsoft 365 plans (class ai_bundle)")
P.v("13", int(W5.loc[("nonai", "consumable"), "n"]) + int(W5.loc[("ai_feature", "consumable"), "n"]), note="consumables of non-AI (12) and AI-feature (1) apps")
P.cond("130 + 4 + 13 = 147", 130 + int(W5.loc[("ai_bundle", "subscription"), "n"]) + int(W5.loc[("nonai", "consumable"), "n"]) + int(W5.loc[("ai_feature", "consumable"), "n"]) == R2["wave2_item_slopes_n_after"])
P.v("21", N_NONAI)
P.pin("2", why="plan name 'Google AI Plus 2 TB' (storage size)")
_g1 = sl[(sl.app == "googleone") & (sl.name == "Google AI Plus (2 TB)")].iloc[0]
P.v("0.026", float(_g1.slope), note="USD slope of the item 'Google AI Plus (2 TB)' of the Google One app (data/processed/wave2_item_slopes.csv)")
P.v("8", R2["applevel_nonai_localise"])
P.v("21", R2["applevel_nonai_apps"], label="8 of the 21 non-AI apps")
P.v("2", R2["applevel_ai_localise"])
P.v("8", R2["applevel_ai_apps"], label="2 of the 8 AI apps")
P.v("0.10", THR_SLOPE)
P.v("0.67", R2["applevel_fisher_p"])
P.notation()

# -- Table E.9 (tab:benchmarks) and Figure E.1
W2K = pd.read_csv(ROOT / "output" / "tables" / "W2_benchmarks.csv", keep_default_na=False, na_values=[""]).set_index("key")   # the 27 rows of Table E.9
P = S("Within-firm contrasts: income slopes of every monthly subscription of the five firms")
P.w("five", N_STACK_FIRMS, note="the five firms of the stacked regression; Table E.9 (W2_benchmarks.csv) has rows for exactly these firms")
P.cond("Table E.9 covers the five firms of the stacked regression (OpenAI, Google, X Corp, Microsoft, Character.AI) and its 29 rows are the 22 stacked items plus the seven excluded ones",
       W2K.firm.nunique() == N_STACK_FIRMS and len(W2K) == len(STACK_PLANS) + 7 and set(STACK_PLANS) < set(W2K.index), len(W2K))
P = S("\\item \\emph{Notes:} Every monthly subscription item of the five firms listed with a U.S. price in at least 60 storefronts")
P.w("five", N_STACK_FIRMS)
P.v("60", MIN_STORES_ITEM, note="storefronts per item (code/09b_wave2_items.py)")
P.cond("the inclusion rule reproduces the 29 rows of Table E.9 from data/processed/wave2_item_slopes.csv: subscriptions of the nine apps of the five firms with a U.S. price in at least 60 storefronts, "
       "less the annual variants (X Premium, X Premium Basic) and the post-promotion product",
       N_E9_RULE == len(W2K) == 29, N_E9_RULE)
P.dt("16 October 2026", d2)
P.v("167", int(W2K.n.max()), note="largest N of Table E.9 (W2_benchmarks.csv: Character.AI Lite)")
P.v("170", W2_INCOME_SF, note="second-wave storefronts with income data")
P.cond("'Group: the classification of the stacked regression': the group column of W2_benchmarks.csv agrees with STACK for every stacked item, and the excluded items are the storage plans "
       "(group 'storage'), the Google One app's second listing of Google AI Plus (group 'capped_one'), the family variants (group 'family') and X's creator subscription (group 'creator')",
       all(W2K.loc[k, "group"] == STACK_GROUP[k] for k in STACK_PLANS) and sorted(set(W2K.index) - set(STACK_PLANS)) == sorted(STORAGE + SECOND + list(FAMILY) + ["x_creator"])
       and all(W2K.loc[k, "group"] == "storage" for k in STORAGE) and all(W2K.loc[k, "group"] == "capped_one" for k in SECOND)
       and all(W2K.loc[k, "group"] == "family" for k in FAMILY) and W2K.loc["x_creator", "group"] == "creator", len(STACK_PLANS))
P.pin("100", why="name of the item 'Google One 100 GB' (storage size)")
P.pin("2", why="name of the item 'Google AI Plus 2 TB' of the Google One app (storage size)")
P.cond("'the storage plans, the second AI Plus listing and the creator subscription are not localised either': median LMIC price ratio of one and a dollar slope below 0.10 for all four",
       all(W2K.loc[k, "median_ratio_lmic"] == 1 and W2K.loc[k, "slope"] < THR_SLOPE for k in STORAGE + SECOND + ["x_creator"]), W2K.loc["x_creator", "slope"])
P.cond("'each family variant moves with the plan it extends': localised exactly when the extended plan is, with the dollar slope on the same side of 0.10 (YouTube Premium Family / Premium, YouTube Music Family / Music, Microsoft 365 Family / Personal)",
       all((W2K.loc[k, "median_ratio_lmic"] < 0.9) == (W2K.loc[v, "median_ratio_lmic"] < 0.9) and (W2K.loc[k, "slope"] > THR_SLOPE) == (W2K.loc[v, "slope"] > THR_SLOPE) for k, v in FAMILY.items()), len(FAMILY))
P = S("Income slopes of local dollar prices for AI and other products of the same firms, 16 October 2026.")
P.dt("16 October 2026", d2)
P.v("1.96", snorm.ppf(0.975), note="97.5th percentile of the standard normal: the bars are 95% intervals")
P.v("0.033", R2["default_slope"])
P.v("0.10", THR_SLOPE)

# -- Table E.10 (tab:cross_vendor)
S("Relative prices against a common frontier reference, 16 October 2026").dt("16 October 2026", d2)
P = S("\\item \\emph{Notes:} For each plan and storefront, $\\ln$ of the local price relative to the local price of ChatGPT Plus")
P.w("three", N_FRONT_NUM, note="the three $19.99 frontier plans of the numeraire (code/13_relative_prices.py)")
P.v("19.99", FRONTIER_US)
P.v("100", PCT_CONV, note="100 (e^m - 1) percent")
P.v("1", PCT_ONE)
P.wpin("two", "the two comparisons (against ChatGPT Plus and against the frontier median; structural)")
_w10 = pd.read_csv(ROOT / "output" / "tables" / "W10_cross_vendor.csv", keep_default_na=False, na_values=[""])
P.w("three", int((_w10.firm == "Other apps").sum()), note="'three other apps': the rows of Table E.10 outside the five firms, Anthropic and Perplexity (W10_cross_vendor.csv: Super Duolingo, Telegram Premium, Snapchat+)")
P.cond("the rows of Table E.10 are the stacked plans, Anthropic's three plans, the storage and creator items, the three family variants, Perplexity Pro and the three other apps",
       set(_w10.plan) == set(STACK_PLANS) | {"claude_pro", "claude_max5x", "claude_max20x"} | set(E9_EXCLUDED) | {"perplexity_pro"} | set(_w10[_w10.firm == "Other apps"].plan)
       and len(_w10) == len(STACK_PLANS) + 3 + 7 + 1 + 3, len(_w10),
       note="36 rows: 22 stacked plans, Anthropic's 3, the storage (2), second-listing (1), family (3) and creator (1) items, Perplexity Pro and the 3 other apps")
P.notation()

# -- Table E.11 (tab:annual_guard)
P = S("\\item \\emph{Notes:} The five items with the most cells dropped")
P.w("five", len(guard_top), note="items with at least five flagged cells (rows of the table)")
P.v("14", R2["guard_flagged_items"])
P.v("151", R2["guard_flagged_cells"])
P.v("21,938", R2["guard_cells_considered"])
P.w("three", GUARD_K, note="the guard's multiple (GUARD_K of code/09b_wave2_items.py)")
P.cond("the Super Duolingo slope remains negative after the guard", R2["guard_duolingo_super_slope_after"] < 0, R2["guard_duolingo_super_slope_after"])

# -- Table E.12 (tab:stability)
P = S("Local prices of the first-wave plans, 27 September and 16 October 2026")
P.dt("27 September", d1)
P.dt("16 October 2026", d2)
P = S("\\item \\emph{Notes:} A local price is identical when the two listings, in the storefront's own currency, differ by less than 0.5\\%.")
P.w("two", N_WAVES, note="the listings of the two waves")
P.v("0.5", 100 * STAB_TOL, note="stability tolerance of code/09b_wave2_items.py: |a - b| < 0.005 max(a, b)")
P.v("20", MULT_ALLOW[1], note="former plan name ChatGPT Pro 20x")
P.v("1,586", R2["stab_all_compared"])
P.v("1,587", W1_LISTINGS, note="first-wave listings of the ten plans (data/processed/appstore_prices_long.csv, without the '_other' variants)")
P.cond("the one listing not compared is Google AI Ultra in the Philippines (listed in wave 1 only)",
       W1_LISTINGS - R2["stab_all_compared"] == 1 and R2["stab_gemini_ultra_compared"] == int((prices.plan == "gemini_ultra").sum()) - 1
       and "ph" in set(prices[prices.plan == "gemini_ultra"].storefront) and not ((rows2.plan == "gemini_ultra") & (rows2.storefront == "ph")).any())

# -- Table E.13 (tab:tax_absorption)
S("Frontier tiers in U.S.-dollar storefronts whose schedule embeds a tax of more than 5\\%").v("5", 100 * (TAX_EMBED - 1))
S(" & \\multicolumn{3}{c}{All 16 storefronts} & \\multicolumn{2}{c}{Low and lower-middle income} \\\\").v("16", R2["taxabs_n_storefronts"], label="All 16 storefronts (header)")
S("Plan & Storefronts & At U.S. price & Within 3\\% of schedule & Storefronts & At U.S. price \\\\").v("3", 100 * THR_WITHIN)
P = S("\\item \\emph{Notes:} The 16 storefronts priced in U.S. dollars whose tax factor")
P.v("16", R2["taxabs_n_storefronts"])
P.v("1.05", TAX_EMBED)
P.v("0.6", 100 * TAXABS_TOL, note="at the U.S. price: |price in US$ / U.S. price - 1| < 0.006 (code/12_default_panel.py)")
P.v("3", 100 * THR_WITHIN)
P.w("eight", R2["taxabs_gemini_ultra_n"], note="Google AI Ultra is listed in eight of the 16 storefronts")
P.v("16", R2["taxabs_n_storefronts"], label="eight of the 16")
P.v("15", R2["taxabs_supergrok_n"])
P.w("Ten", R2["taxabs_n_lmic_storefronts"], note="low- and lower-middle-income storefronts among the 16 (taxabs_n_lmic_storefronts)")
P.v("16", R2["taxabs_n_storefronts"], label="Ten of the 16 storefronts")
P.wpin("two", "the last two columns of the table (structural)")
P.cond("the generator writes the two LMIC columns (n_lmic, at_us_lmic) for every plan of W13_tax_absorption.csv",
       set(pd.read_csv(ROOT / "output" / "tables" / "W13_tax_absorption.csv").columns) >= {"n_lmic", "at_us_lmic"}, 2)
P.v("16", R2["round_usd16_both25_n"], label="In all 16 storefronts the two $20.00 plans ... at $25.00")
P.w("two", int((W1.loc[FRONT13, "us_price"] == 20.00).sum()), note="the two $20.00 plans of different vendors: Claude Pro and Perplexity Pro")
P.v("20.00", us2["perplexity_pro"], note="U.S. price of Perplexity Pro (and Claude Pro)")
P.v("25.00", float(_same20_tax.claude_pro.round(2).mode().iloc[0]), note="the common price of the two plans in the 16 taxed dollar storefronts (round_usd16_both25_n = 16)")
P.cond("both plans are listed at $25.00 in every one of the 16 storefronts", R2["round_usd16_both25_n"] == R2["round_usd16_n"] == R2["taxabs_n_storefronts"])
P.wpin("two", "'two vendors' decisions': Anthropic and Perplexity, the vendors of the two $20.00 plans (structural)")

# -- Table E.14 (tab:weak_storefronts)
S("Storefronts in which the estimated schedule is weak at the \\$19.99 price point").v("19.99", FRONTIER_US)
P = S("\\item \\emph{Notes:} Upper block: the six lower-income storefronts in which no price point")
P.w("six", len(WEAK6), note="the upper block: in, br, eg, ug, ng, tr (code/14_default_validation.py)")
P.v("19.99", FRONTIER_US, note="the $19.99 price point of the frontier plans")
P.w("six", len(re.findall(r'\("([a-z]{2})", 2\)', SRC14)), note="the lower block: six emerging-market storefronts (block 2 of WEAK)")
P.w("three", MIN_ITEMS_POINT, note="ladder points need at least three items")
P.w("half", MODE_SHARE)
P.v("0.2", THR_CLEAN)

# -- Table E.15 (tab:vintage)
S("Vintage test: deviations from the estimated schedule and exchange-rate movements since March 2024").dt("March 2024", FX_DATES[0])
S(" & & \\multicolumn{2}{c}{Slope on $\\ln$ GNI (s.e.)} & \\multicolumn{2}{c}{Coefficient on FX range (s.e.)} & Median & Within 3\\% (\\%): \\\\").v("3", 100 * VINT_BAND)
P = S("\\item \\emph{Notes:} Deviation $=\\ln$(local price / schedule reference). FX range:")
P.w("six", R2["vint_fx_dates"])
P.dt("6 March 2024", FX_DATES[0], note="first snapshot (data/raw/fx_hist/usd_2024-03-06.json)")
P.dt("15 October 2026", FX_DATES[-1], note="last snapshot (usd_2026-10-15.json)")
P.pin("3", "4", "5", "6", why="column numbers of Table E.15")
P.w("ten", len(VINT_FRONT), note="frontier plans pooled")
P.w("ten", len(VINT_FRONT), note="ten rows per storefront")
P.v("0.0014", R2["vint_frontier_slope"], label="pooled slope, clustered by storefront (negative)")
P.v("0.0028", R2["vint_frontier_se_sf"], label="storefront-clustered s.e. of the pooled slope")
P.v("0.0074", R2["vint_frontier_slope_ctrl"], label="pooled slope with the FX control, clustered by storefront (negative)")
P.v("0.0066", R2["vint_frontier_se_ctrl_sf"], label="its storefront-clustered s.e.")
P.v("0.403", R2["vint_frontier_coef_fx"], label="coefficient on the FX range (storefront-clustered row)")
P.v("0.330", R2["vint_frontier_se_fx_sf"])
P.v("0.542", R2["vint_frontier_absdev_fx"], label="absolute deviation on the FX range (storefront-clustered row)")
P.v("0.233", R2["vint_frontier_absdev_fx_se_sf"])
P.v("0.0014", R2["vint_frontier_slope"], label="pooled slope, clustered by currency (negative)")
P.v("0.0031", R2["vint_frontier_se_cl"])
P.v("0.0074", R2["vint_frontier_slope_ctrl"], label="pooled slope with the FX control, clustered by currency (negative)")
P.v("0.0074", R2["vint_frontier_se_ctrl_cl"], label="its currency-clustered s.e.")
P.v("0.403", R2["vint_frontier_coef_fx"], label="coefficient on the FX range (currency-clustered row)")
P.v("0.341", R2["vint_frontier_se_fx_cl"])
P.v("0.542", R2["vint_frontier_absdev_fx"], label="absolute deviation on the FX range (currency-clustered row)")
P.v("0.240", R2["vint_frontier_absdev_fx_se_cl"])
P.v("3", 100 * VINT_BAND, label="within 3% of the schedule")
P.v("10", 100 * (FX_STABLE - 1), note="stable: moved by at most 10%")
P.v("30", 100 * (FX_MOVED - 1), note="moved: by more than 30%")
P.w("ten", MIN_CLASS, note="'--' for a class with fewer than ten rows (MIN_CLASS of code/41_tables_wave2.py)")
P.notation()

# ================================================================================================ Appendix F: the ChatGPT Go rollout
RS = roll["spec"]
C1_ISO, C2_ISO = RS["cohorts"]["C1"], RS["cohorts"]["C2"]
MSW = [w for w in roll["windows"] if w["source"] == "ms"]           # H1-H2 2025, H2 2025-Q1 2026, Q1-Q2 2026
AUW = [w for w in roll["windows"] if w["source"] == "aui"]          # Aug-Nov 2025, Nov 2025-Feb 2026, Feb-May 2026
ROB = pd.DataFrame(roll["robustness"])
SIGNS = roll["c2_signs"]
ROLL_SRC = (ROOT / "extensions" / "go_rollout_analysis.py").read_text()
N_DRAWS = int(grab(ROLL_SRC, r"for _ in range\((\d+)\)\]\)", "number of random groups"))              # permutation draws
FIG_BASE = int(grab((ROOT / "extensions" / "figure_rollout.py").read_text(), r"v / v\[0\] \* (\d+)", "index base of Figure F.1"))
HALF_PER_YEAR = {"h": 2, "q": 4}[MS_COLS[1][3]]                                                       # H2 2025 is a half-year window
H2_END = pd.Timestamp(year=int(MS_COLS[1][-4:]), month=12, day=31)                                    # the half-year ends on 31 December
MONTH_DAYS = 365.25 / 12


def rdate(iso):
    return ro.loc[ro.iso3 == iso, "date"].iloc[0]


def exposure_months(ts):
    """months from the arrival of the tier to the end of the second half-year of 2025"""
    return (H2_END - ts).days / MONTH_DAYS


c3 = ro[ro.cohort == "C3"].iloc[0]
N_C3 = int(re.match(r"(\d+) further", c3.country).group(1))                    # economies of the 14 October 2025 step
c4 = ro[ro.cohort == "C4"]
c4_eu = c4[c4.iso3 != "BRA"]
c6 = ro[ro.cohort == "C6"].iloc[0]
c2 = ro[ro.iso3.isin(C2_ISO)]
free_months = int(re.search(r"free for (\d+) months", ro.loc[ro.iso3 == "IND", "note"].iloc[0]).group(1))
free_from = pd.Timestamp(re.search(r"from (\d{4}-\d\d-\d\d)", ro.loc[ro.iso3 == "IND", "note"].iloc[0]).group(1))
AWIN = {r.release: (pd.Timestamp(r.date_start), pd.Timestamp(r.date_end)) for r in aei_win.itertuples()}        # first window of each release
AWIN_2026 = sorted(pd.Timestamp(r.date_start) for r in aei_win[aei_win.release == "release_2026_06_26"].itertuples())          # April and May 2026
_fe = lambda src, k: ROB[(ROB.window == (MSW if src == "ms" else AUW)[k]["window"]) & (ROB.variant == "region_fe")].iloc[0]

P = S("OpenAI's release notes and press reports date the arrival of ChatGPT Go in India")
day_month_is(P, rdate("IND"), "19", "August", "2025", note="India, first_available in the rollout record")
day_month_is(P, rdate("IDN"), "22", "September", "2025", note="Indonesia")
P.w("sixteen", len(C2_ISO), note="economies of cohort C2 in the rollout record")
day_month_is(P, c2.date.iloc[0], "8", "October", "2025", note="cohort C2")
_names = re.split(r", | and ", re.search(r"\(8 October 2025: (.*?)\)", P.text).group(1))
P.cond("the sixteen economies named in the text are the sixteen of cohort C2 of the rollout record (all dated alike)",
       len(_names) == len(C2_ISO) and c2.date.nunique() == 1 and all(any(c.startswith(n) for c in c2.country) for n in _names), len(_names))
P.v("71", N_C3, note="economies of the 14 October 2025 step ('71 further countries' in the rollout record)")
day_month_is(P, c3.date, "14", "October", "2025", note="cohort C3")
day_month_is(P, rdate("BRA"), "28", "October", note="Brazil")
P.w("eight", len(c4_eu), note="European economies of cohort C4")
P.cond("the eight European economies share one date", c4_eu.date.nunique() == 1, c4_eu.date.nunique())
day_month_is(P, c4_eu.date.iloc[0], "30", "October", note="European economies of cohort C4")
day_month_is(P, c6.date, "16", "January", "2026", note="worldwide rollout (cohort C6)")
P.w("twelve", free_months, note="months of the free offer in India (rollout record, note on India)")
day_month_is(P, free_from, "4", "November", "2025", note="start of the free offer in India (rollout record)")
P.sub("Perplexity Pro (from July 2025", ")").dtpin("July 2025", why="start of the Airtel bundle with Perplexity Pro: press report, no pipeline record")
P.sub("Google AI Pro (from October 2025", ")").dtpin("October 2025", why="start of the Jio bundle with Google AI Pro: press report, no pipeline record")
P.wpin("ninefold", "rise in Perplexity's downloads in India reported by app-analytics firms (press report)")

# -- the windows and the specification
P = S("Against these dates the public indicators offer four semi-annual or quarterly windows of any use")
P.w("four", len(MS_COLS), note="Microsoft periods: panel columns " + ", ".join(MS_COLS))
P.v("2025", int(MS_COLS[0][-4:]), label="H1 2025")
P.cond("H1 2025 ends before any rollout (before the first arrival date of the rollout record)", pd.Timestamp(year=int(MS_COLS[0][-4:]), month=6, day=30) < ro.date.min(), 0)
P.v("2025", int(MS_COLS[1][-4:]), label="H2 2025")
P.w("sixteen", len(C2_ISO))
P.v("2.8", exposure_months(c2.date.iloc[0]), note="cohort C2: months from 8 October to 31 December 2025 (days / 30.44)")
P.v("4.4", exposure_months(rdate("IND")), note="India: months from 19 August to 31 December 2025")
P.cond("Indonesia's exposure lies inside the printed range 2.8-4.4 months", exposure_months(c2.date.iloc[0]) <= exposure_months(rdate("IDN")) <= exposure_months(rdate("IND")), exposure_months(rdate("IDN")))
P.v("2.6", exposure_months(c3.date),
    note="'most others for at most 2.6': the longest exposure among the economies outside the two early cohorts is that of the 71 economies of "
         "14 October 2025: %d days = %.2f months by 31 December (days / 30.44, the rule that gives 2.8 and 4.4 above); Brazil and the eight European "
         "economies %.2f and %.2f, the economies without a date (C5, dated 1 November in the record, 'dates not published') less"
         % ((H2_END - c3.date).days, exposure_months(c3.date), exposure_months(rdate("BRA")), exposure_months(c4_eu.date.iloc[0])),
    label="most others for at most 2.6 months")
P.cond("the 71 economies of 14 October 2025 are the earliest arrivals outside the two early cohorts (C1, C2), so that no other economy was exposed longer",
       ro[~ro.cohort.isin(["C1", "C2"])].date.min() == c3.date, (H2_END - c3.date).days)
P.v("2026", int(MS_COLS[2][-4:]), label="Q1 and Q2 2026")
P.cond("Q1 and Q2 2026 are the last two Microsoft periods", MS_COLS[2][-4:] == MS_COLS[3][-4:], 0)
P.w("five", len(aui_n), note="windows of the Anthropic index: Aug 2025, Nov 2025, Feb 2026, Apr 2026, May 2026 (three change windows plus the two last)")
_mw = re.search(r"\((\d+)--(\d+) ([A-Z][a-z]+) (\d{4}), before India's launch; (\d+)--(\d+) ([A-Z][a-z]+) (\d{4}); ([A-Z][a-z]+), ([A-Z][a-z]+) and ([A-Z][a-z]+) (\d{4})\)", P.text)
(_a0, _a1), (_n0, _n1), (_f0, _f1) = AWIN["release_2025_09_15"], AWIN["release_2026_01_15"], AWIN["release_2026_03_24"]
P.dt(f"{_mw.group(1)}--{_mw.group(2)} {_mw.group(3)} {_mw.group(4)}", _a0, _a1, note="sample window of the release of 15 September 2025")
P.cond("the August window ends before India's launch", _a1 < rdate("IND"), 0)
P.dt(f"{_mw.group(5)}--{_mw.group(6)} {_mw.group(7)} {_mw.group(8)}", _n0, _n1, note="sample window of the release of 15 January 2026")
P.dt(_mw.group(9), _f0, note="window of 5-12 February 2026")
P.dt(_mw.group(10), AWIN_2026[0], note="calendar month of the June 2026 release")
P.dt(f"{_mw.group(11)} {_mw.group(12)}", AWIN_2026[1], note="calendar month of the June 2026 release")
P.w("sixteen", len(C2_ISO))
P.w("sixteen", len(C2_ISO))
P.w("sixteen", len(C2_ISO))

# -- Table F.1 header
S(" & \\multicolumn{2}{c}{Later-exposed comparison econ.} & \\multicolumn{2}{c}{India} & \\multicolumn{2}{c}{Sixteen Asian economies}").w("Sixteen", len(C2_ISO))

# -- Table F.1 notes
P = S("\\item Notes: $\\Delta\\ln$ is the change in the log indicator between the two windows;")
P.wpin("two", "the pre and the post window of a change (structural)")
P.dt("February", _f0, note="February-May 2026 row: from the February 2026 window")
P.dt("May 2026", AWIN_2026[1], note="to May 2026")
P.dt("May 2026", AWIN_2026[1], note="the published May 2026 index")
P.w("two", len(RS["cohorts"]), note="cohorts C1 and C2 of the rollout specification")
P.v("71", N_C3)
day_month_is(P, c3.date, "14", "October", "2025", note="cohort C3")
P.w("nine", len(c4), note="Brazil and the eight European economies of 28-30 October")
P.dt("28--30 October", c4.date.min(), c4.date.max(), note="Brazil (28 October) and the eight European economies (30 October)")
P.w("sixteen", len(C2_ISO))
P.v("2,000", N_DRAWS, note="random groups of the permutation test (extensions/go_rollout_analysis.py)")
P.w("sixteen", len(C2_ISO))
P.v("11", MSW[0]["C2_n"], note="Asian economies with country-specific Microsoft estimates")
P.cond("the number is 11 in all three any-use windows", all(w["C2_n"] == MSW[0]["C2_n"] for w in MSW), MSW[0]["C2_n"])
P.v("14", AUW[0]["C2_n"], label="Aug-Nov 2025")
P.v("14", AUW[1]["C2_n"], label="Nov 2025-Feb 2026")
P.v("9", AUW[2]["C2_n"], label="Feb-May 2026")
P.v("0.017", MSW[0]["IDN_resid"], note="Indonesia, any use, H1-H2 2025")
P.v("0.006", MSW[1]["IDN_resid"])
P.v("0.010", MSW[2]["IDN_resid"])
P.v("0.307", AUW[0]["IDN_resid"], note="Indonesia, Claude activity")
P.v("0.592", AUW[1]["IDN_resid"])
P.v("0.205", AUW[2]["IDN_resid"])
P.notation()

# -- Figure F.1 caption
P = S("Usage indicators around the first rollouts of ChatGPT Go. (a) Microsoft AI User Share indexed to H1 2025 = 100")
P.v("2025", int(MS_COLS[0][-4:]), label="H1 2025")
P.v("100", FIG_BASE, note="index base of figure_rollout.py: v / v[0] * 100")
P.dt("August 2025", T_AUG, note="first Anthropic window (4-11 August 2025)")
P.v("100", FIG_BASE)
P.w("eleven", MSW[0]["C2_n"], note="Asian economies with country-specific Microsoft estimates")
P.w("sixteen", len(C2_ISO))
P.w("five", len(aui_n), note="windows of the Anthropic index")
day_month_is(P, rdate("IND"), "19", "August", "2025", note="India")
day_month_is(P, free_from, "4", "November", note="start of the free offer")
day_month_is(P, rdate("IDN"), "22", "September", note="Indonesia")
P.w("sixteen", len(C2_ISO))
day_month_is(P, c2.date.iloc[0], "8", "October", note="cohort C2")
P.v("71", N_C3)
day_month_is(P, c3.date, "14", "October", "2025", note="cohort C3")
day_month_is(P, c6.date, "16", "January", "2026", note="worldwide rollout")
P.notation()

# -- the record
P = S("The record shows the following.")
w0, w1, w2 = MSW
a0, a1, a2 = AUW
pct = lambda x: 100 * (math.exp(x) - 1)                      # percentage change implied by a log difference
P.w("half", 1 / HALF_PER_YEAR, note="H2 2025 is a half-year window (panel column ms_h2_2025)")
P.w("sixteen", len(C2_ISO))
P.cond("the 71 economies received the tier a week after the sixteen (6 days)", 5 <= (c3.date - c2.date.iloc[0]).days <= 8, (c3.date - c2.date.iloc[0]).days)
P.v("71", N_C3)
P.wpin("two to three months", "the remaining economies are dated only as 'before the worldwide rollout of 16 January 2026' (cohort C5 undated; 3.3 months after 8 October)")
P.v("0.021", _fe("ms", 0).C2_coef, note="any-use contrast with region fixed effects, H1 to H2 2025")
P.v("0.020", _fe("ms", 0).C2_se)
P.v("0.140", _fe("aui", 1).C2_coef, note="Claude contrast with region fixed effects, Nov 2025 to Feb 2026 (negative)")
month_year_is(P, _n0, "November", "2025", note="Nov 2025 window")
month_year_is(P, _f0, "February", "2026", note="Feb 2026 window")
P.v("0.126", _fe("aui", 1).C2_se)
P.cond("neither region-FE contrast is distinguishable from zero (p > 0.05), and the later windows are smaller still in absolute value",
       _fe("ms", 0).C2_p > 0.05 and _fe("aui", 1).C2_p > 0.05 and abs(_fe("ms", 1).C2_coef) < abs(_fe("ms", 0).C2_coef) and abs(_fe("ms", 2).C2_coef) < abs(_fe("ms", 0).C2_coef),
       _fe("aui", 1).C2_p)
P.v("0.024", w0["C2_coef"])
P.v("0.010", w0["C2_se"])
P.v("2.5", pct(w0["C2_coef"]), note="C2 coefficient 0.0245 as a percentage: 100 (e^d - 1)")
P.v("2,000", N_DRAWS)
P.cond("the contrast is exceeded by as many of the 2,000 random groups as the text says (one)", round(w0["C2_perm_p"] * N_DRAWS) == WORDS[re.search(r"exceeded by (\w+) of 2,000", P.text).group(1)], w0["C2_perm_p"])
P.w("ten", SIGNS["ms|H1 2025 to H2 2025"]["positive"], note="positive residuals among the Asian economies")
P.w("eleven", SIGNS["ms|H1 2025 to H2 2025"]["n"])
P.v("0.180", a1["C2_coef"], label="Claude contrast without region FE (negative)")
P.v("0.063", a1["C2_se"])
P.v("16.5", -pct(a1["C2_coef"]), note="Claude activity of the Asian economies relative to others, Nov 2025 to Feb 2026, as a percentage")
P.w("eleven", SIGNS["aui|Nov 2025 to Feb 2026"]["n"] - SIGNS["aui|Nov 2025 to Feb 2026"]["positive"], note="negative residuals among the Asian economies")
P.w("fourteen", SIGNS["aui|Nov 2025 to Feb 2026"]["n"])
P.v("4.9", pct(w0["IND_resid"]), note="India's residual as a percentage")
P.v("0.048", w0["IND_resid"])
P.v("8", 100 * w0["IND_perm_p"], note="share of economies with an absolute residual at least as large")
P.v("15.3", -pct(a0["IND_resid"]), note="India's Claude activity relative to others, Aug to Nov 2025")
P.dt("August", _a0, note="Aug 2025 window")
month_year_is(P, _n0, "November", "2025", note="Nov 2025 window")
P.v("0.166", a0["IND_resid"])
P.v("39", 100 * a0["IND_perm_p"])
P.cond("Indonesia's residuals are small: below 0.05 in every any-use window", all(abs(w["IDN_resid"]) < 0.05 for w in MSW), max(abs(w["IDN_resid"]) for w in MSW))

P = S("This record does not support a causal interpretation, for reasons the table makes visible.")
P.w("six", (c3.date - c2.date.iloc[0]).days, note="days between the sixteen (8 October) and the 71 economies (14 October 2025)")
P.w("three weeks", round((c4.date.max() - c2.date.iloc[0]).days / 7), note="weeks between 8 October and the European step of 30 October (22 days)")
P.w("sixteen", len(C2_ISO))
P.v("2025", int(MS_COLS[1][-4:]), label="H2 2025")
P.w("six", 12 / HALF_PER_YEAR, note="months of a half-year window")
P.cond("the region fixed effects double the standard errors: the ratio of the region-FE to the baseline s.e. is about 2 for both lead contrasts (2.04 and 2.00)",
       all(abs(_fe(src, k).C2_se / w["C2_se"] - 2) < 0.1 for src, k, w in (("ms", 0, w0), ("aui", 1, a1))), _fe("ms", 0).C2_se / w0["C2_se"])
P.w("two", len(re.split(r" and ", re.search(r"subscribers of ([A-Za-z]+ and [A-Za-z]+) received", TEX[TEX.index("OpenAI's release notes and press reports"):]).group(1))),
    note="the two operators named in the first paragraph of the appendix (Airtel and Jio)")
P.w("half", 1 / HALF_PER_YEAR, note="the only pre-period of the any-use series is H1 2025, a half-year")

# ================================================================================================ Appendix G: a protocol for recording access conditions
P = S("A recurring fee does not determine the cost of completing useful work")
P.dtpin("29 September 2026", why="date of the tariff change (vendor release notes)")
_t = re.search(r"tariff change of (\d+) ([A-Z][a-z]+) (\d{4})", P.text)
P.cond("the vendor pages that document the tariff change (extensions/pricing_sources/manifest.json) were retrieved on the printed date",
       MAN_DATES == [iso_of(_t.group(1), _t.group(2), _t.group(3))], len(MAN_DATES),
       note="retrieval date of the archived vendor pages; the date of the vendor's announcement is pinned")
P.cond("the field dictionary named in the text is shipped with the package", (ROOT / "checks" / "access_measurement_fields.csv").exists(), 0)
P = S("\\item Notes: The present audit observes the first three groups for the App Store channel")
_grp = [l.split(" & ")[0] for l in TEX[TEX.index("Group & Fields"):TEX.index("\\bottomrule", TEX.index("Group & Fields"))].split("\n")[1:] if " & " in l]
_gm = re.search(r"the (\w+) and (\w+) groups are documented", P.text)
P.cond("Table G.1 lists five groups: the first three are observed by the App Store audit, the last two (entitlement and access) are documented from vendor pages",
       len(_grp) == 5 and _grp[3].lower().startswith(_gm.group(1)) and _grp[4].lower().startswith(_gm.group(2)), len(_grp))
P.w("three", len(_grp) - len(_gm.groups()), note="groups of Table G.1 less the two documented from vendor pages")
# ===LEDGER END===


# ================================================================================================ coverage and report
all_tokens = [(m.start(), m.group(0)) for m in TOKEN.finditer(MASKED)]


for p, t in all_tokens:
    if p not in COVER and auto_label(p, t):
        COVER[p] = "label"
for a_, b_ in MATH:                                    # single digits inside equation environments are formula notation
    if TEX.startswith("\\begin{equation}", a_):
        for p, t in all_tokens:
            if a_ <= p < b_ and p not in COVER and re.fullmatch(r"\d", t):
                COVER[p] = "notation"
uncovered = [(p, t) for p, t in all_tokens if p not in COVER]
stats = {k: sum(1 for p, t in all_tokens if COVER.get(p) == k) for k in ("value", "pin", "open", "notation", "label")}

word_hits = []
for w_ in SCAN_WORDS:
    for m in re.finditer(r"(?<![A-Za-z\\])" + w_ + r"(?![A-Za-z])", MASKED, re.I):
        word_hits.append((m.start(), m.group(0)))
uncovered_words = [(p, t) for p, t in word_hits if not any(p + k in COVERW for k in range(len(t)))]

month_hits = [(m.start(), m.group(1)) for m in re.finditer(r"(?<![A-Za-z\\])(" + _MONTH_NAMES + r")(?![A-Za-z])", MASKED)]
uncovered_months = [(p, t) for p, t in month_hits if p not in COVERM]

n_fail = sum(1 for e in LEDGER if e["status"] == "FAIL")
n_open = sum(1 for e in LEDGER if e["status"] == "open")
n_mismatch = n_fail + (n_open if ARGS.strict else 0)
n_unacc = len(uncovered) + len(uncovered_words) + len(uncovered_months)
kinds = {k: sum(1 for e in LEDGER if e["kind"] == k) for k in ("value", "word", "date", "cond", "pin", "text", "open", "anchor")}
cov_fail = n_unacc > 0 and not ARGS.no_coverage

print(f"  {kinds['value']} printed numbers compared with a pipeline value, {kinds['word']} number words, {kinds['date']} dates, "
      f"{kinds['cond']} conditions, "
      f"{kinds['pin']} numbers pinned to the text (no pipeline value can exist), {kinds['text']} text snippets, "
      f"{n_open} unresolved entries")
print(f"  coverage of the prose: {len(all_tokens)} numerals in {len(MASKED.splitlines())} lines "
      f"({stats['value']} compared, {stats['pin']} pinned, {stats['open']} unresolved, {stats['label']} names and labels, "
      f"{stats['notation']} notation); "
      f"{len(uncovered)} numerals, {len(uncovered_words)} number words and {len(uncovered_months)} month names unaccounted for; "
      f"{len(word_hits)} scanned number words, {len(month_hits)} month names")
for e in LEDGER:
    if e["status"] == "FAIL":
        print(f"  MISMATCH  {e['loc']}: printed {e['printed']!r}, pipeline value {e['value']!r} {e['note']}")
for p, t in uncovered:
    print(f"  UNACCOUNTED NUMERAL  line {lineno(p)}: " + re.sub(r"\s+", " ", f"{TEX[max(0, p - 40):p]}[[{t}]]{TEX[p + len(t):p + len(t) + 30]}"))
for p, t in uncovered_words:
    print(f"  UNACCOUNTED NUMBER WORD  line {lineno(p)}: " + re.sub(r"\s+", " ", f"{TEX[max(0, p - 40):p]}[[{t}]]{TEX[p + len(t):p + len(t) + 30]}"))
for p, t in uncovered_months:
    print(f"  UNACCOUNTED MONTH NAME  line {lineno(p)}: " + re.sub(r"\s+", " ", f"{TEX[max(0, p - 40):p]}[[{t}]]{TEX[p + len(t):p + len(t) + 30]}"))
if ARGS.list_open or n_open:
    for e in LEDGER:
        if e["status"] == "open":
            print(f"  {'MISMATCH (unresolved entry)' if ARGS.strict else 'UNRESOLVED'}  {e['loc']}: printed {e['printed']!r}, pipeline {e['value']!r}  {e['note']}")
if ARGS.list_pins:
    for ln, tok, why in sorted(PINS):
        print(f"  PIN  line {ln}: {tok}  ({why})")
print(f"  runtime {time.time() - T0:.1f} s")
if n_open and not ARGS.strict:
    print(f"  {n_open} unresolved entries: printed numbers that the pipeline does not reproduce under the literal reading of their sentence "
          f"(listed above); they are not counted as mismatches without --strict")
if cov_fail:
    print(f"  COVERAGE FAILURE: {n_unacc} numerals, number words or month names of the prose are accounted for by no check")
print(f"{len(LEDGER)} checks, {n_mismatch} mismatches")
sys.exit(1 if (n_mismatch or cov_fail) else 0)
