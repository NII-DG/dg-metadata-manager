from flask import Blueprint

bpweb = Blueprint('web', __name__)


@bpweb.route("/")
def name():

    return "hello"
