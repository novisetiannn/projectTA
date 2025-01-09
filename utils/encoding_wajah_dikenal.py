from database import get_db_connection
import pickle
import logging
from utils.known_faces import Known_employee_encodings, Known_employee_names, Known_employee_rolls

#fungsi untuk Memuat encoding wajah yang dikenal dari database untuk digunakan dalam pengenalan wajah.
def load_known_faces():
    global Known_employee_encodings, Known_employee_names, Known_employee_rolls
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Ambil semua data karyawan dari database
        cursor.execute("SELECT id_karyawan, name, face_encoding FROM employee")
        rows = cursor.fetchall()

        for row in rows:
            id_karyawan, nama, face_encoding = row
            if face_encoding is not None:
                # Deserialize face_encoding dari BLOB
                encoding = pickle.loads(face_encoding)
                Known_employee_encodings.append(encoding)
                Known_employee_names.append(nama)
                Known_employee_rolls.append(id_karyawan)

        cursor.close()
        db_conn.close()
        logging.info("Known faces loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading known faces: {e}")