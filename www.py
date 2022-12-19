# Flask Appにルーティングを追加するファイル
from application import app
from api.controllers.index import bpweb
from api.controllers.user_route import user_route

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)


app.register_blueprint(bpweb, url_prefix="/")
app.register_blueprint(user_route, url_prefix="/user")
