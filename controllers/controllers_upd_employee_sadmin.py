from flask import Blueprint
from decorators.decorators import role_required
from utils.update_employee_sadmin import update_employee_superadmin

update_employee_sadmin = Blueprint('update_employee_sadmin', __name__)

@update_employee_sadmin.route('/update_employee_superadmin/<int:id_karyawan>', methods=['GET', 'POST'])
@role_required(['super_admin'])
def update_employee_superadmin(id_karyawan):
    return update_employee_superadmin(id_karyawan)