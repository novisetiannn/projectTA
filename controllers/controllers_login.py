from flask import Blueprint
from utils.loginn import login

log_in = Blueprint('log_in', __name__)

@log_in.route('/login', methods=['GET', 'POST'])
def login():
    return login()