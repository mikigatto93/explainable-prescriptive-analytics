import os.path

import pytest

from gui.model.IO.IOManager import create_missing_folders, get_experiment_folders_list, Paths


def test_create_missing_folders():
    test_file_path = 'folder1/folder2/folder3/test_file.txt'

    with pytest.raises(FileNotFoundError):
        with open(test_file_path, 'w') as f:
            f.write('test')

    create_missing_folders(test_file_path)
    with open(test_file_path, 'w') as f:
        f.write('test')

    assert os.path.isdir(os.path.split(test_file_path)[0])
    assert os.path.isfile(test_file_path)

    os.remove(test_file_path)
    head, _ = os.path.split(test_file_path)
    while os.path.isdir(head):
        os.rmdir(head)
        head, _ = os.path.split(head)


def test_get_experiment_folders_list():
    folder_list = get_experiment_folders_list('test_experiments_dir')
    assert folder_list == [{'ex_name': 'ex1', 'path': 'test_experiments_dir\\ex1##123'},
                           {'ex_name': 'ex2', 'path': 'test_experiments_dir\\ex2##234'},
                           {'ex_name': 'test',
                            'path': 'test_experiments_dir\\test--10-02-2023_21-48-26_541142+0000'}]


def test_path_maker():
    paths = Paths(ex_name='test', main_path='main_dir')
    test_dict_dir = {
        'path1': 'f1.txt',
        'path2': 'f2.txt',
        'path3': 'f3.txt',
    }

    path_dict_out = paths.path_maker('test_path', test_dict_dir)
    assert path_dict_out == {'path1': 'main_dir\\test--\\test_path\\f1.txt',
                             'path2': 'main_dir\\test--\\test_path\\f2.txt',
                             'path3': 'main_dir\\test--\\test_path\\f3.txt'}
