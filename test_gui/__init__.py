from app import app

from gui.presenters.Router import Router
from gui.presenters.RunPresenter import RunPresenter
from gui.presenters.TrainPresenter import TrainPresenter
from gui.presenters.ExplainPresenter import ExplainPresenter
from gui.views.BaseView import BaseView
from gui.views.ExplainView import ExplainView
from gui.views.RunView import RunView
from gui.views.TrainView import TrainView
import dash_uploader as du

import pytest
from dash.testing.browser import Browser
from selenium import webdriver


def startup_gui():
    du.configure_upload(app, '/dummy_folder')
    base_view = BaseView()
    train_view = TrainView('/', 0)
    run_view = RunView('/run', 1)
    explain_view = ExplainView('/explain', 2)

    router_ = Router({
        'base': base_view,
        'train': train_view,
        'run': run_view,
        'explain': explain_view
    })

    train_pres_ = TrainPresenter({
        'base': base_view,
        'train': train_view,
    })

    run_pres_ = RunPresenter({
        'base': base_view,
        'run': run_view,
    })

    explain_pres_ = ExplainPresenter({
        'base': base_view,
        'explain': explain_view,
    })

    app.layout = base_view.get_layout()

    router_.register_callbacks()
    train_pres_.register_callbacks()
    run_pres_.register_callbacks()
    explain_pres_.register_callbacks()

    return router_, train_pres_, run_pres_, explain_pres_


router, train_pres, run_pres, explain_pres = startup_gui()

callbacks_list = list(app.blueprint.callbacks)
CALLBACKS = {}

for callback in callbacks_list:
    CALLBACKS[callback.f.__name__] = callback.f


#  Personal implementation with the setup of the webdriver with a custom path
# (no adding to PATH needed)
CHROME_WEBDRIVER_PATH = r'F:\STAGE\test\chromedriver.exe'
class MyDashComposite(Browser):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self.server = server

    def get_webdriver(self):
        return self._get_chrome()

    def _get_chrome(self):
        return webdriver.Chrome(executable_path=CHROME_WEBDRIVER_PATH)

    def start_server(self, app, **kwargs):
        """Start the local server with app."""

        # start server with app and pass Dash arguments
        self.server(app, **kwargs)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url


@pytest.fixture
def dash_duo2(request, dash_thread_server, tmpdir) -> MyDashComposite:
    with MyDashComposite(
        dash_thread_server,
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as Mdc:
        yield Mdc
