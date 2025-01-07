from flask import Blueprint
from decorators.decorators import role_required
from utils.report_sadmin import report_super_admin

report_sadmin = Blueprint('report_sadmin', __name__)

@report_sadmin.route('/report_superadmin')
@role_required(['super_admin'])  # Mengizinkan hanya super_admin
def report_super_admin():
    return report_super_admin()