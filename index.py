import os

from app import app
from gui.model.Experiment import build_experiment_from_dict
from gui.model.Recommender import Recommender
from gui.model.RunDataSource import RunDataSource
from gui.model.ProgressLogger.TimeLogger import TimeLogger
from gui.presenters.Router import Router
from gui.presenters.RunPresenter import RunPresenter
from gui.presenters.TrainPresenter import TrainPresenter
from gui.presenters.ExplainPresenter import ExplainPresenter
from gui.views.BaseView import BaseView
from gui.views.ExplainView import ExplainView
from gui.views.RunView import RunView
from gui.views.TrainView import TrainView

import dash_uploader as du
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploaded_datasets')
du.configure_upload(app, UPLOAD_FOLDER)

base_view = BaseView()
train_view = TrainView('/', 0)
run_view = RunView('/run', 1)
explain_view = ExplainView('/explain', 2)

router = Router({
    'base': base_view,
    'train': train_view,
    'run': run_view,
    'explain': explain_view
})

train_pres = TrainPresenter({
    'base': base_view,
    'train': train_view,
})

run_pres = RunPresenter({
    'base': base_view,
    'run': run_view,
})

explain_pres = ExplainPresenter({
    'base': base_view,
    'explain': explain_view,
})

app.layout = base_view.get_layout()

router.register_callbacks()
train_pres.register_callbacks()
run_pres.register_callbacks()
explain_pres.register_callbacks()


# if __name__ == '__main__':
#     r = Recommender(build_experiment_from_dict({"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
#                                                 "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
#                                                 "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
#                                                 "pred_column": "remaining_time"}),
#                     RunDataSource('F:/datasets/stage-datasets/VINST_run.csv'))
#     r.prepare_dataset()
#     r.generate_recommendations(TimeLogger())


if __name__ == "__main__":
    app.run_server(debug=True)