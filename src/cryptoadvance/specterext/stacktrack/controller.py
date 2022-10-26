import logging

from flask import redirect, render_template, request, url_for
from flask import current_app as app
from flask_login import login_required, current_user
import plotly.graph_objects as go

from cryptoadvance.specter.services import callbacks
from cryptoadvance.specter.services.controller import user_secret_decrypted_required
from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.wallet import Wallet

from .helpers import pbuild
from .service import StacktrackService

logger = logging.getLogger(__name__)

stacktrack_endpoint = StacktrackService.blueprint


def ext() -> StacktrackService:
    """ convenience for getting the extension-object"""
    return app.specter.ext["stacktrack"]


def specter() -> Specter:
    """ convenience for getting the specter-object"""
    return app.specter


@stacktrack_endpoint.context_processor
def inject_common_stuff():
    """Can be used in all jinja2 templates"""
    return {
        "ext_wallettabs": app.specter.service_manager.execute_ext_callbacks(
            callbacks.add_wallettabs
        ),
    }


@stacktrack_endpoint.route("/")
@login_required
def index():
    return render_template("stacktrack/index.jinja")


# @stacktrack_endpoint.route("/wallet_chart", methods=["GET"])
@stacktrack_endpoint.route("/wallet/<wallet_alias>/chart", methods=["GET"])
@login_required
def stacktrack_wallet_chart(wallet_alias: str) -> str:
    span = request.args.get("span")
    span = "1y" if span is None else span
    wallet = app.specter.wallet_manager.get_by_alias(wallet_alias)
    balance_plot: go.Figure = getattr(pbuild, f"build_plot_{span}")(wallet)
    return render_template(
        "stacktrack/chart.jinja",
        wallet_alias=wallet_alias,
        wallet=wallet,
        ext_wallettabs=app.specter.service_manager.execute_ext_callbacks(callbacks.add_wallettabs),
        active_span=span,
        plot=balance_plot,
    )
