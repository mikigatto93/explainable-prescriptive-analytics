import os

from app import app


from gui.model.Recommender import Recommender
from gui.model.RunDataSource import RunDataSource
from gui.model.ProgressLogger.TimeLogger import TimeLogger
from gui.model.TrainDataSource import TrainDataSource
from gui.model.Trainer import Trainer
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


def startup_gui():
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


if __name__ == "__main__":
    startup_gui()

    # import gui
    # from gui.model.Experiment import build_experiment_from_dict, Experiment
    # from gui.model.Trainer import Trainer
    # from gui.model.ProgressLogger.TrainProgLogger import TrainProgLogger
    # ex_info = gui.model.Experiment.build_experiment_from_dict(
    #     {"ex_name": "test_xes_manuale", "kpi": "Total time", "id": "case:concept:name",
    #      "timestamp": "time:timestamp", "activity": "concept:name",
    #      "resource": None, "act_to_opt": None, "out_thrs": 0.03,
    #      "pred_column": "remaining_time"})
    #
    # data_source = TrainDataSource('F:/datasets/stage-datasets/Hospital_log.xes/Hospital_log.xes')
    #
    # print(ex_info)
    # trainer = Trainer(ex_info, data_source)
    # #self.progress_logger.clear_stack()
    # #self.progress_logger.add_to_stack('Preparing dataset...')
    #
    # trainer.prepare_dataset()
    #
    # # self.progress_logger.add_to_stack('Starting training...')
    # trainer.train(TrainProgLogger('train_progress_manual.tmp'))
    #
    # # self.progress_logger.add_to_stack('Generating variables...')
    # trainer.generate_variables()

    app.run_server(debug=True, dev_tools_hot_reload=False)
