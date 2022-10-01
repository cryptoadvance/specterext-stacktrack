from collections import OrderedDict
import datetime as dt
import logging

import pandas as pd

from .core import Interval

logger = logging.getLogger(__name__)


class SatCounter:
    SATS_PER_BTC: int = 100_000_000

    @classmethod
    def count_sats(cls, wallet, start_dt_snap: dt.datetime, n_ticks: int, interval: Interval):

        # TODO Change this method to accept the end_dt_snap instead of the n_ticks.
        #  In the loop, simply compare the curr_dt to the end_dt_snap.
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
            if interval == Interval.HOURLY:
                tx_dt_snap = dt.datetime(tx_dt.year, tx_dt.month, tx_dt.day, tx_dt.hour)
            elif interval == Interval.DAILY:
                tx_dt_snap = dt.datetime(tx_dt.year, tx_dt.month, tx_dt.day)
            elif interval == Interval.MONTHLY:
                tx_dt_snap = dt.datetime(tx_dt.year, tx_dt.month, 1)
            else:
                raise ValueError(f"Illegal interval: {interval}")

            amount = round(tx["amount"] * cls.SATS_PER_BTC)
            if tx["category"] == "send":
                amount = -amount
            if tx_dt_snap in sats_by_dt.keys():
                sats_by_dt[tx_dt_snap] += amount
            else:
                prior_count += amount

        # Null out future amounts
        now_dt = dt.datetime.now()
        for item in sats_by_dt.items():
            curr_dt = item[0]
            if curr_dt > now_dt:
                sats_by_dt[curr_dt] = None

        sats = OrderedDict(sorted(sats_by_dt.items())).values()

        # Build DataFrame
        df = pd.DataFrame({"timestamp": timestamps, "sats": sats})
        df["sats_cusum"] = df["sats"].cumsum() + prior_count
        df["btc"] = df["sats"] / cls.SATS_PER_BTC
        df["btc_cusum"] = df["sats_cusum"] / cls.SATS_PER_BTC
        return df
