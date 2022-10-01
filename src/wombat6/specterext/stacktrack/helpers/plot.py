import datetime as dt
import logging

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

from .core import *

logger = logging.getLogger(__name__)


# TODO
# - Use UTC
# - Sunday vs Monday start
class SatPlotter:

    @classmethod
    def plot(cls, df: pd.DataFrame, title: str) -> go.Figure:
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
