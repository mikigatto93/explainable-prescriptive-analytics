import os
import pathlib
import tempfile

import pytest

from gui.model.ProgressLogger.RunProgLogger import RunProgLogger, build_RunProgLogger_from_dict


@pytest.fixture
def log():
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = pathlib.Path(temp_dir.name)
    yield RunProgLogger('test_run_logger', base_path=temp_path), temp_dir
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
        'file_name': 'test_run_logger.prog',
        'file_path': os.path.join(temp_path, 'test_run_logger.prog')
    }


def test_free(log, capsys):
    log[0].free()
    assert not os.path.isfile(log[0].file_path)


def test_write(log):
    log_entry = '17%|█▋        | 134/782 [00:19<01:21,  7.98it/s, loss=0.375 ]'
    log[0].write(log_entry)
    output = log[0].get_from_stack()
    assert output == 'Traces analyzed: 134/782, (17%)'


def test_build_runlogger(log):
    temp_path = pathlib.Path(log[1].name)
    dict_obj = {
        'file_name': 'test_run_logger.prog',
        'file_path': os.path.join(temp_path, 'test_run_logger.prog')
    }

    built_log = build_RunProgLogger_from_dict(dict_obj)
    assert built_log.__dict__ == log[0].__dict__
