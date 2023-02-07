import pathlib

import pytest
import tempfile

from gui.model.DiskDict import DiskDict

@pytest.fixture
def dd():
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = pathlib.Path(temp_dir.name)
    diskdict = DiskDict(temp_path, 'test_diskdict')
    yield diskdict
    temp_dir.cleanup()


def test_setitem(dd):
    dd['valid_key'] = {'data': 1}
    assert dd['valid_key'] == {'data': 1}


def test_getitem_error(dd):
    with pytest.raises(KeyError):
        assert dd['invalid_key']


def test_exists(dd):
    dd['valid_key'] = {'data': 1}
    assert dd.exists('valid_key')
    assert not dd.exists('invalid_key')


def test_iter(dd):
    dd['valid_key1'] = {'data': 1}
    dd['valid_key2'] = {'data': 2}
    dd['valid_key3'] = {'data': 3}
    dd['valid_key4'] = {'data': 4}
    dd['valid_key5'] = {'data': 5}

    index = 1
    for item in dd:
        assert item.content == {'data': index}
        assert item.key == 'valid_key{}'.format(index)
        index += 1


def test_delete(dd, capsys):
    dd.delete('invalid_key')
    output = capsys.readouterr().out
    message = output.split(':')[0]
    assert message == 'An error occurred during file deletion'

    dd['valid_key'] = {'data': 1}
    assert dd.exists('valid_key')
    dd.delete('valid_key')
    assert not dd.exists('valid_key')
