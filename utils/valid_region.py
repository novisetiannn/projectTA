# Fungsi untuk memvalidasi region saat absensi
from database import get_db_connection
import logging
import psycopg2

def is_valid_region(employee_id, region_id):
    try:
        with get_db_connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT region_id FROM employee WHERE id_karyawan = %s", (employee_id,))
                result = cursor.fetchone()

                if result is not None:
                    is_valid = result[0] == region_id
                    logging.debug(f"Validasi region untuk karyawan ID {employee_id}: {is_valid}")
                    return is_valid
                else:
                    logging.warning("Karyawan dengan ID %s tidak ditemukan.", employee_id)
                    return False
    except psycopg2.Error as e:
        logging.error("Error saat memeriksa region untuk karyawan %s: %s", employee_id, str(e))
        return False
    except Exception as e:
        logging.error("Kesalahan tidak terduga saat memeriksa region untuk karyawan %s: %s", employee_id, str(e))
        return False