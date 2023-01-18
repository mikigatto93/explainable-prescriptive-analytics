import os


from dash.long_callback import DiskcacheLongCallbackManager
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform, CycleBreakerTransform
import diskcache
from flask_socketio import SocketIO

external_scripts = [{'src': 'https://cdn.socket.io/4.5.4/socket.io.min.js'}]

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

assets_folder_path = os.path.join(os.getcwd(), 'gui/assets')
app = DashProxy(name=__name__,
                assets_folder=assets_folder_path,
                external_scripts=external_scripts,
                suppress_callback_exceptions=True,
                long_callback_manager=long_callback_manager,
                transforms=[MultiplexerTransform(), NoOutputTransform(), CycleBreakerTransform()])

socketio = SocketIO(app.server, logger=True, engineio_logger=True)