import pandas as pd
import pytest

from volatility_from_text.data.align_filings_to_market import first_tradable_date

NY = "America/New_York"

# 2019-07-04 is a holiday; 2015-10-28/29 are for the real Apple filing
SESSIONS = pd.to_datetime([
    "2015-10-28", 
    "2015-10-29",
    "2019-07-01", 
    "2019-07-02", 
    "2019-07-03", 
    "2019-07-05", 
    "2019-07-08",
])


@pytest.mark.parametrize("accepted, expected", [
    ("2019-07-01 08:00", "2019-07-01"),  # before the open: same day
    ("2019-07-01 09:30", "2019-07-02"),  # exactly at the open
    ("2019-07-01 11:00", "2019-07-02"),  # during the session
    ("2019-07-01 16:00", "2019-07-02"),  # at the close
    ("2019-07-03 17:00", "2019-07-05"),  # holiday eve
    ("2019-07-05 17:00", "2019-07-08"),  # Friday evening
    ("2019-07-06 10:00", "2019-07-08"),  # Saturday morning
])

def test_first_session_opens_after_acceptance(accepted, expected):
    accepted = pd.Timestamp(accepted, tz=NY)
    assert first_tradable_date(accepted, SESSIONS) == pd.Timestamp(expected).date()


def test_utc_timestamps_are_converted_not_relabelled():
    # Real Apple 10-K: 20:31 UTC is 16:31 in New York, after the close
    assert first_tradable_date("2015-10-28T20:31:09.000Z", SESSIONS) == pd.Timestamp("2015-10-29").date()
    # 12:00 UTC is 08:00 in New York, before the open: same day
    assert first_tradable_date("2019-07-01T12:00:00.000Z", SESSIONS) == pd.Timestamp("2019-07-01").date()


def test_acceptance_after_the_calendar_raises():
    with pytest.raises(ValueError):
        first_tradable_date(pd.Timestamp("2030-01-01 10:00", tz=NY), SESSIONS)