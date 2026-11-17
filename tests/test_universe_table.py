import pandas as pd

from volatility_from_text.data.universe import UNIVERSE_COLS, universe_table

def test_universe_table_has_one_row_per_company_and_the_expected_columns() -> None:
    """
    Check that the universe table keeps one row per company and only `UNIVERSE_COLS`.
    """
    # Two filings of the same company and one of another, with an extra column
    df = pd.DataFrame({
        "cik": [1, 1, 2],
        "ticker": ["AAA", "AAA", "BBB"],
        "company": ["A Corp", "A Corp", "B Corp"],
        "sector": ["Technology", "Technology", "Utilities"],
        "sic": ["3571", "3571", "4911"],
        "sic_description": ["Electronic Computers", "Electronic Computers", "Electric Services"],
        "fiscal_year_end": ["0930", "0930", "1231"],
        "accession_number": ["x-1", "x-2", "y-1"],     # must not appear in the universe
    })

    out = universe_table(df)

    assert list(out.columns) == UNIVERSE_COLS
    assert list(out["cik"]) == [1, 2]