import pandas as pd
import numpy as np

# 1 row per company, describes the company
UNIVERSE_COLS = ["cik", "ticker", "company", "sector", "sic", "sic_description", "fiscal_year_end"]

def add_ciks(candidates, tickers_json):
    """
    Attach the SEC CIK and company name to each candidate ticker.

    Parameters
    ----------
    candidates : dict[str, list[str]]
        Candidate tickers grouped by sector, ``{sector: [ticker, ...]}``.
    tickers_json : dict
        SEC ``company_tickers.json`` content: a mapping whose values are
        dicts with keys ``cik_str``, ``ticker`` and ``title``.

    Returns
    -------
    pandas.DataFrame
        One row per candidate, with columns ``sector``, ``ticker``,
        ``cik`` (int) and ``company``.

    Raises
    ------
    ValueError
        If any candidate ticker has no CIK in ``tickers_json``.
    """
    df_cik = pd.DataFrame(list(tickers_json.values()))

    df_candidates = pd.DataFrame(
                    [(sector, ticker) for sector, tickers in candidates.items() for ticker in tickers],
                    columns=["sector", "ticker"]
                    )

    # Merge and filter out ciks without ticker
    df =  df_candidates.merge(df_cik, how="left", on="ticker")

    # Rename cik and title columns
    df = df.rename(columns={"cik_str":"cik", "title":"company"})


    # If a ticker has his CIK missing raise an error
    missing = df.loc[df["cik"].isna(), "ticker"].tolist()

    if missing:
        raise ValueError(f"No CIK found for {missing}.")

    df['cik'] = df['cik'].astype(int)

    return df


def one_report_per_year(df: pd.DataFrame, cik_col: str, filing_date_col: str, years: range) -> tuple[pd.DataFrame, pd.Index]:
    """
    Keep only the companies with exactly one filing in every year of ``years``.

    A company is dropped if, for any year in ``years``, it has no filing or
    more than one. Years with no filings in ``df`` count as missing for every
    company. Years outside ``years`` are not checked.

    Parameters
    ----------
    df : pandas.DataFrame
        Filings, one row per report.
    cik_col : str
        Name of the company identifier column.
    filing_date_col : str
        Name of the filing date column (datetime dtype).
    years : range
        Years in which each company must have exactly one filing.

    Returns
    -------
    pandas.DataFrame
        Filings of the companies kept. Their filings outside ``years`` are
        not removed.
    pandas.Index
        Identifiers of the companies dropped.
    """
    # One 10-K per company and year: build the company x year table
    filing_year = df[filing_date_col].dt.year

    # Number of filings per (company, year) pair, as a Series with a 2-level index
    counts = df.groupby([cik_col, filing_year]).size()

    # Move the year level to columns: one row per company, one column per year
    table = counts.unstack(fill_value=0) # fill value of 0 prevents NaN to give false positives

    # Every expected year must be in the table
    table = table.reindex(columns=years, fill_value=0)

    # Companies with exactly one report in every year
    complete = table.index[(table == 1).all(axis=1)]

    # Report and drop the rest
    dropped = table.index.difference(complete)
    df = df[df[cik_col].isin(complete)]

    return df, dropped

def select_per_sector(df, seed, n_sample=10, sector_col="sector", ticker_col="ticker"):
    """
    Randomly pick 10 companies per sector (pilot universe).

    Parameters
    ----------
    df : pandas.DataFrame
        Companies, one row per ticker.
    seed : int
        Seed for NumPy's global random state, for reproducibility.
    n_sample: int, default 10
        Sample size for each Sector
    sector_col : str, default "sector"
        Name of the sector column.
    ticker_col : str, default "ticker"
        Name of the ticker column.

    Returns
    -------
    pandas.DataFrame
        Rows of ``df`` belonging to the selected tickers.

    Raises
    ------
    ValueError
        If a sector has fewer than ``n_sample`` companies.

    """
    # Seed for reproducibility
    rng = np.random.RandomState(seed) 

    companies = df.drop_duplicates(ticker_col)  # sample companies, not filings
    sectors = companies[sector_col].unique()
    chosen = []

    for sector in sectors:
        in_sector = companies.loc[companies[sector_col] == sector, ticker_col]
        chosen += list(in_sector.sample(n=n_sample, random_state=rng))

    df = df[df[ticker_col].isin(chosen)]

    return df

