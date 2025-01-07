# fungsi untuk Menghapus data karyawan dan foto terkait dari database.
from database import get_db_connection
import os
import logging

def delete_employee_data(id_karyawan):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Ambil daftar foto yang terkait dengan karyawan
        cursor.execute("SELECT photo FROM employee WHERE id_karyawan = %s", (id_karyawan,))
        photo_paths = cursor.fetchone()

        # Hapus data karyawan dari database
        cursor.execute("DELETE FROM employee WHERE id_karyawan = %s", (id_karyawan,))
        db_conn.commit()
        
        # Menghapus data absensi terkait
        cursor.execute("DELETE FROM absensi WHERE id_karyawan = %s", (id_karyawan,))

        # Hapus foto-foto dari folder 'Train'
        if photo_paths:
            for photo_path in photo_paths[0].strip('{}').split(','):
                photo_path = photo_path.strip('"')
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                    logging.info(f"Deleted file: {photo_path}")

        cursor.close()
        db_conn.close()
    except Exception as e:
        logging.error(f"Error deleting employee data: {e}")