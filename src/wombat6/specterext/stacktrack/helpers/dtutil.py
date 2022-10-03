from datetime import datetime, timedelta

from .core import Interval


def snap_to(dt: datetime, interval: Interval) -> datetime:
    if interval == Interval.HOUR:
        return datetime(dt.year, dt.month, dt.day, dt.hour)
    elif interval == Interval.DAY:
        return datetime(dt.year, dt.month, dt.day)
    elif interval == Interval.MONTH:
        return datetime(dt.year, dt.month, 1)
    else:
        raise ValueError(f"Illegal interval: {interval}")


def next_dt(curr_dt: datetime, interval: Interval):
    if interval == Interval.HOUR:
        return snap_to(curr_dt, interval) + timedelta(hours=1)
    elif interval == Interval.DAY:
        return snap_to(curr_dt, interval) + timedelta(days=1)
    elif interval == Interval.MONTH:
        year = curr_dt.year
        month = curr_dt.month + 1
        if month == 13:
            year += 1
            month = 1
        return datetime(year, month, 1)
