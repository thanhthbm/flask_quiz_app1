from flask import Blueprint
bp = Blueprint('quiz', __name__)
from . import routes  # noqa
