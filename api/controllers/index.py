from flask.blueprints import Blueprint

bp_index = Blueprint('index', __name__)


@bp_index.route("/")
def name():

    return "hello"
