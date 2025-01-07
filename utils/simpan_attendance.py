from database import get_db_connection
import psycopg2
import logging

def save_attendance(employee_id, photo_filename, region_id):
    try:
        with get_db_connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT nama FROM employee WHERE id_karyawan = %s", (employee_id,))
                employee_name = cursor.fetchone()
                if not employee_name:
                    return "Karyawan tidak ditemukan."
                
                # Simpan absensi
                cursor.execute(
                    "INSERT INTO absensi (id_karyawan, check_in, photo, region_id, nama) VALUES (%s, NOW(), %s, %s, %s)",
                    (employee_id, photo_filename, region_id, employee_name[0])
                )
                db_conn.commit()
                return "Absensi berhasil disimpan."
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error saat menyimpan data absensi: {e}")
        return "Terjadi kesalahan saat mencatat absensi."
    except Exception as e:
        logging.error(f"Error tidak terduga: {e}")
        return "Terjadi kesalahan saat memproses absensi."