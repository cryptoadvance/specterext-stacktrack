import datetime as dt
import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

from . import dtutil
from .core import Interval, SATS_PER_BTC


logger = logging.getLogger(__name__)

# This module deals with transaction lists instead of wallets, since we need to build charts for the wallet overview.


def build_chart_1d(txs: list) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.HOUR)
    start_dt = end_dt - dt.timedelta(hours=24)
    return _build_chart(txs, start_dt, end_dt, Interval.HOUR)


def build_chart_1w(txs: list) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.DAY)
    start_dt = end_dt - dt.timedelta(days=7)
    return _build_chart(txs, start_dt, end_dt, Interval.DAY)


def build_chart_1m(txs: list) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.DAY)
    start_dt = end_dt - dt.timedelta(days=31)
    return _build_chart(txs, start_dt, end_dt, Interval.DAY)


def build_chart_1y(txs: list) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.MONTH)
    start_dt = dt.datetime(end_dt.year - 1, end_dt.month, 1)
    return _build_chart(txs, start_dt, end_dt, Interval.MONTH)


def build_chart_all(txs: list) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.MONTH)
    # TODO Check on the difference between "time" and "blocktime".
    #  Not sure which I'm supposed to use here.
    temp_dt = dt.datetime.fromtimestamp(txs[-1]["time"]) if txs else dt.datetime.now()
    start_dt = dtutil.snap_to(temp_dt, Interval.MONTH)
    if end_dt - start_dt < dt.timedelta(days=365):
        return build_chart_1y(txs)
    else:
        return _build_chart(txs, start_dt, end_dt, Interval.MONTH)


def _build_chart(txs: list, start_dt: dt.datetime, end_dt: dt.datetime, interval: Interval):
    df: pd.DataFrame = _count_sats(txs, start_dt, end_dt, interval)
    return _plot_sats(df)


def _count_sats(
        txs: list,
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

    :param txs: transaction list
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
    for tx in txs:
        # TODO Check on the difference between "time" and "blocktime".
        #  Not sure which I'm supposed to use here.
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


# TODO
# - Use UTC
# - Sunday vs Monday start
def _plot_sats(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["timestamp"],
        y=df["sats"] / SATS_PER_BTC,
        name="BTC",
        marker={"color": "Green"},
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["sats_cusum"] / SATS_PER_BTC,
        name="Cumulative",
        mode="lines",
        line_shape="hv",
        marker={"color": "Gold"},
    ))
    fig.update_layout(
        title="Balance",
        title_x=0.5,
        yaxis_title="BTC",
        template="plotly_dark",
        width=800,
        height=400,
        paper_bgcolor="#11181F",
        plot_bgcolor="#11181F",
    )
    return plot(fig, output_type="div")
