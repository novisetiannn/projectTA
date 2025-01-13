from database import get_db_connection
import logging
from datetime import datetime, timedelta

def bisa_absen_lagi(roll, region_id):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    
    try:
        # Ambil durasi blokir absensi dari global_settings
        cursor.execute("""
            SELECT setting_value 
            FROM global_settings 
            WHERE setting_key = 'blocking_duration_minutes'
        """)
        time_limit_result = cursor.fetchone()
        if not time_limit_result:
            logging.error("Durasi blokir absensi tidak ditemukan di pengaturan global.")
            return False

        # Konversi nilai ke integer
        blocking_duration = int(time_limit_result[0])
        logging.debug(f"Durasi blokir absensi yang digunakan: {blocking_duration} menit")

        # Periksa apakah region aktif dan diizinkan
        cursor.execute("""
            SELECT is_active 
            FROM region
            WHERE id = %s
        """, (region_id,))
        region_result = cursor.fetchone()
        
        if not region_result or not region_result[0]:  # Jika region tidak aktif atau tidak ditemukan
            logging.error(f"Region {region_id} tidak aktif atau tidak ditemukan.")
            return False

        # Ambil waktu absensi terakhir untuk karyawan ini
        cursor.execute("""
            SELECT check_in, region_id 
            FROM absensi 
            WHERE id_karyawan = %s 
            ORDER BY check_in DESC 
            LIMIT 1
        """, (roll,))
        last_entry = cursor.fetchone()

        if last_entry:
            last_check_in, last_region_id = last_entry
            # Periksa apakah absensi terakhir di region yang sama
            if last_region_id == region_id:
                # Periksa waktu absensi terakhir
                if (datetime.now() - last_check_in) < timedelta(minutes=blocking_duration):
                    logging.info("Belum cukup waktu untuk absen kembali di region yang sama.")
                    return False  # Tidak bisa absen lagi di region yang sama
        return True  # Bisa absen
    except Exception as e:
        logging.error("Error saat memeriksa apakah karyawan %s bisa absen: %s", roll, str(e))
        return False
    finally:
        cursor.close()
        db_conn.close()