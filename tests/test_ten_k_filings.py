import pandas as pd
from pathlib import Path

from volatility_from_text.data.filings import ten_k_filings


FIXTURES = Path(__file__).parent / "fixtures"

def test_ten_k_filings_keeps_only_10k_in_range() -> None:
    """
    Check that `ten_k_filings` keeps only 10-K filings inside the date range.
    """
    out = ten_k_filings(
        ciks=pd.Series([1]), 
        companies=pd.Series(["Test Co"]),
        tickers=pd.Series(["TST"]), 
        sectors=pd.Series(["Technology"]),
        route=FIXTURES, 
        start="2010-01-01", 
        end="2019-12-31",
    )

    assert list(out["accessionNumber"]) == ["0000000001-15-000001"]