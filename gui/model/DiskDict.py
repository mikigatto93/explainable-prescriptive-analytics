import json
import os

from gui.model.IO.IOManager import create_missing_folders


def get_df_path(name, key, ext='csv'):
    path = os.path.join(os.getcwd(), 'datasets_for_gui', '{}_{}.{}'.format(name, key, ext))
    create_missing_folders(path)
    return path


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
