"""
explore.py: look at one company's XBRL numbers in a readable table.

Run:   python explore.py
Or:    python explore.py 0000320193     (any CIK, 10 digits)

What it does:
1. Downloads the company's companyfacts JSON from the SEC.
2. Saves the raw JSON to data/raw/ so you can open it later.
3. For each field below, keeps only quarterly 10-Q values and prints
   the last 4, with a link to the filing each one came from.
"""
import json
import sys
from datetime import date
from pathlib import Path

import requests

# The SEC wants a real name and email here. Put yours in.
HEADERS = {"User-Agent": "Jaden student-project jadenzhang1256@gmail.com"}

# Each field can be reported under different tags depending on the company.
# The script uses the first tag the company actually has.
FIELDS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
}


def days_between(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def main():
    cik = sys.argv[1] if len(sys.argv) > 1 else "0000320193"  # Apple
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    data = requests.get(url, headers=HEADERS, timeout=30).json()

    out = Path("data/raw") / f"companyfacts_{cik}.json"
    out.write_text(json.dumps(data, indent=2))
    print(f"{data['entityName']}  (raw JSON saved to {out})\n")

    us_gaap = data["facts"]["us-gaap"]

    for field, tags in FIELDS.items():
        # Pick the tag with the most recent data. Companies switch tags over
        # time (Apple used "Revenues" until 2018), so "first tag found" can
        # land on an old, abandoned one.
        found = [t for t in tags if t in us_gaap]
        tag = max(
            found,
            key=lambda t: max(e["end"] for u in us_gaap[t]["units"].values() for e in u),
            default=None,
        )
        if tag is None:
            print(f"{field}: none of {tags} found for this company\n")
            continue

        units = us_gaap[tag]["units"]
        unit = next(iter(units))  # "USD" for money, "USD/shares" for EPS
        entries = units[unit]

        quarterly = [
            e for e in entries
            if e.get("form") == "10-Q"
            and "start" in e
            and 80 <= days_between(e["start"], e["end"]) <= 100  # about 3 months
            and "frame" in e  # only one entry per period has this, so it dedupes
        ]
        quarterly.sort(key=lambda e: e["end"])

        print(f"{field}  (tag: {tag}, unit: {unit}, "
              f"{len(entries)} total entries, {len(quarterly)} quarterly)")
        for e in quarterly[-4:]:
            accn = e["accn"].replace("-", "")
            link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn}/"
            print(f"  {e['start']} to {e['end']}  {e['fp']} FY{e['fy']}  "
                  f"val={e['val']:,}  filed {e['filed']}")
            print(f"    {link}")
        print()


if __name__ == "__main__":
    main()
