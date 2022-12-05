from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform

app = DashProxy(name=__name__, transforms=[MultiplexerTransform(), NoOutputTransform()])

