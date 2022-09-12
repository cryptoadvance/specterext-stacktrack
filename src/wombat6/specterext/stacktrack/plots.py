import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

from cryptoadvance.specter.wallet import Wallet


class Plots:
    SATS_PER_BTC = 100_000_000

    @classmethod
    def build_tx_df(cls, wallet: Wallet) -> pd.DataFrame:
        data = {
            "timestamp": [],
            "sats": [],
        }

        # TODO Sort this by date, instead of assuming it's in a certain order.
        txlist = reversed(wallet.txlist())

        for tx in txlist:
            time = tx["time"]
            category = tx["category"]

            # FIXME Figure out how to get the exact sat count here, without improper rounding
            amount = tx["amount"] * cls.SATS_PER_BTC

            if category == "send":
                amount = -amount
            data["timestamp"].append(pd.Timestamp(time, unit="s", tz="UTC"))
            data["sats"].append(amount)

        df = pd.DataFrame(data)

        df["date"] = df["timestamp"].dt.date
        df["btc"] = df["sats"] / cls.SATS_PER_BTC
        df["cum_btc"] = df["sats"].cumsum() / cls.SATS_PER_BTC

        return df[["date", "btc", "cum_btc"]]

    @classmethod
    def build_plot(cls, tx_df: pd.DataFrame, title: str) -> go.Figure:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=tx_df["date"],
            y=tx_df["btc"],
            name="Daily",
            marker={
                "color": "Green",
            },
        ))
        fig.add_trace(go.Scatter(
            x=tx_df["date"],
            y=tx_df["cum_btc"],
            name="Cumulative",
            mode="lines",
            line_shape="hv",
            marker={
                "color": "Gold",
            },
        ))
        fig.update_layout(
            title_text=title,
            title_x=0.5,
            # xaxis_title="Date",
            yaxis_title="BTC",
            template="plotly_dark",
            width=800,
            height=400,
            paper_bgcolor="#11181F",
            plot_bgcolor="#11181F",
        )
        return plot(fig, output_type="div")
