from flask import flash, render_template, redirect, url_for
import logging
import base64
import cv2
from database import get_db_connection
from utils.mendeteksi_mengenali_frame import recognize_faces
from utils.employee_active import is_employee_active
from utils.absen_lagi import bisa_absen_lagi
from utils.valid_region import is_valid_region
from utils.inisialisasi_antrian_suara import speech_queue

def process_attendance(request):
    try:
        # Ambil data dari request
        frame_data = request.form.get('frame')
        region_id = request.form.get('region_id')
        employee_id = request.form.get('employee_id')

        # Validasi input
        if not frame_data or not region_id or not employee_id:
            return render_template('attendance.html', message="Semua input wajib diisi.")

        if not frame_data.startswith('data:image/jpeg;base64,'):
            return render_template('attendance.html', message="Format data gambar tidak valid.")

        # Decode frame dan simpan gambar
        frame_data = frame_data.split(',')[1]
        img_data = base64.b64decode(frame_data)
        photo_filename = f"./Train/{employee_id}_attendance.jpg"
        with open(photo_filename, 'wb') as f:
            f.write(img_data)

        # Kenali wajah
        rgb_frame = cv2.imread(photo_filename)
        faces, names, rolls = recognize_faces(rgb_frame)

        if not faces:
            return render_template('attendance.html', message="Tidak ada wajah yang terdeteksi.")

        if names[0] == "Unknown":
            speech_queue.put("Wajah tidak dikenali, silahkan coba lagi.")
            return render_template('attendance.html', message="Wajah tidak dikenali.")

        roll = rolls[0]
        if not is_employee_active(roll):
            return render_template('attendance.html', message="Karyawan tidak aktif.")

        # Ambil durasi blokir absensi
        blocking_duration = get_blocking_duration()

        # Cek apakah bisa absen lagi
        if not bisa_absen_lagi(roll, region_id, blocking_duration):
            speech_queue.put(f"Anda sudah absen dalam {blocking_duration} menit terakhir.")
            return render_template('attendance.html', message=f"Anda sudah absen dalam {blocking_duration} menit terakhir.")

        # Cek validasi region
        if not is_valid_region(roll, region_id):
            speech_queue.put("Wilayah tidak sesuai, silahkan coba di region lain.")
            return render_template('attendance.html', message="Wilayah tidak sesuai.")

        # Simpan data absensi
        save_attendance(roll, photo_filename, region_id)
        speech_queue.put("Berhasil.")
        flash("Absensi berhasil dicatat.", "success")
        return redirect(url_for('attendance.attendance_controller'))

    except Exception as e:
        logging.error(f"Terjadi kesalahan: {e}")
        return render_template('attendance.html', message="Terjadi kesalahan saat memproses absensi.")


def get_blocking_duration():
    try:
        db_conn = get_db_connection()
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT setting_value FROM global_settings WHERE setting_key = 'blocking_duration_minutes'")
            result = cursor.fetchone()
            return int(result[0]) if result else 10  # Default 10 menit
    except Exception as e:
        logging.error(f"Error saat mengambil durasi blokir: {e}")
        return 10  # Default fallback


def save_attendance(roll, photo_filename, region_id):
    try:
        with get_db_connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT nama FROM employee WHERE id_karyawan = %s", (roll,))
                employee_name = cursor.fetchone()
                if not employee_name:
                    raise ValueError(f"Karyawan dengan ID {roll} tidak ditemukan.")

                cursor.execute(
                    "INSERT INTO absensi (id_karyawan, check_in, photo, region_id, nama) VALUES (%s, NOW(), %s, %s, %s)",
                    (roll, photo_filename, region_id, employee_name[0])
                )
                db_conn.commit()
    except Exception as e:
        logging.error(f"Error saat menyimpan data absensi: {e}")
        raise
