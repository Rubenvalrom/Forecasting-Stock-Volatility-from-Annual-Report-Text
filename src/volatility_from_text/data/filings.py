import pandas as pd
from pathlib import Path

from volatility_from_text.data.sec_api import get_json

def ten_k_filings(
    ciks: pd.Series,
    companies: pd.Series,
    tickers: pd.Series,
    sectors: pd.Series,
    route: Path ,
    start: str ,
    end: str,
    headers: dict[str, str] | None = None,
) -> pd.DataFrame:
    """
    Return the 10-K filings of each company between `start` and `end`.

    Parameters
    ----------
    ciks : pandas.Series
        Company CIKs.
    companies : pandas.Series
        Company names, aligned with `ciks`.
    tickers : pandas.Series
        Tickers, aligned with `ciks`.
    sectors : pandas.Series
        Pilot sectors, aligned with `ciks`.
    route : pathlib.Path
        Bronze folder where the SEC submissions JSONs are cached.
    start : str
        First filing date included (YYYY-MM-DD).
    end : str
        Last filing date included (YYYY-MM-DD).
    headers : dict[str, str], optional
            HTTP headers. Defaults to ``sec_headers()``.

    Returns
    -------
    pandas.DataFrame
        One row per 10-K, with company info (SIC, fiscal year end).
    """
    base = "https://data.sec.gov/submissions/"
    folder = route / "submissions"
    folder.mkdir(parents=True, exist_ok=True)   # creates the directory if needed

    all_filings = []

    for cik, company, ticker, sector in zip(ciks, companies, tickers, sectors):
        # main JSON: company info + the newest ~1000 filings + names of the older pages
        name = f"CIK{cik:010d}.json"            # company index padded to 10 digits
        data = get_json(base + name, folder / name, headers)

        pages = [pd.DataFrame(data["filings"]["recent"])]

        # older pages: only those whose date range overlaps [start, end]
        for page in data["filings"]["files"]:
            if page["filingTo"] >= start and page["filingFrom"] <= end:
                old = get_json(base + page["name"], folder / page["name"], headers)
                pages.append(pd.DataFrame(old))   # same columns as "recent"

        # recent + old pages in one DataFrame, with the company data
        cik_filings = pd.concat(pages, ignore_index=True).assign(
            cik=cik, 
            ticker=ticker, 
            company=company, 
            sector=sector,
            sic=data["sic"],  # Standard Industrial Classification, same info as sector but too detailed (4 digit id)
            sic_description=data["sicDescription"], # Title of the sic, human reading only
            fiscal_year_end=data["fiscalYearEnd"],
        )
        all_filings.append(cik_filings)

    filings = pd.concat(all_filings, ignore_index=True)

    # Keep 10-K forms between start and end
    filings = filings[
          (filings["filingDate"] >= start)
        & (filings["filingDate"] <= end)
        & (filings["form"] == "10-K")
    ]
    return filings.reset_index(drop=True)

