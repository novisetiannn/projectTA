from database import get_db_connection
import cv2
import face_recognition
import logging
import numpy as np
from utils.known_faces import Known_employee_encodings, Known_employee_names, Known_employee_rolls

# fungsi untuk Mendeteksi dan mengenali wajah dalam frame video.
def recognize_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    names = []
    rolls = []
    
    for face_encoding in face_encodings:
        # Log encoding wajah yang baru
        logging.info(f"New face encoding: {face_encoding}")

        # Menggunakan face_distance untuk mendapatkan jarak
        face_distances = face_recognition.face_distance(Known_employee_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if face_distances[best_match_index] < 0.4:  # Sesuaikan threshold sesuai kebutuhan
            name = Known_employee_names[best_match_index]
            roll = Known_employee_rolls[best_match_index]
        else:
            name = "Unknown"
            roll = "Unknown"

        names.append(name)
        rolls.append(roll)

        # Log hasil pencocokan
        logging.info(f"Matched name: {name}, roll: {roll}")

    return face_locations, names, rolls