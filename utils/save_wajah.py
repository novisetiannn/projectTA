from database import get_db_connection
import pickle
import logging

#fungsi untuk Menyimpan encoding wajah seorang karyawan ke dalam database.
def save_face_encoding(id_karyawan, face_encoding):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Serialisasi encoding wajah menggunakan pickle
        encoding_blob = pickle.dumps(face_encoding)

        # Simpan encoding wajah ke database
        cursor.execute("UPDATE employee SET face_encoding = %s WHERE id_karyawan = %s", (encoding_blob, id_karyawan))
        db_conn.commit()

        cursor.close()
        db_conn.close()
        logging.info(f"Face encoding for employee ID {id_karyawan} saved successfully.")
    except Exception as e:
        logging.error(f"Error saving face encoding: {e}")