from database import get_db_connection
import logging
from datetime import datetime, timedelta
import psycopg2

def bisa_absen_lagi(roll, region_id, blocking_duration=None):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    
    try:
        # Jika blocking_duration tidak disediakan, ambil dari pengaturan global
        if blocking_duration is None:
            cursor.execute("""
                SELECT setting_value 
                FROM global_settings 
                WHERE setting_key = 'blocking_duration_minutes'
            """)
            time_limit_result = cursor.fetchone()
            if not time_limit_result:
                logging.error("Durasi blokir absensi tidak ditemukan di pengaturan global.")
                return False
            blocking_duration = int(time_limit_result[0])
            logging.debug(f"Durasi blokir absensi yang digunakan: {blocking_duration} menit")

        # Mengecek status region
        cursor.execute("""
            SELECT is_active 
            FROM region
            WHERE id = %s
        """, (region_id,))
        region_result = cursor.fetchone()

        if not region_result or not region_result[0]:
            logging.error(f"Region {region_id} tidak aktif atau tidak ditemukan.")
            return False

        # Mengecek apakah karyawan sudah absen sebelumnya
        cursor.execute("""
            SELECT check_in, region_id 
            FROM absensi 
            WHERE id_karyawan = %s 
            ORDER BY check_in DESC 
            LIMIT 1
        """, (roll,))
        last_entry = cursor.fetchone()

        if roll == "Unknown":
            logging.error("Wajah tidak dikenali, tidak dapat memproses absensi.")
            return False

        if last_entry:
            last_check_in, last_region_id = last_entry

            # Perbandingan langsung dengan timestamp (timestamp without time zone)
            if last_region_id == region_id:
                # Mengecek apakah waktu absen sudah cukup
                if (datetime.now() - last_check_in) < timedelta(minutes=blocking_duration):
                    logging.info("Belum cukup waktu untuk absen kembali di region yang sama.")
                    return False
                else:
                    logging.info("Waktu blokir sudah habis, karyawan bisa absen lagi.")
                    return True

        # Jika belum ada absensi sebelumnya, karyawan bisa absen
        logging.info("Karyawan belum melakukan absensi sebelumnya, bisa absen.")
        return True
    except Exception as e:
        logging.error("Error saat memeriksa apakah karyawan %s bisa absen: %s", roll, str(e))
        return False
    finally:
        cursor.close()
        db_conn.close()

# Untuk menyimpan absensi:
def simpan_absensi(roll, region_id, photo_filename, employee_name):
    try:
        logging.info(f"Mulai menyimpan absensi untuk karyawan {roll} di region {region_id}.")

        with get_db_connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO absensi (id_karyawan, check_in, photo, region_id, nama) VALUES (%s, %s, %s, %s, %s)",
                    (roll, datetime.now(), photo_filename, region_id, employee_name)
                )
                db_conn.commit()  # Pastikan untuk commit setelah query
                logging.info(f"Absensi untuk karyawan {roll} berhasil disimpan.")
                return "Absensi berhasil disimpan."
    
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error saat menyimpan data absensi: {e}")
        return "Terjadi kesalahan saat mencatat absensi."
    
    except Exception as e:
        logging.error(f"Error tidak terduga saat memproses absensi: {e}")
        return "Terjadi kesalahan saat memproses absensi."

