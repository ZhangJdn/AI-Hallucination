# Notes

## Apple (CIK 0000320193), 10-Q for the quarter ending 2026-06-27

Filing: https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/

What the XBRL JSON says (from data/raw/companyfacts_0000320193.json):

| Field | Tag | JSON val (3-month quarter) |
|---|---|---|
| revenue | RevenueFromContractWithCustomerExcludingAssessedTax | 109,417,000,000 |
| net income | NetIncomeLoss | 29,789,000,000 |
| diluted EPS | EarningsPerShareDiluted | 2.02 |

What the filing says (aapl-20260627.htm, Condensed Consolidated Statements of Operations):

Header note: "In millions, except number of shares, which are reflected in thousands, and per-share amounts"

| Field | Name in the filing | Number in the table | Units | Matches JSON? |
|---|---|---|---|---|
| revenue | Total net sales | 109,417 | millions | yes (109,417 x 1,000,000) |
| net income | Net income | 29,789 | millions | yes |
| diluted EPS | Diluted (earnings per share) | 2.02 | per share, not scaled | yes |

The statement has four columns:

| | 3 months to 2026-06-27 | 3 months to 2025-06-28 | 9 months to 2026-06-27 | 9 months to 2025-06-28 |
|---|---|---|---|---|
| Total net sales | 109,417 | 94,036 | 364,357 | 313,695 |
| Net income | 29,789 | 23,434 | 101,464 | 84,544 |
| Diluted EPS | 2.02 | 1.57 | 6.88 | 5.62 |
| Diluted shares (thousands) | 14,714,676 | 14,948,179 | 14,750,302 | 15,051,726 |

The JSON value matched column 1 (current quarter) every time.

## Things I've noticed so far

- Apple has three revenue tags. "SalesRevenueNet" was used until 2018, "Revenues" only for 2016-2018, and "RevenueFromContractWithCustomerExcludingAssessedTax" from 2017 on. explore.py first grabbed the old "Revenues" tag and found zero recent quarters. Fixed it to pick whichever tag has the newest data.
  - Rule: for each field, keep a list of possible tags and use the one with the latest data.
- The same 10-Q has two entries for net income ending 2026-06-27:
  - start 2026-03-29: 29,789,000,000 (the 3-month quarter)
  - start 2025-09-28: 101,464,000,000 (9 months year-to-date)
  - Rule: check start and end dates. About 90 days means the quarter.
- NetIncomeLoss has 341 entries in total but only 22 distinct quarters from 10-Qs. Every filing repeats older periods for comparison.
  - Rule: dedupe. Entries with a "frame" field are one per period.
- EPS unit is "USD/shares", not "USD". It's per-share and not scaled.

- Three different scales in one table: dollars in millions, shares in thousands, EPS as-is. A model has to apply the right one per row.
  - Rule: model returns the number as written plus a scale. Code does the multiplying, so scale mistakes show up as their own error type.
- The filing calls revenue "Total net sales", not "revenue". Other companies will use other names.
  - Rule: the prompt should describe fields by meaning ("total revenue / net sales for the period"), not by one label.
- Each row has 4 numbers next to each other, and only one is right. The 9-month YTD column and last year's column are the obvious wrong answers. This is a built-in distractor test.
  - Rule: the prompt says which period to extract (the most recent 3-month quarter). Picking the wrong column gets scored as a wrong value.
- Sanity check that works: net income / diluted shares = 29,789M / 14,714.676M = 2.0244, which rounds to the reported EPS of 2.02. Same for last year: 23,434 / 14,948.179 = 1.568, reported 1.57.
  - Could be a validation rule for the cascade: if the model's EPS is far from net income / shares, escalate.
- Last year's quarter (94,036 / 23,434 / 1.57) also appears in this filing. That's why the JSON has so many duplicate entries.

