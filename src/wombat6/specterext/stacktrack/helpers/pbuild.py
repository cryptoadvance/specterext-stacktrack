import datetime as dt
import logging

from cryptoadvance.specter.wallet import Wallet
import plotly.graph_objects as go

from . import count, plot, dtutil
from .core import Interval

logger = logging.getLogger(__name__)


def build_plot_1d(wallet: Wallet) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.HOUR)
    start_dt = end_dt - dt.timedelta(hours=24)
    return _build_plot(wallet, start_dt, end_dt, Interval.HOUR)


def build_plot_1w(wallet: Wallet) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.DAY)
    start_dt = end_dt - dt.timedelta(days=7)
    return _build_plot(wallet, start_dt, end_dt, Interval.DAY)


def build_plot_1m(wallet: Wallet) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.DAY)
    start_dt = end_dt - dt.timedelta(days=31)
    return _build_plot(wallet, start_dt, end_dt, Interval.DAY)


def build_plot_1y(wallet: Wallet) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.MONTH)
    start_dt = dt.datetime(end_dt.year - 1, end_dt.month, 1)
    return _build_plot(wallet, start_dt, end_dt, Interval.MONTH)


def build_plot_all(wallet: Wallet) -> go.Figure:
    end_dt = dtutil.next_dt(dt.datetime.now(), Interval.MONTH)
    tx_list: list = wallet.txlist()
    temp_dt = dt.datetime.fromtimestamp(tx_list[-1]["time"]) if tx_list else dt.datetime.now()
    start_dt = dtutil.snap_to(temp_dt, Interval.MONTH)
    if end_dt - start_dt < dt.timedelta(days=365):
        return build_plot_1y(wallet)
    else:
        return _build_plot(wallet, start_dt, end_dt, Interval.MONTH)


def _build_plot(wallet, start_dt: dt.datetime, end_dt: dt.datetime, interval: Interval):
    df = count.count_sats(wallet, start_dt, end_dt, interval)
    return plot.plot_sats(df, f"{wallet.name} Balance")
