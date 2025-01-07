from flask import Blueprint
from decorators.decorators import role_required
from utils.tampil_data_adm import tampil_data_admin

tampil_data_adm = Blueprint('tampil_data_adm', __name__)

@tampil_data_adm.route('/tampil_data_admin', methods=['GET'])
@role_required(['admin'])  # Hanya mengizinkan admin
def tampil_data_admin():
    return tampil_data_admin()