from flask.blueprints import Blueprint
from application import db
from api.models.user import User

# log設定
from logging import getLogger
from config import logging_config

user_route = Blueprint('user', __name__)
logger = getLogger("basicLogger")


@user_route.route("/create/<user_name>")
def create(user_name: str = ""):
    user = User()
    user.name = user_name

    db.session.add(user)
    db.session.commit()
    logger.info("Create User :" + user.name)
    return "OK"


@user_route.route("/lookup/<user_name>")
def lookup(user_name=None):
    user: User = User.query.filter_by(name=user_name).first()
    print(user.id)
    print(user.name)
    return user.name
