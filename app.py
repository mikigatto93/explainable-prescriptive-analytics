import os
import json

from dash import DiskcacheManager
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform, CycleBreakerTransform
import diskcache

from gui.model.DiskDict import DiskDict

external_scripts = [{'src': 'https://cdn.socket.io/4.5.4/socket.io.min.js'}]

long_callback_cache = diskcache.Cache("./long_callback_cache")
long_callback_manager = DiskcacheManager(long_callback_cache)

assets_folder_path = os.path.join(os.getcwd(), 'gui/assets')
app = DashProxy(name=__name__,
                assets_folder=assets_folder_path,
                external_scripts=external_scripts,
                suppress_callback_exceptions=True,
                long_callback_manager=long_callback_manager,
                transforms=[MultiplexerTransform(), NoOutputTransform(), CycleBreakerTransform()])

USERS = DiskDict(os.path.join(os.getcwd(), 'users'), 'user_data', create_path_at_init=True)

config_path = os.path.join(os.getcwd(), 'gui_config.json')
if os.path.exists(config_path):
    with open(config_path, 'r') as config_f:
        CONFIG = json.loads(config_f.read())
else:
    # default configuration
    CONFIG = {'KEEP_ALIVE_SIGNAL_MSEC_INTERVAL': 5000}
