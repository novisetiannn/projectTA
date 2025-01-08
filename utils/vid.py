from flask import Response
from utils.generate_mark_frames import generate_marked_frames

def video(region_id):
    return Response(generate_marked_frames(region_id), mimetype='multipart/x-mixed-replace; boundary=frame')