from datetime import datetime

import pytest

from wombat6.specterext.stacktrack.helpers import dtutil
from wombat6.specterext.stacktrack.helpers.core import Interval


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
