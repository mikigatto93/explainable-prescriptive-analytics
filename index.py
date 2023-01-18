import os

from app import app, socketio
from flask import request
from flask_socketio import SocketIO, emit

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

    app.layout = base_view.get_layout()

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

    router.register_callbacks()
    train_pres.register_callbacks()
    run_pres.register_callbacks()
    explain_pres.register_callbacks()


@socketio.on('connect')
def connect(auth):
    print('connected: {}'.format(request.sid))
    emit('socket:id', request.sid)

@socketio.on('disconnect')
def disconnect():
    print('disconnected: {}'.format(request.sid))


if __name__ == "__main__":
    startup_gui()
    socketio.run(app.server, port=8050, debug=True, host='0.0.0.0')

    # app.run_server(debug=True, dev_tools_hot_reload=False, port=8050, host='0.0.0.0')
