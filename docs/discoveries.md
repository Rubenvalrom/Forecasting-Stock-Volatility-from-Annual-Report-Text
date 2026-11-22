# Pilot discoveries

## Findings
The `Z` in the `acceptanceDateTime` field of filings is true UTC, verified against the filing header (Apple 2015: `20:31Z` in the API, `16:31` New York time in the header).

77% of the reports (232 of 300) have a first tradable date later than their `filingDate`, so `filingDate` cannot be used to align filings with prices. The cause is every report accepted between 09:30 and 17:30: 29% were accepted during the session, and the rest after the 16:00 close but before 17:30, when EDGAR still gives the same-day filing date.

`filings.recent` only holds the latest ~1,000 submissions of a company; older ones are in the files listed under `filings.files`.

The ticker `BK` (Bank of New York Mellon) changed to `BNY`: the SEC file only lists current tickers. One `CIK` can have more than one ticker.

All 45 candidates pass every filter: the list was built from companies that exist today, so it has survivorship bias by construction.

## Bottlenecks
With 45 companies, `build_universe.py` takes about 3 minutes the first time (SEC rate limit); with 300 it will take around 20. Later runs read from the cache.

`first_tradable_date` is computed one filing at a time; it should be vectorised for ~3,000 filings.

Yahoo adjusted prices change over time, so they must be frozen before any result is final.

No access to CRSP/WRDS through the university, Yahoo does not guarantee access to delisted companies; therefore introducing survivorship bias.

## Decisions
`CIK` is the id of every table, since it is unique for each company. Tickers are joined from ticker to `CIK`.

A report accepted during the session is assigned to the next one. It is conservative: for those reports the target misses the same-day reaction.

Only `10-K` forms are used; amendments (`10-K/A`) and transition reports (`10-KT`) are excluded.

Because all 45 companies survived the filters, 30 of them (10 per sector) were chosen at random with a fixed seed.

The earnings release (8-K) is not included in the baselines. It is left as a possible robustness check for a later stage.

## Next steps
Volatility target and past-volatility features, moved from the study notebooks to the package with their tests.

Create a function to solve the problem of a `CIK` having multiple `tickers` since yahoo finance will proably only accept one of them.