import dash

from gui.app import app
from dash_extensions.enrich import Input, Output, State

from gui.presenters.Presenter import Presenter


class Router(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.pathname_list = [view.pathname for view in sorted(self.views.values(), key=lambda x: x.order)]
        self.pathname_list = self.pathname_list[0:]  # remove first element (BaseView, that has order=-1)

    def register_callbacks(self):

        @app.callback([Output(self.views['base'].IDs.GO_NEXT_LINK, 'href'),
                       Output(self.views['base'].IDs.GO_BACK_LINK, 'href')],
                      State(self.views['base'].IDs.LOCATION_URL, 'pathname'),
                      [Input(self.views['base'].IDs.GO_NEXT_BTN, 'n_clicks'),
                       Input(self.views['base'].IDs.GO_BACK_BTN, 'n_clicks')])
        def update_links(pathname, n_clicks_btn1, n_clicks_btn2):
            button_id = dash.ctx.triggered_id
            next_page = 0
            prev_page = 0
            for page_index, _ in enumerate(self.pathname_list):
                page_path = self.pathname_list[page_index]
                if page_path == pathname:
                    next_page = page_index + 1
                    prev_page = page_index - 1
                    if next_page == len(self.pathname_list):
                        next_page = -1

            if button_id == 'go_next_btn' and n_clicks_btn1 > 0:
                go_back = self.pathname_list[prev_page]
                if next_page == -1:
                    go_next = ''
                else:
                    go_next = self.pathname_list[next_page]
                return [go_next, go_back]
            elif button_id == 'go_back_btn' and n_clicks_btn2 > 0:
                go_next = self.pathname_list[next_page]
                if prev_page == -1:
                    go_back = ''
                else:
                    go_back = self.pathname_list[prev_page]
                return [go_next, go_back]
            elif n_clicks_btn1 == 0 and n_clicks_btn2 == 0:
                return [self.pathname_list[next_page], '']

        @app.callback(Output(self.views['base'].IDs.PAGE_CONTAINER, 'children'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def change_page(url):
            for view in self.views.values():
                if view.pathname == url:
                    return view.get_layout()

            return '404: Not Found'

        @app.callback([Output(self.views['base'].IDs.GO_NEXT_BTN, 'disabled'),
                       Output(self.views['base'].IDs.GO_BACK_BTN, 'disabled')],
                      [Input(self.views['base'].IDs.GO_NEXT_LINK, 'href'),
                       Input(self.views['base'].IDs.GO_BACK_LINK, 'href')])
        def disable_unreachable_links(go_next_href, go_back_href):
            go_next_disabled = False
            go_back_disabled = False
            if go_next_href == '':
                go_next_disabled = True
            elif go_back_href == '':
                go_back_disabled = True

            return [go_next_disabled, go_back_disabled]
