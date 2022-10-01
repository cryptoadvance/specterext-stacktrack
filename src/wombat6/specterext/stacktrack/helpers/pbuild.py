import datetime as dt
import logging

from cryptoadvance.specter.wallet import Wallet
import plotly.graph_objects as go

from . import util
from .core import Interval
from .count import SatCounter
from .plot import SatPlotter

logger = logging.getLogger(__name__)


class PlotBuilder:

    @classmethod
    def build_plot_1d(cls, wallet: Wallet) -> go.Figure:
        end_dt = dt.datetime.now() + dt.timedelta(hours=1)
        start_dt = end_dt - dt.timedelta(hours=24)
        return cls._build_plot(wallet, util.snap_to_day(start_dt), 24, Interval.HOURLY)

    @classmethod
    def build_plot_1w(cls, wallet: Wallet) -> go.Figure:
        end_dt = dt.datetime.now() + dt.timedelta(days=1)
        start_dt = end_dt - dt.timedelta(days=7)
        return cls._build_plot(wallet, util.snap_to_day(start_dt), 7, Interval.DAILY)

    @classmethod
    def build_plot_1m(cls, wallet: Wallet) -> go.Figure:
        end_dt = dt.datetime.now() + dt.timedelta(days=1)
        start_dt = end_dt - dt.timedelta(days=30)
        return cls._build_plot(wallet, util.snap_to_day(start_dt), 30, Interval.DAILY)

    @classmethod
    def build_plot_1y(cls, wallet: Wallet) -> go.Figure:
        now_dt = dt.datetime.now()
        start_dt_snap = dt.datetime(now_dt.year - 1, now_dt.month, 1)
        return cls._build_plot(wallet, start_dt_snap, 13, Interval.MONTHLY)

    @classmethod
    def build_plot_all(cls, wallet: Wallet) -> go.Figure:
        now_dt = dt.datetime.now()
        tx_list: list = wallet.txlist()
        start_dt = now_dt if len(tx_list) == 0 else dt.datetime.fromtimestamp(tx_list[-1]["time"])
        start_dt_snap = util.snap_to_year(start_dt)
        n_ticks = 12 * (now_dt.year - start_dt_snap.year + 1)
        return cls._build_plot(wallet, start_dt_snap, n_ticks, Interval.MONTHLY)

    @classmethod
    def _build_plot(cls, wallet, start_dt_snap: dt.datetime, n_ticks: int, interval: Interval):
        df = SatCounter.count_sats(wallet, start_dt_snap, n_ticks, interval)
        return SatPlotter.plot(df, f"{wallet.name} Balance")
