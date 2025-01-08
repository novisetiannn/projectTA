from flask import Blueprint
from decorators.decorators import role_required
from utils.report_sadmin import report_super_admin as report_super_admin_util

report_sadmin = Blueprint('report_sadmin', __name__)

@report_sadmin.route('/report_superadmin')
@role_required(['super_admin'])  # Mengizinkan hanya super_admin
def report_super_admin_view():
    return report_super_admin_util()