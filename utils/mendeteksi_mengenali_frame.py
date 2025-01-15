import cv2
import face_recognition
import logging
import numpy as np
from utils.known_faces import Known_employee_encodings, Known_employee_names, Known_employee_rolls

# Fungsi untuk mendeteksi dan mengenali wajah dalam frame video.
def recognize_faces(frame):
    try:
        # Konversi frame ke RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Deteksi lokasi wajah dan encoding
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        names = []
        rolls = []

        for face_encoding in face_encodings:
            # Log encoding wajah yang baru
            logging.info(f"New face encoding: {face_encoding}")

            # Menggunakan face_distance untuk mendapatkan jarak
            face_distances = face_recognition.face_distance(Known_employee_encodings, face_encoding)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < 0.4:  # Sesuaikan threshold
                    name = Known_employee_names[best_match_index]
                    roll = Known_employee_rolls[best_match_index]
                else:
                    name = "Unknown"
                    roll = "Unknown"
            else:
                logging.warning("Tidak ada wajah yang cocok ditemukan.")
                name = "Unknown"
                roll = "Unknown"

            names.append(name)
            rolls.append(roll)

            # Log hasil pencocokan
            logging.info(f"Matched name: {name}, roll: {roll}")

        return face_locations, names, rolls
    except Exception as e:
        logging.error(f"Error di recognize_faces: {e}")
        return [], [], []
