import datetime
import json
import os
import pathlib
import traceback
from dataclasses import dataclass

from gui.model.IO.IOManager import create_missing_folders


def get_df_path(name, key, ext='csv'):
    path = os.path.join(os.getcwd(), 'datasets_for_gui', '{}_{}.{}'.format(name, key, ext))
    create_missing_folders(path)
    return path


class ItemInfo:
    def __init__(self, entry, dict_entry_name):
        self.name = entry.name
        self.path = entry.path
        self.key = entry.name.replace(dict_entry_name + '_', '').split('.')[0]
        with open(entry.path, 'r') as f:
            self.content = json.loads(f.read())


class DiskDict:
    def __init__(self, base_path, name, create_path_at_init=False):
        self.base_path = base_path
        self.name = name
        if create_path_at_init and not os.path.exists(self.base_path):
            pathlib.Path(self.base_path).mkdir(parents=True, exist_ok=True)

    def __getitem__(self, key):
        try:
            with open(os.path.join(self.base_path, '{}_{}.json'.format(self.name, key)), 'r') as f:
                content = f.read()
                return json.loads(content)
        except OSError:
            raise KeyError('{} not found'.format(key))

    def __setitem__(self, key, value):
        path = os.path.join(self.base_path, '{}_{}.json'.format(self.name, key))
        create_missing_folders(path)
        with open(path, 'w') as f:
            f.write(json.dumps(value))

    def __iter__(self):
        with os.scandir(self.base_path) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file() and entry.name.startswith(self.name):
                    yield ItemInfo(entry, self.name)

    def exists(self, key):
        try:
            with open(os.path.join(self.base_path, '{}_{}.json'.format(self.name, key)), 'r') as f:
                pass
        except FileNotFoundError:
            return False

        return True

    def delete(self, key):
        path = os.path.join(self.base_path, '{}_{}.json'.format(self.name, key))
        try:
            os.remove(path)
        except FileNotFoundError as e:
            print('An error occurred during file deletion: ({})'.format(path))

