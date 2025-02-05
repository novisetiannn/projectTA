from flask import Blueprint
from decorators.decorators import role_required
from utils.upd_employee_admin import update_employee_admin as update_employee_admin_util

upd_employee_admin = Blueprint('upd_employee_admin', __name__)

@upd_employee_admin.route('/update_employee_admin/<int:id_karyawan>', methods=['GET', 'POST'])
@role_required(['admin'])
def update_employee_admin_view(id_karyawan):
    return update_employee_admin_util(id_karyawan)