import os
import time
import datetime

from app import app, USERS, CONFIG
from gui.model.DiskDict import DiskDict
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

base_view = BaseView()
train_view = TrainView('/', 0)
run_view = RunView('/run', 1)
explain_view = ExplainView('/explain', 2)

app.layout = base_view.get_layout

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


def check_timestamps():
    while True:
        server_now_ts = datetime.datetime.now(datetime.timezone.utc)
        for u in USERS:
            client_last_ts = datetime.datetime.fromisoformat(u.content)
            if (server_now_ts - client_last_ts).total_seconds() > CONFIG['MAX_KEEP_ALIVE_SEC_TIME_DIFFERENCE']:
                print('--------------------------------------------------')
                print('user: {}, server: {}, client: {}, diff: {}'.format(
                    u.key, server_now_ts,
                    client_last_ts,
                    (server_now_ts - client_last_ts).total_seconds())
                )
                train_pres.clear_user_data(u.key)
                run_pres.clear_user_data(u.key)
                explain_pres.clear_user_data(u.key)
                USERS.delete(u.key)
                print('--------------------------------------------------')
        time.sleep(CONFIG['CLEAR_DATA_SERVER_SEC_INTERVAL'])


if __name__ == "__main__":
    import threading
    import waitress

    t = threading.Thread(target=check_timestamps)
    t.start()

    waitress.serve(app.server, port=8050, host='0.0.0.0')
    # app.run_server(debug=False, dev_tools_hot_reload=False, port=8050, host='0.0.0.0')
