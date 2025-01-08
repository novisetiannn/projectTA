from flask import Blueprint
from decorators.decorators import role_required
from utils.tb_admin import table_admin as table_admin_util

tb_admin = Blueprint('tb_admin', __name__)

@tb_admin.route('/table_admin')
@role_required(['admin'])
def table_admin_view():
    return table_admin_util()