from flask import Blueprint
from decorators.decorators import role_required
from utils.downl_report import download_report

downl_report = Blueprint('downl_report', __name__)

@downl_report.route('/report/download')
@role_required(['admin', 'super_admin'])
def download_report():
    return download_report()