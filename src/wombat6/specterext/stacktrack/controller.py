import logging

from flask import redirect, render_template, request, url_for
from flask import current_app as app
from flask_login import login_required, current_user
import plotly.graph_objects as go

from cryptoadvance.specter.services import callbacks
from cryptoadvance.specter.services.controller import user_secret_decrypted_required
from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.wallet import Wallet

from .plots import Plots
from .service import StacktrackService

logger = logging.getLogger(__name__)

stacktrack_endpoint = StacktrackService.blueprint

SPANS_TO_PLOT_BUILDERS = {
    "1d": Plots.build_1d_plot,
    "1w": Plots.build_1w_plot,
    "1m": Plots.build_1m_plot,
    "1y": Plots.build_1y_plot,
    "all": Plots.build_all_plot,
}


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
@user_secret_decrypted_required
def index():
    return render_template("stacktrack/index.jinja")


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


@stacktrack_endpoint.route("/wallet_chart", methods=["GET"])
# Disabling these since the wallet endpoints don't seem to require them
# @login_required
# @user_secret_decrypted_required
def stacktrack_wallet_chart() -> str:
    wallet_alias = request.args.get("wallet_alias")
    span = request.args.get("span")
    span = "1y" if span is None else span
    wallet = app.specter.wallet_manager.get_by_alias(wallet_alias)
    balance_plot: go.Figure = SPANS_TO_PLOT_BUILDERS[span](wallet)
    return render_template(
        "stacktrack/chart.jinja",
        wallet=wallet,
        active_span=span,
        plot=balance_plot,
    )
