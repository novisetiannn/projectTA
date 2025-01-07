from flask import Blueprint
from decorators.decorators import role_required
from utils.hps_karyawan_admin import hapus_karyawan_admin

hps_karyawan_admin = Blueprint('hps_karyawan_admin', __name__)

@hps_karyawan_admin.route('/hapus_karyawan_admin/<int:id_karyawan>', methods=['POST'])
@role_required(['admin'])
def hapus_karyawan_admin(id_karyawan):
    return hapus_karyawan_admin(id_karyawan)