from flask import Blueprint, render_template
from decorators.decorators import role_required
from utils.absen_attendance import attendance

absen_attendance = Blueprint('absen_attendance', __name__)

@absen_attendance.route('/attendance', methods=['GET', 'POST'])
def attendance():
    return render_template('attendance.html', regions=regions, selected_region_name=selected_region_name)