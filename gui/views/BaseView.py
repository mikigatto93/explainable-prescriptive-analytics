import uuid

from strenum import StrEnum
from dash_extensions.enrich import html, dcc

from app import CONFIG
from gui.views.View import View


class IDs(StrEnum):
    EXPL_SORT_METHOD = 'explanations_sort_method_store',
    PRED_SORT_METHOD = 'predictions_sort_method_store',
    KEEP_ALIVE_INTERVAL = 'keep_alive_interval',
    RUN_FILE_PATH_STORE = 'run_file_path_store',
    TRAIN_FILE_PATH_STORE = 'train_file_path_store',
    USER_ID = 'user_id',
    ERRORS_MANAGER_STORE_EXPLAIN = 'errors_manager_store_explain',
    ERRORS_MANAGER_STORE_RUN = 'errors_manager_store_run',
    XES_COLUMNS_DATA_STORE = 'xes_cols_store',
    DOWNLOAD_TRAIN = 'download_train_elem',
    START_TRAINING_CONTROLLER = 'start_trainig_controller_store',
    ERRORS_MANAGER_STORE_TRAIN = 'errors_manager_store_train',
    EXPLANATION_QUANTITY_STORE = 'expl_qnt_store',
    ARROW_CONTROLLER_STORE = 'arrow_controller_store',
    ACT_TO_EXPLAIN_STORE = 'act_to_explain_store',
    GO_NEXT_LINK = 'go_next_link',
    GO_NEXT_BTN = 'go_next_btn',
    GO_BACK_LINK = 'go_back_link',
    GO_BACK_BTN = 'go_back_btn',
    PAGE_CONTAINER = 'page_container',
    LOCATION_URL = 'location_url',
    EXPERIMENT_DATA_STORE = 'ex_data_store',
    TRACE_ID_TO_EXPLAIN_STORE = 'trace_id_to_explain_store',


class BaseView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = IDs

    def get_layout(self):
        return html.Div(
            [
                html.Div(
                    dcc.Link(
                        children=[html.Button('>', n_clicks=0, id=self.IDs.GO_NEXT_BTN, className='skip_page_btn')],
                        href='', id=self.IDs.GO_NEXT_LINK
                    ),
                    className='right_col'),
                html.Div(id=self.IDs.PAGE_CONTAINER, children=[], className='main_content'),
                html.Div(
                    dcc.Link(
                        children=[html.Button('<', n_clicks=0, id=self.IDs.GO_BACK_BTN, className='skip_page_btn')],
                        href='', id=self.IDs.GO_BACK_LINK
                    ),
                    className='left_col'),
                dcc.Location(id=self.IDs.LOCATION_URL, refresh=False),
                dcc.Store(id=self.IDs.EXPERIMENT_DATA_STORE, data=None),
                dcc.Store(id=self.IDs.TRACE_ID_TO_EXPLAIN_STORE, data=None),
                dcc.Store(id=self.IDs.ACT_TO_EXPLAIN_STORE, data=None),
                dcc.Store(id=self.IDs.ARROW_CONTROLLER_STORE, data=None),
                dcc.Store(id=self.IDs.EXPLANATION_QUANTITY_STORE, data=None),
                dcc.Store(id=self.IDs.ERRORS_MANAGER_STORE_TRAIN, data=None),
                dcc.Store(id=self.IDs.ERRORS_MANAGER_STORE_RUN, data=None),
                dcc.Store(id=self.IDs.ERRORS_MANAGER_STORE_EXPLAIN, data=None),
                dcc.Store(id=self.IDs.START_TRAINING_CONTROLLER),
                dcc.Store(id=self.IDs.XES_COLUMNS_DATA_STORE, data=None),
                dcc.Store(id=self.IDs.TRAIN_FILE_PATH_STORE, data=None),
                dcc.Store(id=self.IDs.RUN_FILE_PATH_STORE, data=None),
                dcc.Store(id=self.IDs.USER_ID, data=str(uuid.uuid4())),
                # dcc.Store(id=self.IDs.EXPLANATION_QUANTITY_STORE, data=None),
                dcc.Store(id=self.IDs.EXPL_SORT_METHOD, data=None),
                dcc.Interval(id=self.IDs.KEEP_ALIVE_INTERVAL,
                             interval=CONFIG['KEEP_ALIVE_SIGNAL_MSEC_INTERVAL'], n_intervals=0),
                dcc.Download(id=self.IDs.DOWNLOAD_TRAIN),
            ],
            className='container'
        )
