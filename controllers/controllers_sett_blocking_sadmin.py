from flask import Blueprint
from decorators.decorators import role_required
from utils.settings_block_sadmin import blocking_settings

sett_blocking = Blueprint('sett_blocking', __name__)

@sett_blocking.route('/blocking_settings', methods=['GET', 'POST'])
@role_required(['super_admin'])
def blocking_settings():
    return blocking_settings()