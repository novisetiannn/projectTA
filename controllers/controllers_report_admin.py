from flask import Blueprint
from decorators.decorators import role_required
from utils.report_adm import report_admin

report_adm = Blueprint('report_adm', __name__)

@report_adm.route('/report_admin')
@role_required(['admin'])  # Mengizinkan hanya admin
def report_admin():
    return report_admin()