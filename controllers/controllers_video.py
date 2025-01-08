from flask import Blueprint
from decorators.decorators import role_required
from utils.vid import video as video_util

videoAttendance = Blueprint('videoAttendance', __name__)

@videoAttendance.route('/video/<int:region_id>')
def video_view(region_id):
    return video_util(region_id)