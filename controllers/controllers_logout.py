from flask import Blueprint
from utils.log_out import logout as logout_util

log_out = Blueprint('log_out', __name__)

@log_out.route('/logout')
def logout_view():
    return logout_util()