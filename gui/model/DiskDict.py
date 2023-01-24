import datetime
import json
import os
from dataclasses import dataclass

from gui.model.IO.IOManager import create_missing_folders


def get_df_path(name, key, ext='csv'):
    path = os.path.join(os.getcwd(), 'datasets_for_gui', '{}_{}.{}'.format(name, key, ext))
    create_missing_folders(path)
    return path


class ItemInfo:
    def __init__(self, entry):
        self.name = entry.name
        self.path = entry.path
        self.key = (entry.name.split('_')[-1]).split('.')[0]
        with open(entry.path, 'r') as f:
            self.content = json.loads(f.read())


class DiskDict:
    def __init__(self, base_path, name):
        self.base_path = base_path
        self.name = name

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
                    yield ItemInfo(entry)

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
        except OSError:
            print('An error occurred during file deletion: ({})'.format(path))


    # def __getitem__(self, key):
    #     try:
    #         with open(os.path.join(self.base_path, '{}_{}.json'.format(self.name, key)), 'r') as f:
    #             content = f.read()
    #             data = json.loads(content)
    #             if '__single_val__' in data:
    #                 data_to_return = data['__single_val__']
    #             else:
    #                 data_to_return = data
    #             del data_to_return['__system_timestamp__']
    #             return data_to_return
    #     except OSError:
    #         raise KeyError('{} not found'.format(key))
    #
    # def __setitem__(self, key, value):
    #     path = os.path.join(self.base_path, '{}_{}.json'.format(self.name, key))
    #     create_missing_folders(path)
    #     if not isinstance(value, dict):
    #         value_to_write = {'__single_val__': value}
    #     else:
    #         value_to_write = value
    #
    #     value_to_write['__system_timestamp__'] = str(datetime.datetime.now(datetime.timezone.utc))
    #     with open(path, 'w') as f:
    #         f.write(json.dumps(value_to_write))
    #
    # def get_timestamp(self, key):
    #     try:
    #         with open(os.path.join(self.base_path, '{}_{}.json'.format(self.name, key)), 'r') as f:
    #             content = f.read()
    #             data = json.loads(content)
    #             return data['__system_timestamp__']
    #     except OSError:
    #         raise KeyError('{} not found'.format(key))
