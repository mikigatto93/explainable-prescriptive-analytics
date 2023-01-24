#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 17:29:54 2022

@author: padela
"""

import catboost
from catboost import *
import shap

shap.initjs()

import urllib3

urllib3.disable_warnings()
import pandas as pd

import matplotlib.pyplot as plt

plt.style.use('ggplot')

import datetime


def evaluate_shap_vals(trace, model, X_test, case_id_name):
    # t1 = datetime.datetime.now()
    expl_trace = trace.iloc[-2:]
    print('----------------')
    print(expl_trace)
    print('----------------')
    expl_trace = expl_trace[[i for i in expl_trace.columns if i != case_id_name]]
    print('----------------')
    print(expl_trace)
    print('----------------')
    expl_trace = expl_trace[list(model.feature_names_)]
    print(list(model.feature_names_))
    print('----------------')
    print(expl_trace)
    print('----------------')
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(expl_trace.iloc[1:])
    # t2 = datetime.datetime.now()
    # print(t2-t1)
    return shap_values[0]


# def evaluate_shap_vals(trace, model, X_test, case_id_name):
#     trace = trace.iloc[-1]
#     X_test.rename(columns={'time_from_midnight': 'daytime'}, inplace=True)
#     X_test = X_test[trace.index]
#     df = X_test.append(trace).reset_index(drop=True)
#     df = df[[i for i in X_test.columns if i != case_id_name]]
#     # df = df[[list(model.feature_names_)]]
#     explainer = shap.TreeExplainer(model)
#     shap_values = explainer.shap_values(df)
#     return shap_values[-1]


def plot_explanations_recs(groundtruth_explanation, explanations, idxs_chosen, last, experiment_name, trace_idx, act):
    # Python dictionary
    expl_df = {"Following Recommendation": [i for i in explanations[idxs_chosen].sort_values(ascending=False).values],
               "Actual Value": [i for i in groundtruth_explanation[idxs_chosen].sort_values(ascending=False).values]};

    last = last[idxs_chosen]

    feature_names = [str(i) for i in last.index]
    feature_values = [str(i) for i in last.values]

    index = [feature_names[i] + '=' + feature_values[i] for i in range(len(feature_values))]
    # Python dictionary into a pandas DataFrame

    dataFrame = pd.DataFrame(data=expl_df)

    dataFrame.index = index

    dataFrame.plot.barh(rot=0,
                        title=f"How variables contribution on \n KPI changes, ",
                        color=['darkgreen', 'darkred'])
    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)
    plt.tight_layout(pad=0)
    plt.savefig(f'figure.png')
    plt.close()
