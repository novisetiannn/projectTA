from flask import Blueprint
from decorators.decorators import role_required
from utils.tb_admin import table_admin

tb_admin = Blueprint('tb_admin', __name__)

@tb_admin.route('/table_admin')
@role_required(['admin']) 
def table_admin():
    return table_admin()