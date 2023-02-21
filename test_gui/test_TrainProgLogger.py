import os
import pathlib
import tempfile

import pytest

from gui.model.ProgressLogger.TrainProgLogger import TrainProgLogger, build_TrainProgLogger_from_dict


@pytest.fixture
def log():
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = pathlib.Path(temp_dir.name)
    yield TrainProgLogger('test_train_logger', base_path=temp_path), temp_dir
    temp_dir.cleanup()


def test_add_to_stack(log):
    log[0].add_to_stack('test_line')
    with open(log[0].file_path, 'r') as f:
        content = f.read()
    assert content == 'test_line'


def test_clear_stack(log):
    log[0].add_to_stack('test_line1')
    log[0].add_to_stack('test_line2')
    log[0].clear_stack()
    with open(log[0].file_path, 'r') as f:
        content = f.read()
    assert content == ''


def test_get_from_stack(log):
    log[0].add_to_stack('test_line1')
    log[0].add_to_stack('test_line2')
    output = log[0].get_from_stack()
    assert output == 'test_line2'

    log[1].cleanup()  # clear the file
    output = log[0].get_from_stack()
    assert output is None


def test_to_dict(log):
    temp_path = pathlib.Path(log[1].name)
    assert log[0].to_dict() == {
        'file_name': 'test_train_logger.prog',
        'file_path': os.path.join(temp_path, 'test_train_logger.prog')
    }


def test_free(log, capsys):
    log[0].free()
    assert not os.path.isfile(log[0].file_path)


def test_write(log):
    log_entry = '0:      learn: 0.6879879        total: 182ms    remaining: 1.64s'
    log[0].write(log_entry)
    output = log[0].get_from_stack()
    assert output == 'elapsed: 182ms, remaining: 1.64s'

    log[0].phase_number = 1
    log[0].write(log_entry)
    output = log[0].get_from_stack()
    assert output == '1/2 training phases, elapsed: 182ms, remaining: 1.64s'


def test_build_trainlogger(log):
    temp_path = pathlib.Path(log[1].name)
    dict_obj = {
        'file_name': 'test_train_logger.prog',
        'file_path': os.path.join(temp_path, 'test_train_logger.prog')
    }

    built_log = build_TrainProgLogger_from_dict(dict_obj)
    assert built_log.__dict__ == log[0].__dict__
