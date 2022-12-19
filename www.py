# Flask Appにルーティングを追加するファイル
from application import app
from api.controllers.index import bp_index
from api.controllers.user_route import user_route

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)


# api.contrallers で Blueprint('{Blueprint名}', __name__)を新規に追加したら下記に追記する。
# app.register_blueprint(Blueprint()の変数名, url_prefix="{rootパス}")
app.register_blueprint(bp_index, url_prefix="/")
app.register_blueprint(user_route, url_prefix="/user")
