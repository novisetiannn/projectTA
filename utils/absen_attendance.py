from flask import request, render_template
import logging
from database import get_db_connection
import psycopg2
import base64
import cv2
from utils.mendeteksi_mengenali_frame import recognize_faces
from utils.employee_active import is_employee_active
from utils.absen_lagi import bisa_absen_lagi
from utils.valid_region import is_valid_region
from utils.g_region import get_regions
from utils.inisialisasi_antrian_suara import speech_queue

def attendance():
    global error_announced, region_mismatch_alerted, unknown_face_alerted

    if request.method == 'POST':
        # Ambil data dari permintaan
        frame_data = request.form.get('frame')
        region_id = request.form.get('region_id')
        employee_id = request.form.get('employee_id')

        # Validasi input
        if not frame_data:
            logging.error("Tidak ada data frame yang diterima.")
            return render_template('attendance.html', message="Tidak ada data frame yang diterima.")
        
        # Pemrosesan gambar
        if not frame_data.startswith('data:image/jpeg;base64,'):
            logging.error("Format frame tidak valid")
            return render_template('attendance.html', message="Format frame tidak valid.")

        # Decode frame
        frame_data = frame_data.split(',')[1]
        img_data = base64.b64decode(frame_data)

        # Simpan foto
        photo_filename = f"./Train/{employee_id}_attendance.jpg"
        with open(photo_filename, 'wb') as f:
            f.write(img_data)

        # Kenali wajah
        rgb_frame = cv2.imread(photo_filename)
        faces, names, rolls = recognize_faces(rgb_frame)

        if len(faces) == 0:
            logging.error("Tidak ada wajah yang terdeteksi")
            return render_template('attendance.html', message="Tidak ada wajah yang terdeteksi.")

        roll = rolls[0]

        if names[0] == "Unknown":
            logging.info("Wajah tidak dikenali. Absensi tidak disimpan.")
            if not unknown_face_alerted:
                speech_queue.put("Wajah tidak dikenali, silahkan coba lagi.")
                unknown_face_alerted = True
            return render_template('attendance.html', message="Wajah tidak dikenali.")

        if not is_employee_active(roll):
            logging.info(f"Karyawan dengan ID {roll} tidak aktif. Absensi tidak disimpan.")
            return render_template('attendance.html', message="Karyawan tidak aktif.")

        # Ambil durasi blokir absensi dari pengaturan global
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT setting_value 
                FROM global_settings 
                WHERE setting_key = 'blocking_duration_minutes'
            """)
            blocking_duration_result = cursor.fetchone()
            if blocking_duration_result:
                blocking_duration = int(blocking_duration_result[0])
            else:
                logging.error("Durasi blokir absensi tidak ditemukan. Gunakan nilai default 10 menit.")
                blocking_duration = 10  # Default fallback
        except Exception as e:
            logging.error(f"Error saat mengambil durasi blokir: {e}")
            blocking_duration = 10  # Default fallback
        finally:
            cursor.close()
            db_conn.close()

        # Cek absensi
        if not bisa_absen_lagi(roll, region_id, blocking_duration):
            logging.info(f"Anda sudah absen dalam {blocking_duration} menit terakhir di region ini.")
            if not error_announced:
                speech_queue.put(f"Anda sudah absen dalam {blocking_duration} menit terakhir di region ini.")
                error_announced = True
            return render_template('attendance.html', message=f"Anda sudah absen dalam {blocking_duration} menit terakhir di region ini.")
        
        if not is_valid_region(roll, region_id):
            logging.info("Wilayah tidak sesuai. Absensi tidak disimpan.")
            if not region_mismatch_alerted:
                speech_queue.put("Wilayah tidak sesuai, silahkan coba di region lain.")
                region_mismatch_alerted = True
            return render_template('attendance.html', message="Wilayah tidak sesuai.")

        # Simpan data absensi
        try:
            with get_db_connection() as db_conn:
                with db_conn.cursor() as cursor:
                    cursor.execute("SELECT nama FROM employee WHERE id_karyawan = %s", (roll,))
                    employee_name = cursor.fetchone()
                    
                    if employee_name:
                        employee_name = employee_name[0]
                    else:
                        logging.error(f"Karyawan dengan ID {roll} tidak ditemukan.")
                        return render_template('attendance.html', message="Karyawan tidak ditemukan.")

                    cursor.execute(
                        "INSERT INTO absensi (id_karyawan, check_in, photo, region_id, nama) VALUES (%s, NOW(), %s, %s, %s)",
                        (roll, photo_filename, region_id, employee_name)
                    )
                    db_conn.commit()
                    logging.info("Absensi berhasil disimpan.")
                    if not error_announced:
                        speech_queue.put("Berhasil.")
                        error_announced = True

        except psycopg2.Error as e:
            logging.error(f"PostgreSQL error saat menyimpan data absensi: {e}")
            return render_template('attendance.html', message="Terjadi kesalahan saat mencatat absensi.")
        except Exception as e:
            logging.error(f"Error tidak terduga saat memproses absensi: {e}")
            return render_template('attendance.html', message="Terjadi kesalahan saat memproses absensi.")

    # Render halaman jika metode GET
    regions = get_regions()
    selected_region_name = regions[0][1] if regions else "Tidak ada region"
    return render_template('attendance.html', regions=regions, selected_region_name=selected_region_name)