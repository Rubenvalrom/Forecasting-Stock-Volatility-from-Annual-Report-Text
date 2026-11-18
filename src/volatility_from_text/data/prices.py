import pandas as pd
import yfinance as yf
from pathlib import Path


def _download(
    ticker: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
    path: Path,
) -> pd.DataFrame:
    """
    Download adjusted daily prices from yfinance and save them to the parquet cache.
    Just for this module

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker.
    start : pandas.Timestamp
        First date downloaded.
    end : pandas.Timestamp
        End date of the download (exclusive).
    path : pathlib.Path
        Parquet file where the prices are saved (overwritten if it exists).

    Returns
    -------
    pandas.DataFrame
        Daily OHLCV prices indexed by date.

    Raises
    ------
    ValueError
        If yfinance returns no rows (delisted ticker, wrong symbol, empty range).
    """

    df = yf.download(tickers=ticker, start=start, end=end, auto_adjust=True, progress=False)

    # yfinance does not raise on failure, it just returns an empty frame
    if df.empty:
        raise ValueError(f"No prices returned for {ticker}")

    # Recent yfinance versions return (field, ticker) MultiIndex columns
    df.columns = df.columns.get_level_values(0)
    df.to_parquet(path)

    return df


def get_prices(
    ticker: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
    route: Path,
) -> pd.DataFrame:
    """
    Load adjusted daily prices from the parquet cache or download them from yfinance.

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker.
    start : pandas.Timestamp
        First date downloaded.
    end : pandas.Timestamp
        End date of the download (exclusive).
    route : pathlib.Path
        Folder of the parquet cache.

    Returns
    -------
    pandas.DataFrame
        Daily OHLCV prices indexed by date.
    """

    path = route / f"{ticker}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if (path.exists()):
        df = pd.read_parquet(path)
        # Check if the dates are in within the correct range (with some margin)
        min_date = pd.Timestamp(start) + pd.Timedelta(days=7)
        max_date = pd.Timestamp(end) - pd.Timedelta(days=7)

        if df.index.min() > min_date or df.index.max() < max_date:

            # Download again in case the dates are not correct (just for the pilot)
            df = _download(ticker, start, end, path)

    # If the ticker does not have the parquet in cache it is downloaded
    else:
        df = _download(ticker, start, end, path)

    return df


def check_session(df: pd.DataFrame, sessions: pd.DatetimeIndex) -> bool:
    """
    Check that a price table has exactly the same trading days as the SPY calendar.

    Parameters
    ----------
    df : pandas.DataFrame
        Daily prices indexed by date.

    sessions : pandas.DatetimeIndex
        Reference trading sessions (SPY).

    Returns
    -------
    bool
        True if the calendars match or False if they don't
    """
    return df.index.equals(sessions)