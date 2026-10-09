# ChatGPT Go rollout record

`chatgpt_go_rollout.csv` records, by country, the date on which OpenAI's ChatGPT Go tier first became available, as far as
public sources document it (compiled 8 October 2026). Columns: ISO3 code (blank for a batch whose country list was not
published), country, first availability date, cohort (C1 India and Indonesia; C2 the 16-country Asian expansion of
8 October 2025; C3 the 71-country expansion of 14 October 2025, whose list OpenAI did not publish; C4 Brazil and eight
European countries, 28–30 October 2025; C5 further countries added before 16 January 2026, undated; C6 the worldwide rollout
of 16 January 2026), a note, and the sources. The India promotion (12 months of Go at no charge from 4 November 2025) is
noted on the India row.

Only cohorts C1, C2, C4 and C6 have documented country lists. The analysis in `extensions/go_rollout_analysis.py`
therefore compares the documented early-access economies (C1 and C2) with all other economies, and treats the comparison
group as partly exposed from mid-October 2025.
