# Pilot discoveries

## Findings
The `Z` in the `acceptanceDateTime` field of filings is a True UTC.
The ticker `BK` (The Bank of New York Mellon Corporation) had is ticker changed to `BNY`.  

77% of the reports (232 of 300) have a `filingDate` that is not their first tradable date, mostly because they are accepted with the market closed (71% of them), so `filingDate` cannot be used to align filings with prices; `first_tradable_date`, derived from `acceptanceDateTime`, is used instead.

## Bottlenecks
With 45 companies, build_universe.py takes about 3 minutes to execute, with 300 companies it will take around 20 min.

One `CIK`can have more than one ticker.

## Decisions
Since `CIK` is a unique id for each company, it has been also used as the id for the universe table.

Because all 45 companies survived the filters, 30 of them (10 per sector) were chosen at random with a previously setted seed.

# Next Steps

Create a function to solve the problem of a `CIK` having multiple `tickers` since yahoo finance will proably only accept one of them.