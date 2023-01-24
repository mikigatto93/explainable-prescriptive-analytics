import os

from dash.long_callback import DiskcacheLongCallbackManager
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform, CycleBreakerTransform
import diskcache

from gui.model.DiskDict import DiskDict

external_scripts = [{'src': 'https://cdn.socket.io/4.5.4/socket.io.min.js'}]

long_callback_cache = diskcache.Cache("./long_callback_cache")
long_callback_manager = DiskcacheLongCallbackManager(long_callback_cache)

assets_folder_path = os.path.join(os.getcwd(), 'gui/assets')
app = DashProxy(name=__name__,
                assets_folder=assets_folder_path,
                external_scripts=external_scripts,
                suppress_callback_exceptions=True,
                long_callback_manager=long_callback_manager,
                transforms=[MultiplexerTransform(), NoOutputTransform(), CycleBreakerTransform()])

USERS = DiskDict(os.path.join(os.getcwd(), 'users'), 'user_data')