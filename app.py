import os

from dash.long_callback import DiskcacheLongCallbackManager
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform
import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

assets_folder_path = os.path.join(os.getcwd(), 'gui/assets')
app = DashProxy(name=__name__,
                assets_folder=assets_folder_path,
                long_callback_manager=long_callback_manager,
                transforms=[MultiplexerTransform(), NoOutputTransform()])

