import json

import joblib
import pandas as pd
from numpy import np


def read_json(path, **kwargs):
    with open(path) as j:
        return json.load(j)


def read_pickle(path, **kwargs):
    with open(path, 'rb') as f:
        return joblib.load(f)


def read_numpy(path, **kwargs):
    return np.load(path)


def read_csv(path, **kwargs):
    return pd.read_csv(path, low_memory=False, **kwargs)


def read_txt(path, **kwargs):
    with open(path) as f:
        ls = f.readlines()
        d = {}
        for li in ls:
            k, v = li.split(':')
            d[k.strip()] = v.strip()
        return d