import os

import dash
from dash.long_callback import DiskcacheLongCallbackManager
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform, CycleBreakerTransform
import diskcache


cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

assets_folder_path = os.path.join(os.getcwd(), 'gui/assets')
app = DashProxy(name=__name__,
                assets_folder=assets_folder_path,
                suppress_callback_exceptions=True,
                long_callback_manager=long_callback_manager,
                transforms=[MultiplexerTransform(), NoOutputTransform(), CycleBreakerTransform()])
