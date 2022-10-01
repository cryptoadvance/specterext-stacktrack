from collections import OrderedDict
import datetime as dt
import logging

import pandas as pd

from .core import Interval


logger = logging.getLogger(__name__)

SATS_PER_BTC: int = 100_000_000


def count_sats(wallet, start_dt_snap: dt.datetime, n_ticks: int, interval: Interval) -> pd.DataFrame:
    # TODO Change this method to accept the end_dt_snap instead of the n_ticks.
    #  In the loop, simply compare the curr_dt to the end_dt_snap.
    end_dt = dt.datetime.now()
    timestamps = []
    sats_by_dt = {}
    prior_count = 0

    # Initialize sat counter
    for i in range(n_ticks):
        if interval == Interval.HOURLY:
            curr_dt = start_dt_snap + dt.timedelta(hours=i)
        elif interval == Interval.DAILY:
            curr_dt = start_dt_snap + dt.timedelta(days=i)
        elif interval == Interval.MONTHLY:
            month0 = (start_dt_snap.month - 1) + i
            year = start_dt_snap.year + (month0 // 12)
            month = month0 % 12 + 1
            curr_dt = dt.datetime(year, month, 1)
        else:
            raise ValueError(f"Illegal interval: {interval}")

        timestamps.append(pd.Timestamp(curr_dt.timestamp(), unit="s"))
        sats_by_dt[curr_dt] = 0

    # Allocate sats to timestamps
    tx_list: list = wallet.txlist()
    for tx in tx_list:
        tx_dt = dt.datetime.fromtimestamp(tx["time"])
        tx_dt_snap = _snap_to_interval(tx_dt, interval)
        amount = round(tx["amount"] * SATS_PER_BTC)
        if tx["category"] == "send":
            amount = -amount
        if tx_dt_snap in sats_by_dt.keys():
            sats_by_dt[tx_dt_snap] += amount
        else:
            prior_count += amount

    _clear_future_amounts(sats_by_dt, end_dt)
    sats = OrderedDict(sorted(sats_by_dt.items())).values()
    return _to_df(timestamps, sats, prior_count)


def _snap_to_interval(dt0: dt.datetime, interval: Interval) -> dt.datetime:
    if interval == Interval.HOURLY:
        return dt.datetime(dt0.year, dt0.month, dt0.day, dt0.hour)
    elif interval == Interval.DAILY:
        return dt.datetime(dt0.year, dt0.month, dt0.day)
    elif interval == Interval.MONTHLY:
        return dt.datetime(dt0.year, dt0.month, 1)
    else:
        raise ValueError(f"Illegal interval: {interval}")


def _clear_future_amounts(sats_by_dt, end_dt: dt.datetime):
    for item in sats_by_dt.items():
        curr_dt = item[0]
        if curr_dt > end_dt:
            sats_by_dt[curr_dt] = None


def _to_df(timestamps, sats, prior_count) -> pd.DataFrame:
    df = pd.DataFrame({"timestamp": timestamps, "sats": sats})
    df["sats_cusum"] = df["sats"].cumsum() + prior_count
    df["btc"] = df["sats"] / SATS_PER_BTC
    df["btc_cusum"] = df["sats_cusum"] / SATS_PER_BTC
    return df
