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
