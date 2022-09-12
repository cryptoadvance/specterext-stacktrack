import logging

import pandas as pd
from flask import redirect, render_template, request, url_for
from flask import current_app as app
from flask_login import login_required, current_user
import plotly.graph_objects as go

from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.services.controller import user_secret_decrypted_required
from cryptoadvance.specter.wallet import Wallet

from .plots import Plots
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
    wallet: Wallet = StacktrackService.get_associated_wallet()
    tx_df: pd.DataFrame = Plots.build_tx_df(wallet)
    balance_plot: go.Figure = Plots.build_plot(tx_df, f"Wallet balance: {wallet.name}")
    return render_template(
        "stacktrack/transactions.jinja",
        wallet=wallet,
        txlist=wallet.txlist(),
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
