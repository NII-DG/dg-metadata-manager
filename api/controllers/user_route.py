from flask.blueprints import Blueprint
from application import db
from api.models.user import User
from api.utils.app_logging.log import Log
from flask import request

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

# POSTメソッドでユーザを作成し、JSONを返す
@user_route.route("/create", methods=['POST'])
def create_post():
    user = User()
    user.name = request.args['username']
    db.session.add(user)
    db.session.commit()
    log.Info("Create User :" + user.name)
    log.Error("Create User :" + user.name)
    return {
        "result": "OK",
        "username": user.name
    }


@user_route.route("/lookup/<user_name>")
def lookup(user_name=None):
    user: User = User.query.filter_by(name=user_name).first()
    print(user.id)
    print(user.name)
    return user.name
