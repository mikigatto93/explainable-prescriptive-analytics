import datetime

from gui.model.Experiment import Experiment, build_experiment_from_dict


def test_experiment_init():
    ts = datetime.datetime.now()
    exp = Experiment(ex_name='test1',
                     kpi='Total time',
                     id='ID_COL',
                     timestamp='TIMESTAMP_COL',
                     activity='ACTIVITY_COL',
                     resource=None,
                     act_to_opt='ACT_TO_OPT',
                     out_thrs=0.05,
                     creation_timestamp=str(ts))

    assert exp.pred_column == 'remaining_time'
    assert exp.act_to_opt is None

    exp = Experiment(ex_name='test1',
                     kpi='Minimize activity occurrence',
                     id='ID_COL',
                     timestamp='TIMESTAMP_COL',
                     activity='ACTIVITY_COL',
                     resource=None,
                     act_to_opt='ACT_TO_OPT',
                     out_thrs=0.05,
                     creation_timestamp=str(ts))

    assert exp.pred_column == 'independent_activity'
    assert exp.act_to_opt is not None


def test_experiment_to_dict():
    ts = datetime.datetime.now()
    exp = Experiment(ex_name='test1',
                     kpi='Total time',
                     id='ID_COL',
                     timestamp='TIMESTAMP_COL',
                     activity='ACTIVITY_COL',
                     resource=None,
                     act_to_opt='ACT_TO_OPT',
                     out_thrs=0.05,
                     creation_timestamp=str(ts))

    assert exp.to_dict() == {'act_to_opt': None,
                             'activity': 'ACTIVITY_COL',
                             'creation_timestamp': str(ts),
                             'ex_name': 'test1',
                             'id': 'ID_COL',
                             'kpi': 'Total time',
                             'out_thrs': 0.05,
                             'pred_column': 'remaining_time',
                             'resource': None,
                             'timestamp': 'TIMESTAMP_COL'}

    exp = Experiment(ex_name='test1',
                     kpi='Minimize activity occurrence',
                     id='ID_COL',
                     timestamp='TIMESTAMP_COL',
                     activity='ACTIVITY_COL',
                     resource=None,
                     act_to_opt='ACT_TO_OPT',
                     out_thrs=0.05,
                     creation_timestamp=str(ts))

    assert exp.to_dict() == {'act_to_opt': 'ACT_TO_OPT',
                             'activity': 'ACTIVITY_COL',
                             'creation_timestamp': str(ts),
                             'ex_name': 'test1',
                             'id': 'ID_COL',
                             'kpi': 'Minimize activity occurrence',
                             'out_thrs': 0.05,
                             'pred_column': 'independent_activity',
                             'resource': None,
                             'timestamp': 'TIMESTAMP_COL'}


def test_experiment_build_from_dict():
    ts = datetime.datetime.now()
    dict1 = {'act_to_opt': None,
             'activity': 'ACTIVITY_COL',
             'creation_timestamp': str(ts),
             'ex_name': 'test1',
             'id': 'ID_COL',
             'kpi': 'Total time',
             'out_thrs': 0.05,
             'pred_column': 'remaining_time',
             'resource': None,
             'timestamp': 'TIMESTAMP_COL'}

    ex1 = build_experiment_from_dict(dict1)

    assert ex1.__dict__ == dict1
