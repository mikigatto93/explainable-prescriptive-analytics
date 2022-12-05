from strenum import StrEnum
from dash_extensions.enrich import html, dcc

from views.View import View


class ExplainView(View):
    class IDs(StrEnum):
        pass

    def get_layout(self):
        return html.Div([
            html.H1('Explain')
        ])