from application import app
from api.controllers.index import bpweb

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)


app.register_blueprint(bpweb, url_prefix="/")
