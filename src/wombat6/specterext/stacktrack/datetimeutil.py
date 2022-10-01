import datetime as dt


def snap_to_day(dt0: dt.datetime) -> dt.datetime:
    return dt.datetime(dt0.year, dt0.month, dt0.day)


def snap_to_year(dt0: dt.datetime) -> dt.datetime:
    return dt.datetime(dt0.year, 1, 1)


# def years_diff_ceil(dt0: dt.datetime, dt1: dt.datetime) -> int:
#     # https://stackoverflow.com/a/765862
#     result = dt0.year - dt1.year + 1
#     dt0_adj = dt.datetime(dt1.year, dt0.month, dt0.day, dt0.hour, dt0.minute, dt0.second)
#     if dt0_adj < dt1:
#         result -= 1
#     return result
