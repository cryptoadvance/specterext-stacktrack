import datetime as dt
from collections import OrderedDict
import logging

from cryptoadvance.specter.wallet import Wallet
import pandas as pd

from . import dtutil
from .core import Interval


logger = logging.getLogger(__name__)

SATS_PER_BTC: int = 100_000_000


def count_sats(
        wallet: Wallet,
        start_dt: dt.datetime,
        end_dt: dt.datetime,
        interval: Interval
) -> pd.DataFrame:

    timestamps = []
    sat_bins = {}
    prior_count = 0

    # Initialize
    curr_dt = start_dt
    while curr_dt < end_dt:
        timestamps.append(pd.Timestamp(curr_dt.timestamp(), unit="s"))
        sat_bins[curr_dt] = 0
        curr_dt = dtutil.next_dt(curr_dt, interval)

    # Count
    txs: list = wallet.txlist()
    for tx in txs:
        tx_dt = dt.datetime.fromtimestamp(tx["time"])
        amount = round(tx["amount"] * SATS_PER_BTC)
        if tx["category"] == "send":
            amount = -amount
        if tx_dt < timestamps[0]:
            prior_count += amount
        else:
            tx_dt_snap = dtutil.snap_to(tx_dt, interval)
            sat_bins[tx_dt_snap] += amount

    sats = [item[1] for item in sorted(sat_bins.items())]

    df = pd.DataFrame({"timestamp": timestamps, "sats": sats})
    df["sats_cusum"] = df["sats"].cumsum() + prior_count
    df["btc"] = df["sats"] / SATS_PER_BTC
    df["btc_cusum"] = df["sats_cusum"] / SATS_PER_BTC

    return df
