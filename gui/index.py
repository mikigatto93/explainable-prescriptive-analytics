from app import app
from model.Trainer import Trainer
from presenters.Router import Router
from presenters.TrainPresenter import TrainPresenter
from views.BaseView import BaseView
from views.ExplainView import ExplainView
from views.RunView import RunView
from views.TrainView import TrainView


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
}, Trainer())

app.layout = base_view.get_layout()

router.register_callbacks()
train_pres.register_callbacks()

if __name__ == "__main__":
    app.run_server(debug=True)