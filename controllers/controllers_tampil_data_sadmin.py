from flask import Blueprint
from decorators.decorators import role_required
from utils.tampil_data_sadmin import tampil_data_superadmin

tampil_data_sadmin = Blueprint('tampil_data_sadmin', __name__)

@tampil_data_sadmin.route('/tampil_data_superadmin', methods=['GET'])
@role_required(['super_admin'])  # Hanya mengizinkan super_admin
def tampil_data_superadmin():
    return tampil_data_superadmin()