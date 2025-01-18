from flask import flash, render_template, redirect, url_for, session
import logging
import base64
import cv2
import psycopg2
from database import get_db_connection
from utils.mendeteksi_mengenali_frame import recognize_faces
from utils.employee_active import is_employee_active
from utils.absen_lagi import bisa_absen_lagi
from utils.valid_region import is_valid_region
from utils.g_region import get_regions
from utils.inisialisasi_antrian_suara import speech_queue

def process_attendance(request):
    try:
        # Cek dan atur session untuk mencegah pengumuman yang berulang
        session.setdefault('error_announced', False)
        session.setdefault('region_mismatch_alerted', False)
        session.setdefault('unknown_face_alerted', False)

        if request.method == 'POST':
            # Ambil data dari permintaan
            frame_data = request.form.get('frame')
            region_id = request.form.get('region_id')
            employee_id = request.form.get('employee_id')
            session['region_mismatch_alerted'] = False  # Reset per permintaan baru

            # Validasi input
            if not frame_data or not frame_data.startswith('data:image/jpeg;base64,'):
                logging.error("Format atau data frame tidak valid.")
                return render_template('attendance.html', message="Format atau data frame tidak valid.")

            # Decode dan simpan gambar
            frame_data = frame_data.split(',')[1]
            try:
                img_data = base64.b64decode(frame_data)
            except Exception as e:
                logging.error(f"Error decoding frame: {e}")
                return render_template('attendance.html', message="Kesalahan saat memproses gambar.")

            photo_filename = f"./Train/{employee_id}_attendance.jpg"
            with open(photo_filename, 'wb') as f:
                f.write(img_data)

            # Kenali wajah
            rgb_frame = cv2.imread(photo_filename)
            faces, names, rolls = recognize_faces(rgb_frame)

            if not faces:
                logging.error("Tidak ada wajah yang terdeteksi.")
                return render_template('attendance.html', message="Tidak ada wajah yang terdeteksi.")

            roll = rolls[0]
            if names[0] == "Unknown" or not str(roll).isdigit():
                logging.error(f"Wajah tidak dikenali atau ID karyawan tidak valid: {names[0]}, Roll: {roll}")
                speech_queue.put("Wajah tidak dikenali atau ID karyawan tidak valid. Silahkan coba lagi.")
                return render_template('attendance.html', message="Wajah tidak dikenali atau ID karyawan tidak valid.")

            # Validasi status karyawan
            if not is_employee_active(roll):
                logging.info(f"Karyawan dengan ID {roll} tidak aktif.")
                return render_template('attendance.html', message="Karyawan tidak aktif.")

            # Ambil durasi blokir absensi
            blocking_duration = 10  # Default fallback
            try:
                with get_db_connection() as db_conn:
                    with db_conn.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT setting_value 
                            FROM global_settings 
                            WHERE setting_key = 'blocking_duration_minutes'
                            """
                        )
                        result = cursor.fetchone()
                        if result:
                            blocking_duration = int(result[0])
            except Exception as e:
                logging.error(f"Error saat mengambil durasi blokir: {e}")

            # Cek jika sudah absen sebelumnya
            if not bisa_absen_lagi(roll, region_id, blocking_duration):
                logging.info(f"Anda sudah absen dalam {blocking_duration} menit terakhir.")
                if not session['error_announced']:
                    speech_queue.put(f"Anda sudah absen dalam {blocking_duration} menit terakhir.")
                    session['error_announced'] = True
                return render_template('attendance.html', message=f"Anda sudah absen dalam {blocking_duration} menit terakhir.")

            # Validasi wilayah
            if not is_valid_region(roll, region_id):
                logging.info("Wilayah tidak sesuai.")
                if not session['region_mismatch_alerted']:
                    speech_queue.put("Wilayah tidak sesuai, silahkan coba di region lain.")
                    session['region_mismatch_alerted'] = True
                return render_template('attendance.html', message="Wilayah tidak sesuai.")

            # Simpan absensi
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
                            """
                            INSERT INTO absensi (id_karyawan, check_in, photo, region_id, nama)
                            VALUES (%s, NOW(), %s, %s, %s)
                            """,
                            (roll, photo_filename, region_id, employee_name)
                        )
                        db_conn.commit()
                        logging.info("Absensi berhasil disimpan.")
                        speech_queue.put("Berhasil.")

            except psycopg2.Error as e:
                logging.error(f"PostgreSQL error saat menyimpan data absensi: {e}")
                return render_template('attendance.html', message="Terjadi kesalahan saat mencatat absensi.")

        # Render halaman untuk metode GET
        regions = get_regions()
        selected_region_name = regions[0][1] if regions else "Tidak ada region"
        return render_template('attendance.html', regions=regions, selected_region_name=selected_region_name)

    except Exception as e:
        logging.error(f"Error tidak terduga: {e}")
        return render_template('attendance.html', message="Terjadi kesalahan tidak terduga.")
