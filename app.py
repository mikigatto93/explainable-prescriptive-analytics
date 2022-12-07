import os

from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform


assets_folder_path = os.path.join(os.getcwd(), 'gui/assets')
app = DashProxy(name=__name__,
                assets_folder=assets_folder_path,
                transforms=[MultiplexerTransform(), NoOutputTransform()])

