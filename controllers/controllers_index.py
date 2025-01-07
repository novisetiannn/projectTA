from flask import Blueprint
from decorators.decorators import login_required
from utils.indx import index

indexx = Blueprint('indexx', __name__)

@indexx.route('/')
@login_required
def index():
    return index()