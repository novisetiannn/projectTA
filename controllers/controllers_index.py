from flask import Blueprint
from decorators.decorators import login_required
from utils.indx import index as index_util

indexx = Blueprint('indexx', __name__)

@indexx.route('/')
@login_required
def index_view():
    return index_util()