import datetime as dt


def snap_to_day(dt0: dt.datetime) -> dt.datetime:
    return dt.datetime(dt0.year, dt0.month, dt0.day)


def snap_to_year(dt0: dt.datetime) -> dt.datetime:
    return dt.datetime(dt0.year, 1, 1)
