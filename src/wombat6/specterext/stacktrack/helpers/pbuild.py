import datetime as dt
import logging

from cryptoadvance.specter.wallet import Wallet
import plotly.graph_objects as go

from . import count, plot
from .core import Interval

logger = logging.getLogger(__name__)


def build_plot_1d(wallet: Wallet) -> go.Figure:
    end_dt = dt.datetime.now() + dt.timedelta(hours=1)
    start_dt = end_dt - dt.timedelta(hours=24)
    return _build_plot(wallet, _snap_to_day(start_dt), 24, Interval.HOURLY)


def build_plot_1w(wallet: Wallet) -> go.Figure:
    end_dt = dt.datetime.now() + dt.timedelta(days=1)
    start_dt = end_dt - dt.timedelta(days=7)
    return _build_plot(wallet, _snap_to_day(start_dt), 7, Interval.DAILY)


def build_plot_1m(wallet: Wallet) -> go.Figure:
    end_dt = dt.datetime.now() + dt.timedelta(days=1)
    start_dt = end_dt - dt.timedelta(days=30)
    return _build_plot(wallet, _snap_to_day(start_dt), 30, Interval.DAILY)


def build_plot_1y(wallet: Wallet) -> go.Figure:
    now_dt = dt.datetime.now()
    start_dt_snap = dt.datetime(now_dt.year - 1, now_dt.month, 1)
    return _build_plot(wallet, start_dt_snap, 13, Interval.MONTHLY)


def build_plot_all(wallet: Wallet) -> go.Figure:
    now_dt = dt.datetime.now()
    tx_list: list = wallet.txlist()
    start_dt = now_dt if len(tx_list) == 0 else dt.datetime.fromtimestamp(tx_list[-1]["time"])
    start_dt_snap = _snap_to_year(start_dt)
    n_ticks = 12 * (now_dt.year - start_dt_snap.year + 1)
    return _build_plot(wallet, start_dt_snap, n_ticks, Interval.MONTHLY)


def _build_plot(wallet, start_dt_snap: dt.datetime, n_ticks: int, interval: Interval):
    df = count.count_sats(wallet, start_dt_snap, n_ticks, interval)
    return plot.plot_sats(df, f"{wallet.name} Balance")


def _snap_to_day(dt0: dt.datetime) -> dt.datetime:
    return dt.datetime(dt0.year, dt0.month, dt0.day)


def _snap_to_year(dt0: dt.datetime) -> dt.datetime:
    return dt.datetime(dt0.year, 1, 1)
