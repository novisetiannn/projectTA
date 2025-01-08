from flask import Blueprint, render_template
from decorators.decorators import role_required
from utils.tampil_data_adm import fetch_admin_data

tampil_data_adm = Blueprint('tampil_data_adm', __name__)

@tampil_data_adm.route('/tampil_data_admin', methods=['GET'])
@role_required(['admin'])  # Hanya mengizinkan admin
def tampil_data_admin():
    data_list, error = fetch_admin_data()
    if error:
        return f"Terjadi kesalahan: {error}", 500

    return render_template('tampil_data_admin.html', data_list=data_list)
