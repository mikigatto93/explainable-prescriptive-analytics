from strenum import StrEnum
from dash_extensions.enrich import html, dcc

from gui.views.View import View


class _IDs(StrEnum):
    GO_NEXT_LINK = 'go_next_link',
    GO_NEXT_BTN = 'go_next_btn',
    GO_BACK_LINK = 'go_back_link',
    GO_BACK_BTN = 'go_back_btn',
    PAGE_CONTAINER = 'page_container',
    LOCATION_URL = 'location_url',
    EXPERIMENT_DATA_STORE = 'ex_data_store',


class BaseView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = _IDs

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
                dcc.Store(id=self.IDs.EXPERIMENT_DATA_STORE, data=None)
            ],
            className='container'
        )
