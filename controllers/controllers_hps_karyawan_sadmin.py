from flask import Blueprint
from decorators.decorators import role_required
from utils.hps_karyawan_sadmin import hapus_karyawan

hps_karyawan_sadmin = Blueprint('hps_karyawan_sadmin', __name__)

@hps_karyawan_sadmin.route('/hapus_karyawan/<int:id_karyawan>', methods=['POST'])
@role_required(['super_admin'])
def hapus_karyawan(id_karyawan):
    return hapus_karyawan(id_karyawan)