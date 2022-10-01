import datetime as dt

import pytest

from wombat6.specterext.stacktrack.helpers import count
from wombat6.specterext.stacktrack.helpers.core import *


def test_snap_to_hourly():
    dt0 = dt.datetime(2022, 10, 1, 16, 38, 30)
    result = count._snap_to_interval(dt0, Interval.HOURLY)
    assert result == dt.datetime(2022, 10, 1, 16, 0, 0)


def test_snap_to_daily():
    dt0 = dt.datetime(2022, 10, 1, 16, 38, 30)
    result = count._snap_to_interval(dt0, Interval.DAILY)
    assert result == dt.datetime(2022, 10, 1, 0, 0, 0)


def test_snap_to_monthly():
    dt0 = dt.datetime(2022, 10, 1, 16, 38, 30)
    result = count._snap_to_interval(dt0, Interval.MONTHLY)
    assert result == dt.datetime(2022, 10, 1, 0, 0, 0)


def test_snap_to_invalid_interval():
    with pytest.raises(ValueError):
        dt0 = dt.datetime(2022, 10, 1, 16, 38, 30)
        count._snap_to_interval(dt0, -1)
