## ATLAS v1.0 Data Documentation

This documentation accompanies the data provided at
[ai.google/economy/atlas](http://ai.google/economy/atlas) and released alongside
the
[Atlas v1.0 report](https://ai.google/static/documents/GoogleATLASv1.pdf)`.`The
data is based on a sample of user interactions from Gemini App, Google AI Mode,
and Gemini API in April 2026\. See the full report and the methodology section
of this site for additional details.

### Archive Contents

`atlas_v1_public_data.zip` \
`├── README.md` \
`├── atlas_v1_work_occupations.csv` \
`├── atlas_v1_geography_intensity.csv` \
`└── atlas_v1_household_activities.csv`

Each section below details the fields contained in the datasets associated with
the visualizations on this site related to occupational and task metrics,
household time use, and geographic adoption and intensity. Further detail on the
complete analyses related to these topics can be found in the
[Atlas v1.0 report](https://ai.google/static/documents/GoogleATLASv1.pdf). All
data contained here has had differential privacy applied in the manner described
in the \[methodology\](link) section. Groupings with insufficient data have been
suppressed and statistical noise may influence the exact figures included in the
data.

### Occupational & Task Metrics (`atlas_v1_work_occupations.csv`)

Work-related interactions are mapped to the O\*NET 30.2 task taxonomy and 2018
Standard Occupational Classification (SOC) Occupations. Certain fields are made
available for Broad occupations while others are only provided at the Major
occupation group level. (*Note: usage shares in* `percentage_of_total` *at the
Broad occupation level will not aggregate to the Major occupation shares for the
US, OECD, or Non-OECD groupings reported in the paper. This stems from the
exclusion of “All Other” Detailed occupations when calculating the Broad
occupation shares reported here. See further discussion in the report.)*

Within occupations, task saturation is measured as the share of associated
O\*NET tasks where at least some minimum number of distinct users are observed.
The measure in this dataset, `non_negligible_ai_use` and `intensive_ai_use`
reflect task saturation measured with lower and higher user count thresholds.
Task saturation is an occupation-level metric and is thus reported exclusively
at the Global level (left unpopulated on U.S. rows). Additionally,
`full_automation_pct` captures the estimated proportion of work interactions
where users requested end-to-end task execution rather than iterative
co-piloting. Full task mapping and classifier validation details are documented
in Section 3 of the
[ATLAS 1.0 Report](https://ai.google/static/documents/GoogleATLASv1.pdf).

(*Note: The exact definitions of non-negligible and intensive AI use are
particular to our current sample. We may update these in future iterations of
ATLAS but intend to provide retroactive measures for consistency if we do.)*

**Unit of Observation**: `(geographic_region, soc_code)`

| Column Name | Type | Description | Values / Range | Availability |
| :--- | :--- | :--- | :--- | :--- |
| geographic_region | string | Geographic scope of the sample | GLOBAL, US | Broad/Major occupations |
| soc_code | string | 2018 Standard Occupational Classification Broad Occupation code | e.g., 15-1250 or 15-0000 | All occupations |
| percentage_of_total | float | Percentage share of total work volume within the geographic scope | 0.00% to 100.00% | Broad occupations, Global/US |
| non_negligible_ai_use | float | Percentage of O*NET tasks with observed AI usage (task saturation) above lower user count threshold (25) in our sample | 0.00% to 100.00% | Broad/Major occupations, Global |
| intensive_ai_use | float | Percentage of O*NET tasks with observed AI usage (task saturation) above higher user count threshold (100) in our sample | 0.00% to 100.00% | Broad/Major occupations, Global |
| saturation_tier | int | (Non-negligible) task saturation quintile (1 = lowest, 5 = highest). | 1 to 5 | Broad occupations, Global |
| full_automation_pct | float | Estimated share of user interactions seeking end-to-end task automation | 0.00% to 100.00% | Major occupations, Global/US |
| non_routine_cognitive_pct | float | Estimated share of user interactions categorized as non-routine cognitive tasks based on Autor and Thompson (2025) (see report for additional discussion) | 0.00% to 100.00% | Major occupations, Global/US |

### Household Time Use (`atlas_v1_household_activities.csv`)

Personal and household interactions are classified into the three-tier American
Time Use Survey (ATUS) taxonomy across major domains (Tier 1), intermediate
clusters (Tier 2), and detailed activities (Tier 3). Activity volume shares
(`request_share`) are measured across 10 weekly time blocks (`week_block`) to
capture temporal usage dynamics (e.g. Monday working hours, Monday-Tuesday
evening, etc.). Full time-use taxonomy crosswalks are detailed in Section 4 of
the [ATLAS 1.0 Report](https://ai.google/static/documents/GoogleATLASv1.pdf).

**Unit of Observation**: `(geographic_region, atus_tier3, week_block)`

| Column Name | Type | Description | Values / Range | Availability |
| :--- | :--- | :--- | :--- | :--- |
| geographic_region | string | Geographic scope | GLOBAL, US | All |
| atus_major | string | ATUS Tier-1 Major Activity Category | e.g., Socializing, Relaxing, and Leisure | All |
| atus_tier2 | string | ATUS Tier-2 Intermediate Activity Category | e.g., Relaxing and Leisure | All |
| atus_tier3 | string | ATUS Tier-3 Detailed Activity Category | e.g., Reading for personal interest | All |
| week_block | string | Time block identifier | Mon Work, Mon-Tue Night, Weekend, etc. | All |
| request_share | float | Percentage share of non-work requests within region | 0.00% to 100.00% | All |

### Geography & Adoption Intensity (`atlas_v1_geography_intensity.csv`)

Adoption intensity (`intensity_quintile`) reflects per-capita AI usage
normalized by World Bank (or IMF, where needed) population data and is adjusted
based on variation in platform penetration and usage intensity using
country-by-country web traffic referral shares. The dataset also reports the
work vs. non-work composition (`work_share_pct`) of conversational AI usage, the
top three interaction languages, and the top three Minor Occupation Groups
(subject to privacy limitations). Top languages are only reported for the top
two usage volume quintiles. Top occupations are suppressed for the lowest usage
volume quintile.

For additional details and discussion, see Section 5 of the
[ATLAS 1.0 Report](https://ai.google/static/documents/GoogleATLASv1.pdf).

**Unit of Observation**: `(geo_id)`

| Column Name | Type | Description | Values / Range | Availability |
| :--- | :--- | :--- | :--- | :--- |
| geo_id | string | ISO 3166-1 alpha-2 country code or US state postal code | e.g., US, IN, CA, IL | All |
| geo_level | string | Geographic aggregation level | country, state | All |
| geo_name | string | English geographic name resolved via CLDR | e.g., United States, India, Illinois | All |
| work_share_pct | float | Percentage share of geographic conversation volume in Work category | 0.00% to 100.00% | All |
| intensity_quintile | int | Per-capita adoption quintile (1 = Very Low, 5 = Very High) | 1 to 5 | Population >= 1M |
| top_language_1 | string | Primary conversation language in entity | e.g., English, Hindi, Spanish | All |
| top_language_1_pct | float | Percentage share of primary language | 0.00% to 100.00% | All |
| top_language_2 | string | Secondary conversation language in entity | e.g., Spanish, French, Arabic | Available if not unobserved/suppressed |
| top_language_2_pct | float | Percentage share of secondary language | 0.00% to 100.00% | Available if not unobserved/suppressed |
| top_language_3 | string | Tertiary conversation language in entity | e.g., German, Bangla, Tagalog | Available if not unobserved/suppressed |
| top_language_3_pct | float | Percentage share of tertiary language | 0.00% to 100.00% | Available if not unobserved/suppressed |
| top_occupation_1 | string | Primary Minor Occupation Group in entity | e.g., Computer and Mathematical Occupations | Available if not unobserved/suppressed |
| top_occupation_1_pct | float | Percentage share of primary occupation | 0.00% to 100.00% | Available if not unobserved/suppressed |
| top_occupation_2 | string | Secondary Minor Occupation Group in entity | e.g., Computer and Mathematical Occupations | Available if not unobserved/suppressed |
| top_occupation_2_pct | float | Percentage share of secondary occupation | 0.00% to 100.00% | Available if not unobserved/suppressed |
| top_occupation_3 | string | Tertiary Minor Occupation Group in entity | e.g., Computer and Mathematical Occupations | Available if not unobserved/suppressed |
| top_occupation_3_pct | float | Percentage share of tertiary occupation | 0.00% to 100.00% | Available if not unobserved/suppressed |

## Citation & Academic Attribution

If you utilize this dataset in academic publications, working papers, policy
reports, or data analyses, please cite the project as follows:

**`@article`**`{iscenko2026googlesaieconomy,` \
`title={Google's AI \& Economy ATLAS v1.0: Mapping Gemini Usage in the
Economy},` \
`author={Iscenko, Zanna and Strand, Scott and Chen, Yiyuan and Aimard,
Guillaume` \
`and Codreanu, Mihai and Sampathkumar, Vivek and Imas, Alex` \
`and Jacobs, Julian and Muiruri, Evalyne and Mateos-Garcia, Juan` \
`and Ng, Jia Jen and Javed, Samirah and Martin, Josh and Ajmeri, Omar` \
`and Calin, Denis and Kim, Andrew and Curto Millet, Fabien` \
`and Manyika, James},` \
`journal={Google Research Technical Report},` \
`year={2026},` \
`url={https://ai.google/static/documents/GoogleATLASv1.pdf}` \
`}`

## Data License & Terms

*   **License**: Released under the **Creative Commons Attribution 4.0
    International (CC-BY 4.0)** license. You are free to share, copy, adapt, and
    build upon this data for academic, commercial, and policy applications,
    provided appropriate attribution is given.
*   **External Taxonomies**:
    *   Standard Occupational Classification (SOC) and American Time Use Survey
        (ATUS) structures courtesy of the **U.S. Bureau of Labor Statistics
        (BLS)**.
    *   O\*NET Database courtesy of the **U.S. Department of Labor, Employment
        and Training Administration (USDOL/ETA)**.
*   **Feedback & Research Collaborations**: Contact the ATLAS research team at
    `ai-econ-leads@google.com`.
