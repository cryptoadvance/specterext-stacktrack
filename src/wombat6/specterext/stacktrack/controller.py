import logging

import pandas as pd
from flask import redirect, render_template, request, url_for, flash
from flask import current_app as app
from flask_login import login_required, current_user

import plotly.graph_objects as go
from plotly.offline import plot
from plotly.graph_objs import Scatter

import plotly.express as px

from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.services.controller import user_secret_decrypted_required
from cryptoadvance.specter.user import User
from cryptoadvance.specter.wallet import Wallet
from .service import StacktrackService


logger = logging.getLogger(__name__)

stacktrack_endpoint = StacktrackService.blueprint


def ext() -> StacktrackService:
    """ convenience for getting the extension-object"""
    return app.specter.ext["stacktrack"]


def specter() -> Specter:
    """ convenience for getting the specter-object"""
    return app.specter


@stacktrack_endpoint.route("/")
@login_required
@user_secret_decrypted_required
def index():
    return render_template("stacktrack/index.jinja")


@stacktrack_endpoint.route("/transactions")
@login_required
@user_secret_decrypted_required
def transactions():
    # The wallet currently configured for ongoing auto-withdrawals
    wallet: Wallet = StacktrackService.get_associated_wallet()
    balance_df: pd.DataFrame = StacktrackService.build_balance_df(wallet)

    # fig = px.line(df, x="year", y="lifeExp", color="country", template="plotly_dark")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=balance_df["date"],
        y=balance_df["cum_btc"],
        name="BTC balance",
        mode="lines",
        line_shape="hv",
    ))
    fig.add_trace(go.Bar(
        x=balance_df["date"],
        y=balance_df["btc"],
        name="BTC",
        marker={
            "color": "green",
        },
    ))
    fig.update_layout(
        title_text=f"Wallet balance: {wallet.name}",
        title_x=0.5,
        xaxis_title="Date",
        template="plotly_dark",
        width=800,
        height=400,
        paper_bgcolor="#11181F",
        plot_bgcolor="#11181F",
    )
    balance_plot = plot(fig, output_type="div")

    return render_template(
        "stacktrack/transactions.jinja",
        wallet=wallet,
        services=app.specter.service_manager.services,
        plot=balance_plot,
    )


@stacktrack_endpoint.route("/settings", methods=["GET"])
@login_required
@user_secret_decrypted_required
def settings_get():
    associated_wallet: Wallet = StacktrackService.get_associated_wallet()

    # Get the user's Wallet objs, sorted by Wallet.name
    wallet_names = sorted(current_user.wallet_manager.wallets.keys())
    wallets = [current_user.wallet_manager.wallets[name] for name in wallet_names]

    return render_template(
        "stacktrack/settings.jinja",
        associated_wallet=associated_wallet,
        wallets=wallets,
        cookies=request.cookies,
    )


@stacktrack_endpoint.route("/settings", methods=["POST"])
@login_required
@user_secret_decrypted_required
def settings_post():
    show_menu = request.form["show_menu"]
    user = app.specter.user_manager.get_user()
    if show_menu == "yes":
        user.add_service(StacktrackService.id)
    else:
        user.remove_service(StacktrackService.id)
    used_wallet_alias = request.form.get("used_wallet")
    if used_wallet_alias is not None:
        wallet = current_user.wallet_manager.get_by_alias(used_wallet_alias)
        StacktrackService.set_associated_wallet(wallet)
    return redirect(url_for(f"{ StacktrackService.get_blueprint_name()}.settings_get"))
