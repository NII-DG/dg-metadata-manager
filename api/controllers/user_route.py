from flask.blueprints import Blueprint
from application import db
from api.models.user import User

user_route = Blueprint('user', __name__)


@user_route.route("/create/<user_name>")
def create(user_name=None):
    user = User()
    user.name = user_name

    db.session.add(user)
    db.session.commit()
    return "OK"


@user_route.route("/lookup/<user_name>")
def lookup(user_name=None):
    user: User = User.query.filter_by(name=user_name).first()
    print(user.id)
    print(user.name)
    return user.name
