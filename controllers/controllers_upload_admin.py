from flask import Blueprint
from decorators.decorators import role_required
from utils.upd_admin import upload_admin as upload_admin_util

upd_admin = Blueprint('upd_admin', __name__)

@upd_admin.route('/upload_admin', methods=['GET', 'POST'])
@role_required(['admin'])
def upload_admin_view():
    return upload_admin_util()