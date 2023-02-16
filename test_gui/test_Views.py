import os
import time

import pytest

from gui.views.BaseView import IDs as baseIDs
from gui.views.TrainView import IDs as trainIDs
from gui.views.RunView import IDs as runIDs
from gui.views.ExplainView import IDs as explainIDs

from app import app

from test_gui import dash_duo2


def load_test_dataset(sel_driver, file_name, page):
    if page == 'train':
        sel_driver.wait_for_element_by_id(trainIDs.TRAIN_FILE_UPLOADER)
        input_id = trainIDs.TRAIN_FILE_UPLOADER + '-upload'
    elif page == 'run':
        sel_driver.wait_for_element_by_id(runIDs.RUN_FILE_UPLOADER)
        input_id = runIDs.RUN_FILE_UPLOADER + '-upload'
    else:
        raise ValueError('page argument must be either "train" or "run", not {}'.format(page))
    upload_input_elem = sel_driver.find_element('input[name={}]'.format(input_id))
    test_file_path = os.path.join(os.getcwd(), 'test_datasets', file_name)
    upload_input_elem.send_keys(test_file_path)
    time.sleep(3)  # gives time to load the file


def test_001_go_next_and_go_back_disabled_at_start(dash_duo2):
    dash_duo2.start_server(app)
    dash_duo2.wait_for_element_by_id(baseIDs.GO_NEXT_BTN)
    dash_duo2.wait_for_element_by_id(baseIDs.GO_BACK_BTN)
    go_back_btn = dash_duo2.find_element('#' + baseIDs.GO_BACK_BTN)
    go_next_btn = dash_duo2.find_element('#' + baseIDs.GO_BACK_BTN)
    assert go_back_btn.is_enabled()
    assert go_next_btn.is_enabled()


def test_002_load_file_btn(dash_duo2):
    dash_duo2.start_server(app)
    load_test_dataset(dash_duo2, 'bac_train_red.csv', 'train')
    load_train_file_btn = dash_duo2.find_element('#' + trainIDs.LOAD_TRAIN_FILE_BTN)
    assert load_train_file_btn.is_displayed()


def test_003_load_file_btn_disabled_during_processing(dash_duo2):
    dash_duo2.start_server(app)
    load_test_dataset(dash_duo2, 'bac_train_red.csv', 'train')
    load_train_file_btn = dash_duo2.find_element('#' + trainIDs.LOAD_TRAIN_FILE_BTN)
    time.sleep(8)
    load_train_file_btn.click()
    time.sleep(1)
    assert not load_train_file_btn.is_enabled()


def test_004_train_btn_disabled_during_processing(dash_duo2):
    dash_duo2.start_server(app)
    load_test_dataset(dash_duo2, 'bac_train_red.csv', 'train')
    load_train_file_btn = dash_duo2.find_element('#' + trainIDs.LOAD_TRAIN_FILE_BTN)
    time.sleep(8)
    load_train_file_btn.click()

    fade_all_controls = dash_duo2.find_element('#' + trainIDs.FADE_ALL_TRAIN_CONTROLS)
    timeout = 15
    i = 0
    while not fade_all_controls.is_displayed() and i < timeout:
        time.sleep(1)
        i += 1
    if i > timeout:
        raise TimeoutError()

    dash_duo2.find_element('#' + trainIDs.EXPERIMENT_NAME_TEXTBOX).send_keys('test_experiment')
    dash_duo2.find_element('#' + trainIDs.ID_DROPDOWN + ' input').send_keys('REQUEST_ID')
    dash_duo2.find_element('.Select-menu-outer').click()
    dash_duo2.find_element('#' + trainIDs.ACTIVITY_DROPDOWN + ' input').send_keys('ACTIVITY')
    dash_duo2.find_element('.Select-menu-outer').click()
    dash_duo2.find_element('#' + trainIDs.TIMESTAMP_DROPDOWN + ' input').send_keys('START_DATE')
    dash_duo2.find_element('.Select-menu-outer').click()
    dash_duo2.find_element('#' + trainIDs.NEXT_SELECT_PHASE_TRAIN_BTN).click()

    time.sleep(1)

    dash_duo2.find_elements('input[type=radio]')[0].click()

    time.sleep(1)
    dash_duo2.find_element('#' + trainIDs.START_TRAINING_BTN).click()
    time.sleep(2)
    assert not dash_duo2.find_element('#' + trainIDs.START_TRAINING_BTN).is_enabled()
    dash_duo2.driver.get('http://localhost:58050/run')


def test_005_process_btn(dash_duo2):
    dash_duo2.start_server(app)
    dash_duo2.driver.get('http://localhost:58050/run')
    go_back_btn = dash_duo2.find_element('#' + baseIDs.GO_BACK_BTN)
    go_next_btn = dash_duo2.find_element('#' + baseIDs.GO_BACK_BTN)
    load_test_dataset(dash_duo2, 'bac_train_red.csv', 'run')
    assert not go_next_btn.is_enabled()
    time.sleep(1)
    load_log_btn = dash_duo2.find_element('#' + runIDs.LOAD_RUN_FILE_BTN)
    load_log_btn.click()
    time.sleep(1)
    assert not load_log_btn.is_enabled()
    assert not go_back_btn.is_enabled()


def test_006_generate_btn(dash_duo2):
    dash_duo2.start_server(app)
    dash_duo2.driver.get('http://localhost:58050/run')
    go_back_btn = dash_duo2.find_element('#' + baseIDs.GO_BACK_BTN)
    go_next_btn = dash_duo2.find_element('#' + baseIDs.GO_BACK_BTN)
    load_test_dataset(dash_duo2, 'bac_train_red.csv', 'run')
    time.sleep(1)
    load_log_btn = dash_duo2.find_element('#' + runIDs.LOAD_RUN_FILE_BTN)
    load_log_btn.click()
    time.sleep(8)
    generate_btn = dash_duo2.find_element('#' + runIDs.GENERATE_PREDS_BTN)
    assert generate_btn.is_enabled()
    generate_btn.click()
    time.sleep(2)
    assert not generate_btn.is_enabled()



