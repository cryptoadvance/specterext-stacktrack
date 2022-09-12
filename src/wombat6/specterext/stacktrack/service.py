from decimal import *
import logging

from flask import current_app as app
from flask_apscheduler import APScheduler
import pandas as pd

from cryptoadvance.specter.services.service import Service, devstatus_alpha, devstatus_prod, devstatus_beta
# A SpecterError can be raised and will be shown to the user as a red banner
from cryptoadvance.specter.specter_error import SpecterError
from cryptoadvance.specter.wallet import Wallet

logger = logging.getLogger(__name__)


class StacktrackService(Service):
    id = "stacktrack"
    name = "StackTrack"
    icon = "stacktrack/img/ghost.png"
    logo = "stacktrack/img/logo.jpeg"
    desc = "Where a stacktrack grows bigger."
    has_blueprint = True
    blueprint_module = "wombat6.specterext.stacktrack.controller"
    devstatus = devstatus_alpha
    isolated_client = False

    # TODO: As more Services are integrated, we'll want more robust categorization and sorting logic
    sort_priority = 2

    # ServiceEncryptedStorage field names for this service
    # Those will end up as keys in a json-file
    SPECTER_WALLET_ALIAS = "wallet"

    SATS_PER_BTC = 100_000_000

    def callback_after_serverpy_init_app(self, scheduler: APScheduler):
        def every5seconds(hello, world="world"):
            with scheduler.app.app_context():
                print(f"Called {hello} {world} every5seconds")
        # Here you can schedule regular jobs. triggers can be one of "interval", "date" or "cron"
        # Examples:
        # interval: https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html
        # scheduler.add_job("every5seconds4", every5seconds, trigger='interval', seconds=5, args=["hello"])
        
        # Date: https://apscheduler.readthedocs.io/en/3.x/modules/triggers/date.html
        # scheduler.add_job("MyId", my_job, trigger='date', run_date=date(2009, 11, 6), args=['text'])
        
        # cron: https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
        # sched.add_job("anotherID", job_function, trigger='cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2014-05-30')
        
        # Maybe you should store the scheduler for later use:
        self.scheduler = scheduler
        
    # There might be other callbacks you're interested in. Check the callbacks.py in the specter-desktop source.
    # if you are, create a method here which is "callback_" + callback_id

    @classmethod
    def get_associated_wallet(cls) -> Wallet:
        """Get the Specter `Wallet` that is currently associated with this service"""
        service_data = cls.get_current_user_service_data()
        if not service_data or cls.SPECTER_WALLET_ALIAS not in service_data:
            # Service is not initialized; nothing to do
            return
        try:
            return app.specter.wallet_manager.get_by_alias(
                service_data[cls.SPECTER_WALLET_ALIAS]
            )
        except SpecterError as e:
            logger.debug(e)
            # Referenced an unknown wallet
            # TODO: keep ignoring or remove the unknown wallet from service_data?
            return

    @classmethod
    def set_associated_wallet(cls, wallet: Wallet):
        """Set the Specter `Wallet` that is currently associated with this Service"""
        cls.update_current_user_service_data({cls.SPECTER_WALLET_ALIAS: wallet.alias})

    @classmethod
    def build_balance_df(cls, wallet: Wallet) -> pd.DataFrame:
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
