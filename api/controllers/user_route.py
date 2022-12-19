from flask.blueprints import Blueprint
from application import db
from api.models.user import User
from api.app_logging.log import Log

# log設定

user_route = Blueprint('user', __name__)
log = Log()


@user_route.route("/create/<user_name>")
def create(user_name: str = ""):
    user = User()
    user.name = user_name

    db.session.add(user)
    db.session.commit()
    log.Info("Create User :" + user.name)
    log.Error("Create User :" + user.name)
    return "OK"


@user_route.route("/lookup/<user_name>")
def lookup(user_name=None):
    user: User = User.query.filter_by(name=user_name).first()
    print(user.id)
    print(user.name)
    return user.name
