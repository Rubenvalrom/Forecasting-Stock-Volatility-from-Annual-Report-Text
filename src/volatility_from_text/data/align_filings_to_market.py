"""Align each filing with the first trading session that opens after its acceptance."""

import datetime
import pandas as pd

NY = "America/New_York"

def first_tradable_date(accepted_at: str | pd.Timestamp, sessions: pd.DatetimeIndex) -> datetime.date:
    """
    Return the first session whose 09:30 NY open is after `accepted_at`.

    Parameters
    ----------
    accepted_at : str or pandas.Timestamp
        Filing acceptance time (naive values are assumed NY time).
    sessions : pandas.DatetimeIndex
        Sorted trading session dates.

    Returns
    -------
    datetime.date
        First tradable session date.
    """

    # Adapt data types
    accepted_at = pd.Timestamp(accepted_at) # assert is a timestamp

    sessions = pd.DatetimeIndex(pd.to_datetime(sessions)) # sum timedeltas

    # Newyork timezone 
    # If a timezone is already set, corvert it first to avoid errors

    if accepted_at.tz is None:
        accepted_at = accepted_at.tz_localize(NY)      # no zone: assumes new york
    else:
        accepted_at = accepted_at.tz_convert(NY)       # with zone: convert it no NY

    # Newyork timezone + open hour (9:30)
    opens = (sessions + pd.Timedelta(hours=9, minutes=30)).tz_localize(NY)

    # first open index after accepted_at
    i = opens.searchsorted(accepted_at, side="right")

    # catch error if the date is in the future
    if i == len(opens):
        raise ValueError(f"{accepted_at} is after the last session in the calendar ({sessions[-1].date()})")

    return sessions[i].date()