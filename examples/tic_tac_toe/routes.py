from flask import Blueprint, render_template, abort, render_template_string


routes = Blueprint("routes", __name__)


@routes.route("/")
def index():
    return "Tic tac toe"
