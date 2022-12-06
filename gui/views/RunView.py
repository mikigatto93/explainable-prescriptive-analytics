from strenum import StrEnum
from dash_extensions.enrich import html, dcc

from gui.views.View import View


class RunView(View):
    class IDs(StrEnum):
        pass

    def get_layout(self):
        return html.Div([
            html.H1('Run')
        ])