from database import get_db_connection
import logging
import pickle

def save_to_database(name, roll, newEncode, saved_files_pg, region_id):
    try:
        with get_db_connection() as db_conn:
            cursor = db_conn.cursor()
            face_encoding_bytes = pickle.dumps(newEncode)

            cursor.execute(
                "INSERT INTO employee (name, id_karyawan, face_encoding, photo, region_id) VALUES (%s, %s, %s, %s, %s)",
                (name, roll, face_encoding_bytes, saved_files_pg, region_id)
            )
            db_conn.commit()
    except Exception as e:
        logging.error(f"Error saving to database: {e}")
        return False
    return True