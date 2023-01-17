import logging
import random

from flask import current_app as app, render_template, request
from flask_login import login_required
import plotly.graph_objects as go

from cryptoadvance.specter.server_endpoints.wallets.wallets_vm import WalletsOverviewVm
from cryptoadvance.specter.services import callbacks
from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.wallet import Wallet

from .helpers import plot
from .service import StacktrackService

logger = logging.getLogger(__name__)
rand = random.randint(0, 1e32)  # to force style refresh

# TODO Check whether this is correct. I don't see a blueprint attribute on StacktrackService.
stacktrack_endpoint = StacktrackService.blueprint


def specter() -> Specter:
    """ convenience for getting the specter-object"""
    return app.specter


def ext() -> StacktrackService:
    """ convenience for getting the extension-object"""
    return specter().ext["stacktrack"]


@stacktrack_endpoint.context_processor
def inject_common_stuff():
    """Can be used in all jinja2 templates"""
    return {
        "ext_wallettabs": specter().service_manager.execute_ext_callbacks(
            callbacks.add_wallettabs
        ),
    }


@stacktrack_endpoint.route("/")
@login_required
def index():
    return render_template("stacktrack/index.jinja")


@stacktrack_endpoint.route("/wallets_overview")
@login_required
def wallets_overview():
    span: str = request.args.get("span")
    span = "1y" if span is None else span

    specter().check_blockheight()

    # Replace the default tx table with one that includes a chart.
    view_model = WalletsOverviewVm()
    view_model.tx_table_include = "stacktrack/wallet/overview/overview_chart_and_tx_table.jinja"

    wallets: list[Wallet] = list(specter().wallet_manager.wallets.values())
    for wallet in wallets:
        wallet.update_balance()
        wallet.check_utxo()
    txs: list = _extract_txs(wallets)
    try:
        chart: go.Figure = plot.build_chart(span, txs)
    except Exception as e:
        logger.exception(e)
        chart = None

    return render_template(
        "wallet/overview/wallets_overview.jinja",
        specter=specter(),
        rand=rand,
        services=specter().service_manager.services,
        wallets_overview_vm=view_model,
        active_span=span,
        chart=chart,
        url_path="wallets_overview",
    )

    return render_template("stacktrack/wallet/overview/wallets_overview.jinja")


@stacktrack_endpoint.route("/wallet/<wallet_alias>/chart", methods=["GET"])
@login_required
def stacktrack_wallet_chart(wallet_alias: str) -> str:
    span: str = request.args.get("span")
    span = "1y" if span is None else span
    wallet: Wallet = app.specter.wallet_manager.get_by_alias(wallet_alias)
    chart: go.Figure = plot.build_chart(span, wallet.txlist())
    return render_template(
        "stacktrack/wallet/chart/wallet_chart.jinja",
        wallet_alias=wallet_alias,
        wallet=wallet,
        ext_wallettabs=app.specter.service_manager.execute_ext_callbacks(callbacks.add_wallettabs),
        active_span=span,
        chart=chart,
        url_path="chart",
    )


# 'type' object not subscriptable in Python 3.7, so just use bare list.
# def _extract_txs(wallets: list[Wallet]) -> list:
def _extract_txs(wallets: list) -> list:
    txs: list = []
    for wallet in wallets:
        txs = txs + wallet.txlist()

    # Reverse sort, like wallets do
    return sorted(txs, key=lambda d: d["blockheight"], reverse=True)
