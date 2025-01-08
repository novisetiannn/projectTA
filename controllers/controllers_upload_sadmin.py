from flask import Blueprint
from decorators.decorators import role_required
from utils.upd_sadmin import upload_superadmin as upload_superadmin_util

upd_sadmin = Blueprint('upd_sadmin', __name__)

@upd_sadmin.route('/upload_superadmin', methods=['GET', 'POST'])
@role_required(['super_admin'])
def upload_superadmin_view():
    return upload_superadmin_util()