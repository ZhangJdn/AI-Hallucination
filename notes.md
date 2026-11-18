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


## Shake Shack (CIK 0001620533), 10-Q for the quarter ending 2026-09-30

Filing: https://www.sec.gov/Archives/edgar/data/1620533/000162053326000041/shak-20260930.htm

What the XBRL JSON says for this filing:

| Field | Tag | This quarter (2026-07-02 to 2026-09-30) | Same quarter last year (2025-06-26 to 2025-09-24) |
|---|---|---|---|
| revenue | RevenueFromContractWithCustomerExcludingAssessedTax | 423,273,000 | 367,411,000 |
| net income, total | ProfitLoss | 17,767,000 | 13,711,000 |
| minus non-controlling interests | NetIncomeLossAttributableToNoncontrollingInterest | 1,281,000 | 1,210,000 |
| net income attributable to Shake Shack Inc. | NetIncomeLoss | 16,486,000 | 12,501,000 |
| diluted EPS | EarningsPerShareDiluted | 0.39 | 0.30 |
| diluted shares | WeightedAverageNumberOfDilutedSharesOutstanding | 41,910,000 | 41,874,000 |

What the filing says (Condensed Consolidated Statements of Income, page 4):

Header note: "(in thousands, except per share amounts)". Apple was in millions.

Columns: "Thirteen Weeks Ended" Sept 30 2026 / Sept 24 2025, then "Thirty-Nine Weeks Ended" for the same dates. Apple said "Three Months Ended".

| Field | Label in the filing | This quarter | Units | Matches JSON? |
|---|---|---|---|---|
| revenue | TOTAL REVENUE | 423,273 | thousands | yes |
| net income, total | NET INCOME | 17,767 | thousands | yes (ProfitLoss) |
| net income attributable to Shake Shack Inc. | NET INCOME ATTRIBUTABLE TO SHAKE SHACK INC. | 16,486 | thousands | yes (NetIncomeLoss) |
| diluted EPS | Earnings per share of Class A common stock: Diluted | 0.39 | per share | yes |
| diluted shares | Weighted-average shares of Class A common stock outstanding: Diluted | 41,910 | thousands | yes |

Every value matched column 1 again.

### New things Shake Shack showed that Apple didn't

- Two "net income" numbers. Shake Shack has non-controlling interests (part of the business is owned by other people), so the statement shows total net income (17.8M), subtracts the minority share (1.3M), and ends with net income attributable to Shake Shack Inc. (16.5M). NetIncomeLoss is the second one. Apple only had one.
  - Rule: define net_income as "attributable to the company / parent". That's the one EPS is based on.
  - EPS check proves it: 16,486,000 / 41,910,000 = 0.393, matches 0.39. Using the total gives 0.424, which doesn't.
  - This is a great test case: a model that grabs the first "Net income" line gets it wrong.
- explore.py's first line was misleading. It showed 2025-06-26 to 2025-09-24 as "Q3 FY2026, filed 2026-11-05". That's last year's quarter. fy, fp and filed describe the filing the number appeared in, not the period. The "frame" dedupe kept the copy from the newest filing (the 2026 10-Q repeats last year as a comparison column).
  - Rule: don't use frame to build the answer key. For each filing (accn), the gold value is the entry with the latest end date in that filing and a ~90-day period.
- A loss quarter. Q1 2026 net income was -290,000 and EPS -0.01. This filing confirms negatives are printed in parentheses (Interest expense shows as (567)), so the Q1 loss would be (290).
  - Rule: normalize "(290)" to -290 before comparing. Good test of whether models keep the sign.
- No Q4 in the list. Companies file a 10-K for the 4th quarter, not a 10-Q, and the 10-K mostly reports the full year.
  - Rule: only use 10-Q filings, so there are 3 usable quarters per company per year.
- Quarters end on odd dates (2026-04-01, 2026-07-01, 2026-09-30). Shake Shack uses a 52/53-week fiscal year that ends on a Wednesday, not on calendar month-ends.
  - Rule: never assume quarters end on the last day of a month. Always use the dates in the data.
- More distractors than Apple in the same table:
  - Revenue has sub-lines above the total: "Shack sales" 408,026 and "Licensing revenue" 15,247. A model could grab Shack sales.
  - EPS has Basic (0.41) right above Diluted (0.39).
  - The very next statement (Comprehensive Income) starts with "Net income $17,767" again and has "Comprehensive income attributable to Shake Shack Inc." of 16,486 this quarter but 12,504 last year (vs 12,501 net income). Near-identical numbers on a different line.
  - Rule: the gold value is always the line the XBRL tag points to. The documents should include these nearby lines on purpose, since that's what makes the test realistic.
- Different period wording: "Thirteen Weeks Ended" / "Thirty-Nine Weeks Ended" instead of "Three Months" / "Nine Months".
  - Rule: the prompt should say "the most recent quarter (about 13 weeks / 3 months)", not one exact phrase.
- Shares are in thousands here too (41,910 = 41,910,000), same as the dollar amounts, unlike Apple where shares had their own scale.
