import json

import joblib
import numpy as np
import pandas as pd


def write_json(data, path):
    with open(path, 'w') as j:
        json.dump(data, j)


def write_pickle(data, path):
    with open(path, 'wb') as f:
        pd.to_pickle(data, f)


def write_numpy(data, path):
    np.save(path, data)


def write_csv(data, path):
    data.to_csv(path, index=False)


writer = {
    'json': write_json,
    'pkl': write_pickle,
    'pickle': write_pickle,
    'npy': write_numpy,
    'csv': write_csv,
}
