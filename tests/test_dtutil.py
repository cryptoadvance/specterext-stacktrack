from datetime import datetime

import pytest

from cryptoadvance.specterext.stacktrack.helpers import dtutil
from cryptoadvance.specterext.stacktrack.helpers.core import Interval


def test_snap_to_hour():
    dt = datetime(2022, 10, 5, 16, 38, 30)
    result = dtutil.snap_to(dt, Interval.HOUR)
    assert result == datetime(2022, 10, 5, 16, 0, 0)


def test_snap_to_day():
    dt = datetime(2022, 10, 5, 16, 38, 30)
    result = dtutil.snap_to(dt, Interval.DAY)
    assert result == datetime(2022, 10, 5)


def test_snap_to_month():
    dt = datetime(2022, 10, 5, 16, 38, 30)
    result = dtutil.snap_to(dt, Interval.MONTH)
    assert result == datetime(2022, 10, 1)


def test_snap_to_invalid_interval():
    with pytest.raises(ValueError):
        dt = datetime(2022, 10, 5, 16, 38, 30)
        dtutil.snap_to(dt, -1)


def test_next_dt_hour():
    curr_dt = datetime(2022, 10, 5, 16, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.HOUR)
    assert result == datetime(2022, 10, 5, 17, 0, 0)


def test_next_dt_hour_rollover():
    curr_dt = datetime(2022, 10, 5, 23, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.HOUR)
    assert result == datetime(2022, 10, 6)


def test_next_dt_day():
    curr_dt = datetime(2022, 10, 5, 16, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.DAY)
    assert result == datetime(2022, 10, 6)


def test_next_dt_day_rollover():
    curr_dt = datetime(2022, 10, 31, 16, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.DAY)
    assert result == datetime(2022, 11, 1)


def test_next_dt_day_rollover_leap_day():
    curr_dt = datetime(2024, 2, 29, 16, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.DAY)
    assert result == datetime(2024, 3, 1)


def test_next_dt_month():
    curr_dt = datetime(2022, 10, 5, 16, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.MONTH)
    assert result == datetime(2022, 11, 1)


def test_next_dt_month_rollover():
    curr_dt = datetime(2022, 12, 5, 16, 38, 30)
    result = dtutil.next_dt(curr_dt, Interval.MONTH)
    assert result == datetime(2023, 1, 1)
