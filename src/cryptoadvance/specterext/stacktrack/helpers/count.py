import datetime as dt
import logging

from cryptoadvance.specter.wallet import Wallet
import pandas as pd

from . import dtutil
from .core import *


logger = logging.getLogger(__name__)


def count_sats(
        wallet: Wallet,
        start_dt: dt.datetime,
        end_dt: dt.datetime,
        interval: Interval
) -> pd.DataFrame:

    """
    Counts the wallet's satoshis for the given time range, binned by the given interval. The returned DataFrame has
    three columns:

    - timestamp: Timestamp in epoch seconds.
    - sats: Satoshi count for a given interval. Can be negative if there was a net outflow.
    - sats_cusum: Satoshi cumulative sum. Again this can be negative if there was a net outflow.

    Note that satoshis for transactions before the start time are rolled into the satoshi cumulative sum.

    :param wallet: bitcoin wallet
    :param start_dt: start of the time range (inclusive)
    :param end_dt: end of the time range (exclusive)
    :param interval: increment interval
    :return: a pandas DataFrame as described above
    """

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
            bin_dt = dtutil.snap_to(tx_dt, interval)
            sat_bins[bin_dt] += amount

    sats = [item[1] for item in sorted(sat_bins.items())]

    df = pd.DataFrame({"timestamp": timestamps, "sats": sats})
    df["sats_cusum"] = df["sats"].cumsum() + prior_count

    return df
