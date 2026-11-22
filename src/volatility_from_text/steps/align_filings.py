import argparse
from pathlib import Path

import pandas as pd
import yaml

from volatility_from_text.data.align_filings_to_market import first_tradable_date
from volatility_from_text.data.filings import filings_table, ten_k_filings
from volatility_from_text.data.prices import get_prices

BRONZE = Path("data/bronze")
SILVER = Path("data/silver")


def main(config_path):
    config = yaml.safe_load(Path(config_path).read_text())

    # Companies selected in step 1
    universe = pd.read_parquet(SILVER / "universe.parquet")

    # Their 10-K filings (read from the bronze cache, no new downloads)
    filings = ten_k_filings(ciks=universe["cik"],
                            companies=universe["company"],
                            tickers=universe["ticker"],
                            sectors=universe["sector"],
                            route=BRONZE,
                            start=config["start"],
                            end=config["end"])

    # Market calendar: the trading sessions of the market ticker
    sessions = get_prices(ticker=config["market_ticker"],
                          start=config["start_prices"],
                          end=config["end_prices"],
                          route=BRONZE / "prices").index

    # First session that opens after each acceptance time
    filings["first_tradable_date"] = pd.to_datetime(
        [first_tradable_date(accepted, sessions) for accepted in filings["accepted_at_utc"]]
    )

    table = filings_table(filings)

    # Sanity checks before saving
    assert table["accession_number"].is_unique, "duplicated filings"
    assert (table["first_tradable_date"] >= table["filing_date"]).all(), "tradable before filed"

    table.to_parquet(SILVER / "filings.parquet", index=False)

    differs = (table["first_tradable_date"] != table["filing_date"]).mean()

    print(f"{len(table)} filings -> {SILVER / 'filings.parquet'} ")  
    print(f"({differs:.0%} with first tradable date after the filing date)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/pilot.yaml")
    main(parser.parse_args().config)