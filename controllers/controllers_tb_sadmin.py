from flask import Blueprint
from decorators.decorators import role_required
from utils.tb_sadmin import table_superadmin

tb_sadmin = Blueprint('tb_sadmin', __name__)

@tb_sadmin.route('/table_superadmin')
@role_required(['super_admin'])  # Hanya mengizinkan super_admin
def table_superadmin():
    return table_superadmin()