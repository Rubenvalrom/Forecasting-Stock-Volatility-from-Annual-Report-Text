import pandas as pd

from volatility_from_text.data.universe import one_report_per_year

YEARS = range(2015, 2018)   # 2015, 2016, 2017


def _filings(rows: list[tuple[int, str]]) -> pd.DataFrame:
    """
    Build a small filings table from (cik, date) pairs.

    Parameters
    ----------
    rows : list of tuple[int, str]
        Pairs of company identifier and filing date ("YYYY-MM-DD").

    Returns
    -------
    pandas.DataFrame
        Filings with `cik` and `filing_date` (datetime dtype) columns.
    """
    df = pd.DataFrame(rows, columns=["cik", "filing_date"])
    df["filing_date"] = pd.to_datetime(df["filing_date"])
    return df


def test_only_companies_with_one_report_in_every_year_are_kept() -> None:
    """
    Check that companies with a missing or duplicated year are dropped.
    """
    df = _filings([
        # cik 1: one report per year -> kept
        (1, "2015-02-01"), (1, "2016-02-01"), (1, "2017-02-01"),
        # cik 2: two reports in 2016 -> dropped
        (2, "2015-02-01"), (2, "2016-02-01"), (2, "2016-08-01"), (2, "2017-02-01"),
        # cik 3: no report in 2016 -> dropped
        (3, "2015-02-01"), (3, "2017-02-01"),
    ])

    kept, dropped = one_report_per_year(df, "cik", "filing_date", YEARS)

    assert set(kept["cik"]) == {1}
    assert set(dropped) == {2, 3}


def test_a_year_missing_for_every_company_drops_them_all() -> None:
    """
    Check that a required year absent from the data drops every company.
    """
    # Nobody filed in 2016: the year never shows up in the data, but it is still required
    df = _filings([(1, "2015-02-01"), (1, "2017-02-01")])

    kept, dropped = one_report_per_year(df, "cik", "filing_date", YEARS)

    assert kept.empty
    assert set(dropped) == {1}