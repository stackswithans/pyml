import expan
from flask import Blueprint
from .views.index import Index  # type: ignore


routes_bp = Blueprint("routes_bp", __name__)


@routes_bp.route("/")
def index():
    return Index()
