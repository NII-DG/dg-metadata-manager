from application import app
from api.controllers.index import index_page

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)


app.register_blueprint(index_page, url_prefix="/")
