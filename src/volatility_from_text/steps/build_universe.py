import argparse
from pathlib import Path

import pandas as pd
import yaml

from volatility_from_text.data.filings import ten_k_filings
from volatility_from_text.data.prices import check_session, get_prices
from volatility_from_text.data.sec_api import get_json
from volatility_from_text.data.universe import (
    add_ciks, one_report_per_year, select_per_sector, universe_table,
)

BRONZE = Path("data/bronze")
SILVER = Path("data/silver")
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


def main(config_path):
    config = yaml.safe_load(Path(config_path).read_text())
    discards = {"ticker": [], "reason":[]}                                   

    # Candidates with their CIK
    tickers_json = get_json(url = TICKERS_URL, 
                            path = BRONZE / "company_tickers.json")

    candidates = add_ciks(candidates =   config["candidates"], 
                          tickers_json = tickers_json)

    # Beginning and conclusion of the reports' period
    start = config["start"]
    end   = config["end"]

    # Seed for reproducibility
    seed = config["selection"]["seed"]

    # Their 10-K filings
    filings = ten_k_filings(ciks =      candidates["cik"], 
                            companies = candidates["company"], 
                            tickers =   candidates["ticker"],
                            sectors =   candidates["sector"], 
                            route =     BRONZE, 
                            start =     start, 
                            end =       end)
   
    # Filter companies that do not have exactly 1 report each year
    start_year = pd.to_datetime(start).year
    end_year =   pd.to_datetime(end).year

    years = range(start_year, end_year + 1) # range(n, m) goes from n to m-1

    filings, dropped = one_report_per_year(df =                 filings, 
                                           cik_column =         "cik", 
                                           filing_date_column = "filing_date", 
                                           years =              years)

    # Add the dropped ones to discards
    for ticker_dropped in dropped:
        discards["ticker"].append(ticker_dropped)
        discards["reason"].append("one_report_per_year")


    # Get NY sessions (sp500 index fund)
    route_prices = BRONZE / "prices"
    
    start_prices = config["start_prices"]
    end_prices = config["end_prices"]

    sessions = get_prices(ticker = config["market_ticker"], 
                          start =  start_prices, 
                          end =    end_prices,
                          route =  route_prices).index # prices gives the entire dataset, only the dates are needed

    for ticker in filings["ticker"].unique(): # Tickers are repeated each year, just use it once

        # Import prices form yfinance or data/bronze/prices/ticker.parquet 
        df_ticker = get_prices(ticker = ticker, 
                               start=   start_prices, 
                               end =    end_prices,
                               route =  route_prices) 

        # If the ticker has sessions missing or extra compared to `sessions` it is removed
        if not (check_session(df = df_ticker, sessions = sessions)): 
            filings = filings[filings["ticker"] != ticker]

            # Add the discarded ticker
            discards["ticker"].append(ticker) 
            discards["reason"].append("check_session")
    
    # Eliminate n per sector and save
    survivors = select_per_sector(df =       filings, 
                                  n_sample = config["selection"]["per_sector"], 
                                  seed =     seed)
    
    universe = universe_table(survivors)

    # Save the remaining companies
    SILVER.mkdir(parents=True, exist_ok=True)
    universe.to_parquet(SILVER / "universe.parquet", index=False)

    # Save the discarded companies by an error
    discards = pd.DataFrame(discards)
    discards.to_csv(SILVER / "universe_discards.csv", index=False)

    # Final message with the number of companies kept and defective
    print(f"{len(universe)} companies -> {SILVER / 'universe.parquet'} ({len(discards)} discarded)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Config argument to pick between pilot and full project
    parser.add_argument("--config", default="configs/pilot.yaml")
    main(parser.parse_args().config)