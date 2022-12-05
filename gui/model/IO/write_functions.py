import json

import joblib
import numpy as np


def write_json(data, path):
    with open(path, 'w') as j:
        json.dump(data, j)


def write_pickle(data, path):
    with open(path, 'wb') as f:
        joblib.dump(data, f)


def write_numpy(data, path):
    np.save(path, data)


def write_csv(data, path):
    data.to_csv(path, index=False)