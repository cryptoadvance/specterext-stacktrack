import logging

from flask import current_app as app, url_for
from flask_apscheduler import APScheduler

from cryptoadvance.specter.services.service import Service, devstatus_alpha, devstatus_prod, devstatus_beta
# A SpecterError can be raised and will be shown to the user as a red banner
from cryptoadvance.specter.specter_error import SpecterError
from cryptoadvance.specter.wallet import Wallet
from cryptoadvance.specter.server_endpoints.wallets.wallets_vm import WalletsOverviewVm


logger = logging.getLogger(__name__)


class StacktrackService(Service):
    id = "stacktrack"
    name = "StackTrack"
    icon = "stacktrack/img/chart.png"
    logo = "stacktrack/img/logo.jpeg"
    desc = "A chart to visualize your Bitcoin stack over time"
    has_blueprint = True
    blueprint_module = "cryptoadvance.specterext.stacktrack.controller"
    devstatus = devstatus_alpha
    isolated_client = False

    SHOW_OVERVIEW_CHART = "show_overview_chart"

    # TODO: As more Services are integrated, we'll want more robust categorization and sorting logic
    sort_priority = 2

    # ServiceEncryptedStorage field names for this service
    # Those will end up as keys in a json-file
    SPECTER_WALLET_ALIAS = "wallet"

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

    # 'type' object not subscriptable in Python 3.7, so just use bare list.
    # def callback_add_wallettabs(self) -> list[dict[str, str]]:
    def callback_add_wallettabs(self) -> list:
        return [{
            "title": "Chart",
            "endpoint": "stacktrack_wallet_chart",
        }]

    def callback_adjust_view_model(self, view_model: WalletsOverviewVm):
        if type(view_model) == WalletsOverviewVm:
            # Redirect to our custom StackTrack controller so we can generate a chart.
            view_model.wallets_overview_redirect = url_for("stacktrack_endpoint.wallets_overview")
        return view_model

    @classmethod
    def get_show_overview_chart(cls) -> str:
        service_data = cls.get_current_user_service_data()
        if not service_data or cls.SHOW_OVERVIEW_CHART not in service_data:
            # Service is not initialized; nothing to do
            return "no"
        try:
            return service_data[cls.SHOW_OVERVIEW_CHART]
            
        except Exception as e:
            logger.exception(e)
            # Referenced an unknown wallet
            # TODO: keep ignoring or remove the unknown wallet from service_data?
            return "no"

    @classmethod
    def set_show_overview_chart(cls, value: bool):
        """Set the Specter `Wallet` that is currently associated with this Service"""
        cls.update_current_user_service_data({cls.SHOW_OVERVIEW_CHART: value})
