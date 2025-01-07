from flask import Blueprint
from decorators.decorators import role_required
from utils.vid import video

videoAttendance = Blueprint('videoAttendance', __name__)

@videoAttendance.route('/video/<int:region_id>')
def video(region_id):
    return video(region_id)