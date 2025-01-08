from flask import Blueprint
from utils.loginn import login as login_util

log_in = Blueprint('log_in', __name__)

@log_in.route('/login', methods=['GET', 'POST'])
def login_view():
    return login_util()