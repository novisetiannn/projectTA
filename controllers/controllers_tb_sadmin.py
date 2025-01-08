from flask import Blueprint
from decorators.decorators import role_required
from utils.tb_sadmin import table_superadmin as table_superadmin_util

tb_sadmin = Blueprint('tb_sadmin', __name__)

@tb_sadmin.route('/table_superadmin')
@role_required(['super_admin'])  # Hanya mengizinkan super_admin
def table_superadmin_view():
    return table_superadmin_util()