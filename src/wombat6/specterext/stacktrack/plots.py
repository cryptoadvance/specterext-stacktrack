from collections import OrderedDict
import datetime as dt
from enum import Enum
import logging

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

from cryptoadvance.specter.wallet import Wallet
from wombat6.specterext.stacktrack import datetimeutil as dtu

logger = logging.getLogger(__name__)


class Interval(Enum):
    HOURLY = 1
    DAILY = 2
    MONTHLY = 3


# TODO
# - Use UTC
# - Sunday vs Monday start
class Plots:
    SATS_PER_BTC: int = 100_000_000

    @classmethod
    def build_1d_plot(cls, wallet: Wallet) -> go.Figure:
        end_dt = dt.datetime.now() + dt.timedelta(hours=1)
        start_dt = end_dt - dt.timedelta(hours=24)
        return cls._to_plot(wallet, dtu.snap_to_day(start_dt), 24, Interval.HOURLY)

    @classmethod
    def build_1w_plot(cls, wallet: Wallet) -> go.Figure:
        end_dt = dt.datetime.now() + dt.timedelta(days=1)
        start_dt = end_dt - dt.timedelta(days=7)
        return cls._to_plot(wallet, dtu.snap_to_day(start_dt), 7, Interval.DAILY)

    @classmethod
    def build_1m_plot(cls, wallet: Wallet) -> go.Figure:
        end_dt = dt.datetime.now() + dt.timedelta(days=1)
        start_dt = end_dt - dt.timedelta(days=30)
        return cls._to_plot(wallet, dtu.snap_to_day(start_dt), 30, Interval.DAILY)

    @classmethod
    def build_1y_plot(cls, wallet: Wallet) -> go.Figure:
        now_dt = dt.datetime.now()
        start_dt_snap = dt.datetime(now_dt.year - 1, now_dt.month, 1)
        return cls._to_plot(wallet, start_dt_snap, 13, Interval.MONTHLY)

    @classmethod
    def build_all_plot(cls, wallet: Wallet) -> go.Figure:
        now_dt = dt.datetime.now()
        tx_list: list = wallet.txlist()
        start_dt = now_dt if len(tx_list) == 0 else dt.datetime.fromtimestamp(tx_list[-1]["time"])
        start_dt_snap = dtu.snap_to_year(start_dt)
        n_ticks = 12 * (now_dt.year - start_dt_snap.year + 1)
        return cls._to_plot(wallet, start_dt_snap, n_ticks, Interval.MONTHLY)

    @classmethod
    def _to_plot(cls, wallet, start_dt_snap: dt.datetime, n_ticks: int, interval: Interval):
        timestamps, sats, prior = cls._count_sats(wallet, start_dt_snap, n_ticks, interval)
        df = cls._to_dataframe(timestamps, sats, prior)
        return cls._df_to_plot(df, f"{wallet.name} Balance")

    @classmethod
    def _count_sats(cls, wallet, start_dt_snap: dt.datetime, n_ticks: int, interval: Interval):
        timestamps = []
        sats_by_dt = {}
        prior = 0

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
                prior += amount

        # Null out future amounts
        now_dt = dt.datetime.now()
        for item in sats_by_dt.items():
            curr_dt = item[0]
            if curr_dt > now_dt:
                sats_by_dt[curr_dt] = None

        sats = OrderedDict(sorted(sats_by_dt.items())).values()
        return timestamps, sats, prior

    @classmethod
    def _to_dataframe(cls, timestamps, sats, base_sats):
        df = pd.DataFrame({"timestamp": timestamps, "sats": sats})
        df["sats_cusum"] = df["sats"].cumsum() + base_sats
        df["btc"] = df["sats"] / cls.SATS_PER_BTC
        df["btc_cusum"] = df["sats_cusum"] / cls.SATS_PER_BTC
        return df

    @classmethod
    def _df_to_plot(cls, df: pd.DataFrame, title: str) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["timestamp"],
            y=df["btc"],
            name="BTC",
            marker={"color": "Green"},
        ))
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["btc_cusum"],
            name="Cumulative",
            mode="lines",
            line_shape="hv",
            marker={"color": "Gold"},
        ))
        fig.update_layout(
            title=title,
            title_x=0.5,
            yaxis_title="BTC",
            template="plotly_dark",
            width=800,
            height=400,
            paper_bgcolor="#11181F",
            plot_bgcolor="#11181F",
        )
        return plot(fig, output_type="div")
