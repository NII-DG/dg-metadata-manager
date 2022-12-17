from flask import Blueprint

index_page = Blueprint("index_page", __name__)


@index_page.route("/")
def index():

    return "hello"
