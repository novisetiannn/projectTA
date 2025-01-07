from flask import Blueprint
from decorators.decorators import role_required
from utils.log_out import logout

log_out = Blueprint('log_out', __name__)

@log_out.route('/logout')
def logout():
    logout()