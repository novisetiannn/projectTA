from database import get_db_connection
import logging

# Fungsi untuk mengecek apakah ID karyawan ada di database
def check_employee_exists(id_karyawan):
    try:
        with get_db_connection() as db_conn:
            cursor = db_conn.cursor()
            cursor.execute("SELECT FROM employee WHERE id_karyawan = %s", (id_karyawan,))
            return cursor.fetchone() is not None
    except Exception as e:
        logging.error(f"Error checking employee existence: {e}")
        return False