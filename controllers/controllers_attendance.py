from flask import Blueprint, render_template, request
from decorators.decorators import role_required
from utils.absen_attendance import process_attendance
from utils.g_region import get_regions

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET', 'POST'])
def attendance_controller():
    if request.method == 'POST':
        return process_attendance(request)

    # Render halaman untuk metode GET
    regions = get_regions()
    selected_region_name = regions[0][1] if regions else "Tidak ada region"
    return render_template('attendance.html', regions=regions, selected_region_name=selected_region_name)
