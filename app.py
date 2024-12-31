from flask import Flask, flash, jsonify, render_template, Response, request, redirect, session, url_for, send_file
from database import get_db_connection
from functools import wraps
import face_recognition
import numpy as np
import cv2
import logging
import queue 
import threading
from passlib.hash import sha256_crypt
import os
import base64
import pandas as pd
import pdfkit
import time
import uuid
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
from gtts import gTTS
from playsound import playsound
import pickle
from flask_sqlalchemy import SQLAlchemy
import json
import re
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import io
import openpyxl

app = Flask(__name__)
# Atur ukuran maksimal (contoh: 50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2655@localhost:5432/attendancedbb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Variabel global
current_employee_name_superadmin = ""
current_employee_name_admin = ""
error_announced = False
error_timestamp = None

# Atur ukuran maksimal (contoh: 50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

db = SQLAlchemy(app)

#model untuk tabel user
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Menyimpan role pengguna
    
# Model untuk tabel Employee
class Employee(db.Model):
    __tablename__ = 'employee'
    id_karyawan = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    face_encoding = db.Column(db.LargeBinary)  # Menggunakan LargeBinary untuk BYTEA
    photo = db.Column(db.ARRAY(db.Text))  # Menggunakan ARRAY untuk tekstual array
    status = db.Column(db.CHAR(1), default='A', nullable=False)
    tgl_create = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    create_by = db.Column(db.String)
    tgl_update = db.Column(db.DateTime)
    update_by = db.Column(db.String)
    tgl_delete = db.Column(db.DateTime)
    delete_by = db.Column(db.String)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('loginsignup'))
        return f(*args, **kwargs)
    return decorated_function

# Inisialisasi logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


# Inisialisasi antrian suara
speech_queue = queue.Queue()
error_announced = False  # Variabel global untuk melacak apakah error telah diumumkan
error_timestamp = None  # Variabel waktu untuk membatasi pengulangan error

# Fungsi untuk memproses suara dari antrian menggunakan gTTS dan playsound
def speak_from_queue(speech_queue):
    while True:
        text = speech_queue.get()
        if text:  # Jika ada teks dalam antrian
            try:
                # Buat file suara sementara dari teks
                tts = gTTS(text=text, lang='id')
                tts.save("temp_speech.mp3")

                # Putar file suara
                playsound("temp_speech.mp3")

            except Exception as e:
                print(f"Error playing sound: {e}")
            finally:
                # Hapus file sementara setelah diputar, pastikan file ada sebelum menghapus
                if os.path.exists("temp_speech.mp3"):
                    os.remove("temp_speech.mp3")
                
                speech_queue.task_done()  # Menandakan tugas selesai

# Fungsi untuk menandai kehadiran tanpa nama
def mark_attendance():
    # Langsung kembalikan pesan "Berhasil"
    return "Berhasil"

# Jalankan thread untuk memutar suara dari antrian
speech_thread = threading.Thread(target=speak_from_queue, args=(speech_queue,))
speech_thread.daemon = True  # Mengatur thread sebagai daemon agar berhenti saat aplikasi berhenti
speech_thread.start()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

Known_employee_encodings = []
Known_employee_names = []
Known_employee_rolls = []

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
        
# fungsi untuk Menyimpan data karyawan baru beserta encoding wajahnya ke dalam database.
def save_employee(name, photo_path):
    try:
        # Baca foto dan ekstrak face encoding
        image = face_recognition.load_image_file(photo_path)
        face_encodings = face_recognition.face_encodings(image)

        # Pastikan ada setidaknya satu encoding wajah
        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]  # Ambil encoding wajah pertama
            
            # Serialisasi encoding wajah menggunakan pickle
            encoding_blob = pickle.dumps(face_encoding)

            # Koneksi ke database
            db_conn = psycopg2.connect(
                host="localhost",
                user="postgres",
                password="2655",
                dbname="attendancedbb"
            )
            cursor = db_conn.cursor()

            # Simpan data karyawan
            cursor.execute("INSERT INTO employee (name, face_encoding) VALUES (%s, %s)", (name, encoding_blob))
            db_conn.commit()

            cursor.close()
            db_conn.close()
            print(f"Employee {name} saved successfully.")
        else:
            print("No face encodings found in the image.")

    except Exception as e:
        print(f"Error saving employee: {e}")

#fungsi untuk Memuat encoding wajah yang dikenal dari database untuk digunakan dalam pengenalan wajah.
def load_known_faces():
    global Known_employee_encodings, Known_employee_names, Known_employee_rolls
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Ambil semua data karyawan dari database
        cursor.execute("SELECT id_karyawan, name, face_encoding FROM employee")
        rows = cursor.fetchall()

        for row in rows:
            id_karyawan, nama, face_encoding = row
            if face_encoding is not None:
                # Deserialize face_encoding dari BLOB
                encoding = pickle.loads(face_encoding)
                Known_employee_encodings.append(encoding)
                Known_employee_names.append(nama)
                Known_employee_rolls.append(id_karyawan)

        cursor.close()
        db_conn.close()
        logging.info("Known faces loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading known faces: {e}")

# fungsi untuk Mendeteksi dan mengenali wajah dalam frame video.
def recognize_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    names = []
    rolls = []
    
    for face_encoding in face_encodings:
        # Log encoding wajah yang baru
        logging.info(f"New face encoding: {face_encoding}")

        # Menggunakan face_distance untuk mendapatkan jarak
        face_distances = face_recognition.face_distance(Known_employee_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if face_distances[best_match_index] < 0.4:  # Sesuaikan threshold sesuai kebutuhan
            name = Known_employee_names[best_match_index]
            roll = Known_employee_rolls[best_match_index]
        else:
            name = "Unknown"
            roll = "Unknown"

        names.append(name)
        rolls.append(roll)

        # Log hasil pencocokan
        logging.info(f"Matched name: {name}, roll: {roll}")

    return face_locations, names, rolls

def is_face_in_correct_region(roll, selected_region_id):
    """
    Memeriksa apakah karyawan dengan roll tertentu terdaftar di region yang sesuai.

    :param roll: ID karyawan (roll number)
    :param selected_region_id: ID region yang dipilih
    :return: True jika karyawan terdaftar di region, False sebaliknya
    """
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Query untuk memeriksa apakah karyawan terdaftar di region yang sesuai
        cursor.execute("""
            SELECT COUNT(*) 
            FROM employee 
            WHERE id_karyawan = %s AND region_id = %s
        """, (roll, selected_region_id))

        count = cursor.fetchone()[0]
        return count > 0  # Kembali True jika ada kecocokan, False jika tidak ada
    except Exception as e:
        logging.error(f"Error memeriksa kecocokan region: {e}")
        return False  # Kembali False jika terjadi kesalahan
    finally:
        cursor.close()  # Pastikan cursor ditutup
        db_conn.close()  # Pastikan koneksi ditutup

def generate_marked_frames(selected_region_id):
    global speech_queue, error_announced, error_timestamp
    camera = cv2.VideoCapture(0)
    recognized_names = set()
    unknown_face_alerted = False
    region_mismatch_alerted = False
    frame_skip = 5
    frame_count = 0
    processed_employees = set()  # Menyimpan nama yang sudah diproses untuk speech

    while True:
        success, frame = camera.read()
        if not success or frame is None or frame.size == 0:
            logging.error("Gagal menangkap frame dari kamera atau frame kosong.")
            continue
        
        frame_count += 1
        
        if frame_count % frame_skip != 0:
            continue

        frame = cv2.resize(frame, (320, 240))
        faces, names, rolls = recognize_faces(frame)

        found_unknown = False

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

        for (top, right, bottom, left), name, roll in zip(faces, names, rolls):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            display_name = get_latest_employee_name(roll) or "Unknown"
            logging.debug(f"Displaying: {display_name} ({roll})")
            
            if not is_employee_active(roll):
                logging.info(f"Karyawan dengan ID {roll} tidak aktif. Lewati.")
                continue

            cv2.putText(frame, f"{display_name} ({roll})", (left, bottom + 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)

            if roll != "Unknown":
                unknown_face_alerted = False
                
                # Ambil status allowed dari region
                region_allowed = get_region_allowed(selected_region_id)

                # Simpan foto dan data ke database
                photo_filename = f"./Train/{name}_attendance.jpg"
                cv2.imwrite(photo_filename, frame)

                try:
                    db_conn = get_db_connection()
                    cursor = db_conn.cursor()
                    
                    # Cek jika region diizinkan
                    if region_allowed or is_face_in_correct_region(roll, selected_region_id):
                        # Cek apakah karyawan sudah absen dalam durasi blokir terakhir di region ini
                        last_absence_time = get_last_absence_time(roll, selected_region_id)
                        if last_absence_time and (datetime.now() - last_absence_time).total_seconds() < blocking_duration * 60:
                            # Jika sudah absen dalam durasi blokir terakhir dan belum diproses
                            if roll not in processed_employees:
                                speech_queue.put("Akses diterima, terimakasih.")
                                processed_employees.add(roll)  # Tandai sudah diproses
                        else:
                            # Jika belum absen dalam durasi blokir
                            cursor.execute(
                                "INSERT INTO absensi (nama, id_karyawan, check_in, photo, region_id) VALUES (%s, %s, NOW(), %s, %s)", 
                                (display_name, roll, photo_filename, selected_region_id)
                            )
                            db_conn.commit()
                            speech_queue.put("Berhasil.")
                        
                        recognized_names.add(name)
                    else:
                        if not region_mismatch_alerted:
                            speech_queue.put("Tidak sesuai area finger.")
                            region_mismatch_alerted = True

                except Exception as e:
                    logging.error(f"Error menyimpan data absen: {e}")
                    speech_queue.put("Terjadi kesalahan saat mencatat absensi.")
                finally:
                    cursor.close()
                    db_conn.close()
            else:
                found_unknown = True

        if found_unknown and not unknown_face_alerted:
            speech_queue.put("Wajah tidak dikenali, silahkan coba lagi.")
            unknown_face_alerted = True

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logging.error("Gagal mengubah frame ke format JPEG.")
            break

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

def get_last_absence_time(employee_id, region_id):
    """ Fungsi untuk mengambil waktu absensi terakhir dari database berdasarkan karyawan dan region """
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT check_in FROM absensi WHERE id_karyawan = %s AND region_id = %s ORDER BY check_in DESC LIMIT 1", 
        (employee_id, region_id)
    )
    result = cursor.fetchone()
    cursor.close()
    db_conn.close()
    
    if result:
        return result[0]
    return None

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

def process_images(files, name, roll):
    saved_files = []
    for idx, file in enumerate(files):
        if file and allowed_file(file.filename):
            ext = file.filename.split('.')[-1]
            stfilename = f"{name}_{roll}_{idx + 1}.{ext}"

            file_path = os.path.join('./Train/', stfilename)
            file.save(file_path)
            saved_files.append(file_path)

            newImg = cv2.imread(file_path)
            if newImg is None:
                os.remove(file_path)
                return None, True  # Gambar tidak valid

            face_encodings = face_recognition.face_encodings(cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB))
            if len(face_encodings) == 0:
                os.remove(file_path)
                return None, True  # Tidak ada wajah terdeteksi

            return face_encodings[0], saved_files  # Kembalikan encoding wajah dan daftar file

    return None, saved_files  # Jika tidak ada file yang valid

def save_to_database(name, roll, newEncode, saved_files_pg, region_id):
    try:
        with get_db_connection() as db_conn:
            cursor = db_conn.cursor()
            face_encoding_bytes = pickle.dumps(newEncode)

            cursor.execute(
                "INSERT INTO employee (name, id_karyawan, face_encoding, photo, region_id) VALUES (%s, %s, %s, %s, %s)",
                (name, roll, face_encoding_bytes, saved_files_pg, region_id)
            )
            db_conn.commit()
    except Exception as e:
        logging.error(f"Error saving to database: {e}")
        return False
    return True
        
def get_latest_employee_name(roll):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM employee WHERE id_karyawan = %s", (roll,))
    result = cursor.fetchone()
    cursor.close()
    db_conn.close()
    
    return result[0] if result else None

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

                                    
# fungsi untuk Mengonversi gambar ke format Base64.
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# fungsi untuk Menghapus data karyawan dan foto terkait dari database.
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

# decorators untuk membatasi akses berdasarkan role
def role_required(roles):
    # Pastikan roles adalah list jika hanya satu role yang diberikan
    if isinstance(roles, str):
        roles = [roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Memeriksa apakah role pengguna ada di dalam roles yang diizinkan
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('login'))  # Ganti 'login' dengan rute Anda
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Fungsi untuk memvalidasi region saat absensi
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

def get_regions():
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, name, allowed FROM region WHERE is_active = TRUE")
    regions = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return regions

def get_region_allowed(region_id):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("SELECT allowed FROM region WHERE id = %s", (region_id,))
        result = cursor.fetchone()
        return result[0] if result else False
    except Exception as e:
        logging.error(f"Error mendapatkan status allowed: {e}")
        return False
    finally:
        cursor.close()
        db_conn.close()

def is_employee_active(roll):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT status FROM employee WHERE id_karyawan = %s", (roll,))
        status = cursor.fetchone()
        return status is not None and status[0] == 'A'
    except Exception as e:
        logging.error(f"Error checking employee status: {e}")
        return False
    finally:
        cursor.close()
        db_conn.close()    
    
# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     role = session.get('role')
    
#     if role == 'admin':
#         return render_template('admin_dashboard.html')
#     elif role == 'super_admin':
#         return render_template('super_admin_dashboard.html')
#     else:
#         return "Unauthorized access", 403

#@app.route('/admin')
#@role_required('admin')  # Hanya admin yang bisa akses
#def admin_dashboard():
#   return render_template('admin_dashboard.html')

#@app.route('/superadmin')
#@role_required('super_admin')  # Hanya super admin yang bisa akses
#def superadmin_dashboard():
#    return render_template('superadmin_dashboard.html')

# Global variable to hold the updated employee name
@app.route('/update_employee_superadmin/<int:id_karyawan>', methods=['GET', 'POST'])
@role_required(['super_admin'])
def update_employee_superadmin(id_karyawan):
    global current_employee_name_superadmin  # Deklarasi variabel global

    if request.method == 'POST':
        nama = request.form['nama']
        region_id = request.form['region_id']
        
        try:
            update_by = session.get('user_name')
            db_conn = get_db_connection()
            cursor = db_conn.cursor()

            cursor.execute("""
                UPDATE employee 
                SET name = %s, region_id = %s, tgl_update = CURRENT_TIMESTAMP, update_by = %s
                WHERE id_karyawan = %s
            """, (nama, region_id, update_by, id_karyawan))
            db_conn.commit()

            current_employee_name_superadmin = nama  # Perbarui nama
            return redirect(url_for('tampil_data_superadmin'))
        except Exception as e:
            logging.error(f"Error updating employee data: {e}")
            db_conn.rollback()
            flash("Terjadi kesalahan saat memperbarui data karyawan.", "danger")
        finally:
            cursor.close()
            db_conn.close()

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee WHERE id_karyawan = %s", (id_karyawan,))
    karyawan = cursor.fetchone()

    cursor.close()
    db_conn.close()

    return render_template('update_employee_superadmin.html', karyawan=karyawan)

@app.route('/hapus_karyawan/<int:id_karyawan>', methods=['POST'])
@role_required(['super_admin'])
def hapus_karyawan(id_karyawan):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        # Ambil nama superadmin yang sedang login
        delete_by = session.get('user_name')  # Jika menggunakan Flask-Login, bisa ganti dengan current_user.name

        cursor.execute("""
            UPDATE employee 
            SET status = 'N', tgl_delete = CURRENT_TIMESTAMP, delete_by = %s 
            WHERE id_karyawan = %s
        """, (delete_by, id_karyawan))
        db_conn.commit()
    except Exception as e:
        logging.error(f"Error deleting employee: {e}")
        db_conn.rollback()

    finally:
        cursor.close()
        db_conn.close()

    return redirect(url_for('tampil_data_superadmin'))

@app.route('/update_employee_admin/<int:id_karyawan>', methods=['GET', 'POST'])
@role_required(['admin'])
def update_employee_admin(id_karyawan):
    global current_employee_name_admin

    if request.method == 'POST':
        new_name = request.form['name']
        try:
            update_by = session.get('user_name')
            db_conn = get_db_connection()
            cursor = db_conn.cursor()

            cursor.execute("""
                UPDATE employee 
                SET name = %s, update_by = %s
                WHERE id_karyawan = %s AND status != 'Deleted'
            """, (new_name, update_by, id_karyawan))
            db_conn.commit()

            current_employee_name_admin = new_name  # Perbarui nama

        except Exception as e:
            logging.error(f"Error updating employee name: {e}")
            return "An error occurred while updating the data.", 500

        finally:
            cursor.close()
            db_conn.close()

        return redirect(url_for('tampil_data_admin'))

    employee_data = None
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT id_karyawan, name
            FROM employee 
            WHERE id_karyawan = %s AND status != 'Deleted'
        """, (id_karyawan,))
        employee_data = cursor.fetchone()

    except Exception as e:
        logging.error(f"Error fetching employee data for update: {e}")
        return "An error occurred while fetching data for the update.", 500

    finally:
        cursor.close()
        db_conn.close()

    if employee_data is None:
        flash('Data karyawan tidak ditemukan.', 'error')
        return redirect(url_for('tampil_data_admin'))

    return render_template('update_employee_admin.html', employee_data=employee_data)

@app.route('/hapus_karyawan_admin/<int:id_karyawan>', methods=['POST'])
@role_required(['admin'])  # Hanya mengizinkan admin
def hapus_karyawan_admin(id_karyawan):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Ambil nama admin yang sedang login
        delete_by = session.get('user_name')  # Jika menggunakan Flask-Login, bisa ganti dengan current_user.name

        # Update status menjadi 'N' untuk menandakan data tidak aktif dan catat siapa yang menghapus
        cursor.execute("""
            UPDATE employee 
            SET status = 'N', delete_by = %s
            WHERE id_karyawan = %s AND status != 'N'
        """, (delete_by, id_karyawan))
        db_conn.commit()  # Pastikan perubahan disimpan ke database

    except Exception as e:
        db_conn.rollback()  # Jika terjadi error, batalkan perubahan
        logging.error(f"Error deleting employee: {e}")
        return "Terjadi kesalahan saat menghapus karyawan.", 500  # Tampilkan pesan error jika terjadi kesalahan

    finally:
        cursor.close()  # Menutup cursor
        db_conn.close()  # Menutup koneksi ke database

    return redirect(url_for('tampil_data_admin'))  # Arahkan ke halaman data karyawan admin
    
@app.route('/')
@login_required
def index():
    if 'logged_in' in session:
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM login")
            total_pengguna = cursor.fetchone()
            
            cursor.execute("SELECT * FROM login")
            users = cursor.fetchall()
            
            cursor.close()
            db_conn.close()
        except Exception as e:
            logging.error(f"Error fetching user data: {e}")
            total_pengguna = (0,)
            users = []

        return render_template('index.html', nama=session['nama'], username=session['username'], total_pengguna=total_pengguna, users=users)
    else:
        return redirect('/loginsignup')

@app.route('/attendance', methods=['GET', 'POST'])
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

@app.route('/video/<int:region_id>')
def video(region_id):
    return Response(generate_marked_frames(region_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/table_admin')
@role_required(['admin'])  # Hanya mengizinkan admin
def table_admin():
    return fetch_absensi_data('table_admin.html')

@app.route('/table_superadmin')
@role_required(['super_admin'])  # Hanya mengizinkan super_admin
def table_superadmin():
    return fetch_absensi_data('table_superadmin.html')

def fetch_absensi_data(template_name):
    absensi_data = []  # Inisialisasi data absensi
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        region = request.args.get('region')

        # Query untuk mengambil data absensi
        query = "SELECT nama, id_karyawan, check_in, photo, region_id FROM absensi WHERE 1=1"
        params = []

        # Tambahkan filter berdasarkan tanggal
        if start_date and end_date:
            query += " AND check_in BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        # Tambahkan filter berdasarkan region
        if region:
            query += " AND region_id = %s"
            params.append(region)

        cursor.execute(query, params)
        absensi_data = cursor.fetchall()

    except Exception as e:
        logging.error(f"Error fetching attendance data: {e}")
    finally:
        cursor.close()
        db_conn.close()

    # Menyediakan data ke template
    return render_template(template_name, data=absensi_data)

@app.route('/upload_superadmin', methods=['GET', 'POST'])
@role_required(['super_admin'])
def upload_superadmin():
    if request.method == 'POST':
        files = request.files.getlist('images')
        name = request.form['name']
        roll = request.form['roll']
        region_id = request.form['region_id']
        image_data = request.form.getlist('image_data')  # Ambil semua data gambar dari kamera

        # Hitung total gambar yang akan diproses
        total_images = len(files) + len(image_data)
        
        # Validasi input
        if total_images == 0 or not (1 <= total_images <= 10) or not name or not roll or not region_id:
            flash("Validasi gagal. Pastikan minimal 1 gambar diunggah atau ditangkap, dan tidak lebih dari 10 gambar total.", "error")
            return redirect(url_for('upload_superadmin'))

        newEncode = None
        saved_files = []

        # Proses file yang diunggah
        newEncode, saved_files = process_images(files, name, roll)

        # Proses gambar yang ditangkap dari kamera
        for img_data in image_data:
            if img_data:  # Pastikan img_data tidak kosong
                parts = img_data.split(',')
                if len(parts) > 1:  # Pastikan ada data setelah split
                    img_data = parts[1]  # Ambil data gambar
                    
                    try:
                        img_bytes = base64.b64decode(img_data)
                    except Exception as e:
                        flash("Gagal mendekode gambar yang ditangkap.", "error")
                        return redirect(url_for('upload_superadmin'))

                    image_path = os.path.join('./Train/', f"{name}_{roll}_captured_{len(saved_files)}.jpg")
                    with open(image_path, 'wb') as f:
                        f.write(img_bytes)
                    saved_files.append(image_path)

                    newImg = cv2.imread(image_path)
                    if newImg is None or not face_recognition.face_encodings(cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB)):
                        os.remove(image_path)
                        flash("Gambar yang ditangkap tidak valid. Tidak ada wajah terdeteksi.", "error")
                        return redirect(url_for('upload_superadmin'))

                    face_encodings = face_recognition.face_encodings(cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB))
                    newEncode = face_encodings[0]

        # Simpan ke database jika berhasil
        if newEncode is not None:
            saved_files_pg = "{" + ",".join([f'"{file_path}"' for file_path in saved_files]) + "}"
            if save_to_database(name, roll, newEncode, saved_files_pg, region_id):
                flash("Upload berhasil!", "success")
                return redirect(url_for('upload_superadmin'))
            else:
                flash("Gagal menyimpan ke database.", "error")

        # Hapus file yang disimpan jika terjadi kesalahan
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    # Untuk permintaan GET, ambil data region
    regions = get_regions()  
    return render_template('upload_superadmin.html', regions=regions)

@app.route('/upload_admin', methods=['GET', 'POST'])
@role_required(['admin'])
def upload_admin():
    if request.method == 'POST':
        files = request.files.getlist('images')
        name = request.form['name']
        roll = request.form['roll']
        region_id = request.form['region_id']
        image_data = request.form.getlist('image_data')  # Ambil semua data gambar dari kamera

        # Hitung total gambar yang akan diproses
        total_images = len(files) + len(image_data)
        
        # Validasi input
        if total_images == 0 or not (1 <= total_images <= 10) or not name or not roll or not region_id:
            flash("Validasi gagal. Pastikan minimal 1 gambar diunggah atau ditangkap, dan tidak lebih dari 10 gambar total.", "error")
            return redirect(url_for('upload_admin'))

        newEncode = None
        saved_files = []

        # Proses file yang diunggah
        newEncode, saved_files = process_images(files, name, roll)

        # Proses gambar yang ditangkap dari kamera
        for img_data in image_data:
            if img_data:  # Pastikan img_data tidak kosong
                parts = img_data.split(',')
                if len(parts) > 1:  # Pastikan ada data setelah split
                    img_data = parts[1]  # Ambil data gambar
                    
                    try:
                        img_bytes = base64.b64decode(img_data)
                    except Exception as e:
                        flash("Gagal mendekode gambar yang ditangkap.", "error")
                        return redirect(url_for('upload_admin'))

                    image_path = os.path.join('./Train/', f"{name}_{roll}_captured_{len(saved_files)}.jpg")
                    with open(image_path, 'wb') as f:
                        f.write(img_bytes)
                    saved_files.append(image_path)

                    newImg = cv2.imread(image_path)
                    if newImg is None or not face_recognition.face_encodings(cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB)):
                        os.remove(image_path)
                        flash("Gambar yang ditangkap tidak valid. Tidak ada wajah terdeteksi.", "error")
                        return redirect(url_for('upload_admin'))

                    face_encodings = face_recognition.face_encodings(cv2.cvtColor(newImg, cv2.COLOR_BGR2RGB))
                    newEncode = face_encodings[0]

        # Simpan ke database jika berhasil
        if newEncode is not None:
            saved_files_pg = "{" + ",".join([f'"{file_path}"' for file_path in saved_files]) + "}"
            if save_to_database(name, roll, newEncode, saved_files_pg, region_id):
                flash("Upload berhasil!", "success")
                return redirect(url_for('upload_admin'))
            else:
                flash("Gagal menyimpan ke database.", "error")

        # Hapus file yang disimpan jika terjadi kesalahan
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    # Untuk permintaan GET, ambil data region
    regions = get_regions()  
    return render_template('upload_admin.html', regions=regions)

@app.route('/add_region', methods=['GET', 'POST'])
@role_required(['admin'])
def add_region():
    if request.method == 'POST':
        name = request.form['name']
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO region (name) VALUES (%s)", (name,))
            db_conn.commit()
            flash("Region berhasil ditambahkan!", "success")
        except Exception as e:
            logging.error(f"Error adding region: {e}")
            flash("Terjadi kesalahan saat menambahkan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()
        return redirect(url_for('admin_regions'))

    return render_template('add_region.html')

@app.route('/regions', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_regions():
    if request.method == 'POST':
        allowed_ids = request.form.getlist('allowed_region')
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("UPDATE region SET allowed = FALSE")
            if allowed_ids:
                cursor.execute("UPDATE region SET allowed = TRUE WHERE id IN %s", (tuple(allowed_ids),))
            db_conn.commit()
            flash("Pengaturan region berhasil diperbarui!", "success")
        except Exception as e:
            logging.error(f"Error updating allowed regions: {e}")
            flash("Terjadi kesalahan saat memperbarui pengaturan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()

    regions = get_regions()
    return render_template('regions.html', regions=regions)

@app.route('/add_superadmin_region', methods=['GET', 'POST'])
@role_required(['super_admin'])
def add_superadmin_region():
    if request.method == 'POST':
        name = request.form['name']
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO region (name) VALUES (%s)", (name,))
            db_conn.commit()
            flash("Region berhasil ditambahkan!", "success")
        except Exception as e:
            logging.error(f"Error adding superadmin region: {e}")
            flash("Terjadi kesalahan saat menambahkan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()
        return redirect(url_for('superadmin_regions'))

    return render_template('add_superadmin_region.html')

@app.route('/superadmin_regions', methods=['GET', 'POST'])
@role_required(['super_admin'])
def superadmin_regions():
    if request.method == 'POST':
        allowed_ids = request.form.getlist('allowed_region')
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("UPDATE region SET allowed = FALSE")
            if allowed_ids:
                cursor.execute("UPDATE region SET allowed = TRUE WHERE id IN %s", (tuple(allowed_ids),))
            db_conn.commit()
            flash("Pengaturan region berhasil diperbarui!", "success")
        except Exception as e:
            logging.error(f"Error updating allowed regions: {e}")
            flash("Terjadi kesalahan saat memperbarui pengaturan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()

    regions = get_regions()
    return render_template('superadmin_regions.html', regions=regions)

@app.route('/deactivate_region_superadmin/<int:id>', methods=['POST'])
@role_required(['super_admin'])
def deactivate_region_superadmin(id):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Tandai region sebagai tidak aktif
        cursor.execute("UPDATE region SET is_active = FALSE WHERE id = %s", (id,))
        db_conn.commit()
        flash("Region berhasil dinonaktifkan!", "success")
    except Exception as e:
        logging.error(f"Error deactivating region: {e}")
        flash("Terjadi kesalahan saat menonaktifkan region.", "danger")
    finally:
        cursor.close()
        db_conn.close()
    return redirect(url_for('superadmin_regions'))

@app.route('/deactivate_region_admin/<int:id>', methods=['POST'])
@role_required(['admin'])
def deactivate_region_admin(id):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Tandai region sebagai tidak aktif
        cursor.execute("UPDATE region SET is_active = FALSE WHERE id = %s", (id,))
        db_conn.commit()
        flash("Region berhasil dinonaktifkan!", "success")
    except Exception as e:
        logging.error(f"Error deactivating region: {e}")
        flash("Terjadi kesalahan saat menonaktifkan region.", "danger")
    finally:
        cursor.close()
        db_conn.close()
    return redirect(url_for('admin_region'))

@app.route('/tampil_data_admin', methods=['GET'])
@role_required(['admin'])  # Hanya mengizinkan admin
def tampil_data_admin():
    search_query = request.args.get('search', '')  # Ambil kata kunci pencarian dari URL
    data_list = []
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Query SQL untuk mencari karyawan berdasarkan nama dan memastikan status aktif
        if search_query:
            cursor.execute("""
                SELECT id_karyawan, name
                FROM employee 
                WHERE LOWER(name) LIKE LOWER(%s) AND status != 'N'
            """, ('%' + search_query + '%',))  # Menambahkan wildcard '%' di sekitar kata kunci
        else:
            cursor.execute("""
                SELECT id_karyawan, name
                FROM employee 
                WHERE status != 'N'
            """)

        data_list = cursor.fetchall()  # Ambil hasil query

    except Exception as e:
        logging.error(f"Error fetching employee data for admin: {e}")
        return "Terjadi kesalahan dalam mengambil data.", 500

    finally:
        cursor.close()
        db_conn.close()

    return render_template('tampil_data_admin.html', data_list=data_list)

@app.route('/tampil_data_superadmin', methods=['GET'])
@role_required(['super_admin'])  # Hanya mengizinkan super_admin
def tampil_data_superadmin():
    data_list = []
    query = request.args.get('query', '')  # Ambil parameter pencarian
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Query dengan filter pencarian yang tidak case sensitive
        if query:
            cursor.execute("""
                SELECT * 
                FROM employee 
                WHERE LOWER(name) LIKE LOWER(%s) 
                ORDER BY tgl_create DESC
            """, (f"%{query}%",))
        else:
            cursor.execute("SELECT * FROM employee ORDER BY tgl_create DESC")
        
        data_list = cursor.fetchall()
    except Exception as e:
        logging.error(f"Error fetching employee data for superadmin: {e}")
    finally:
        cursor.close()
        db_conn.close()

    return render_template('tampil_data_superadmin.html', data_list=data_list)

@app.route('/report_admin')
@role_required(['admin'])  # Mengizinkan hanya admin
def report_admin():
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        cursor.execute("SELECT nama, id_karyawan, check_in, region_id FROM absensi")
        report_data = cursor.fetchall()
        
        cursor.close()
        db_conn.close()
        
        if not report_data:
            logging.warning("No data found for attendance report for admin.")
    except Exception as e:
        logging.error(f"Error fetching attendance report data for admin: {e}")
        report_data = []

    return render_template('report_admin.html', report_data=report_data)

@app.route('/report_superadmin')
@role_required(['super_admin'])  # Mengizinkan hanya super_admin
def report_super_admin():
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        cursor.execute("SELECT nama, id_karyawan, check_in, region_id FROM absensi")
        report_data = cursor.fetchall()
        
        cursor.close()
        db_conn.close()
        
        if not report_data:
            logging.warning("No data found for attendance report for super admin.")
    except Exception as e:
        logging.error(f"Error fetching attendance report data for super admin: {e}")
        report_data = []

    return render_template('report_superadmin.html', report_data=report_data)

import tempfile

@app.route('/report/download')
@role_required(['admin', 'super_admin'])
def download_report():
    format_type = request.args.get('format')
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("SELECT nama, id_karyawan, check_in, region_id FROM absensi")
        report_data = cursor.fetchall()
        cursor.close()
        db_conn.close()

        if not report_data:
            return "Tidak ada data untuk membuat laporan", 404

        if format_type == 'pdf':
            html_content = render_template('report_pdf.html', report_data=report_data)
            path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                pdfkit.from_string(html_content, temp_pdf.name, configuration=config)
                response = send_file(
                    temp_pdf.name,
                    as_attachment=True,
                    download_name='laporan_absensi.pdf'
                )

            return response  # File temp_pdf akan dihapus setelah request selesai

        elif format_type == 'excel':
            df = pd.DataFrame(report_data, columns=['Nama Karyawan', 'ID Karyawan', 'Waktu Check-in', 'Region'])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
                df.to_excel(temp_excel.name, index=False)
                response = send_file(
                    temp_excel.name,
                    as_attachment=True,
                    download_name='laporan_absensi.xlsx'
                )

            return response  # File temp_excel akan dihapus setelah request selesai

        else:
            return "Format tidak valid", 400

    except Exception as e:
        app.logger.error(f"Error generating report: {e}")
        return "Terjadi kesalahan saat membuat laporan", 500
    
@app.route('/add_admin', methods=['GET', 'POST'])
@role_required(['super_admin'])
def add_admin():
    if request.method == 'POST':
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']
        role = 'admin'

        # Validasi input
        if not nama or not username or not password:
            flash("Semua bidang wajib diisi!", "danger")
            return redirect(url_for('add_admin'))

        if not re.match(r"^[\w.%+-]+@gmail\.com$", username):
            flash("Username harus berupa email dengan domain @gmail.com.", "danger")
            return redirect(url_for('add_admin'))

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$", password):
            flash("Password harus memiliki minimal 8 karakter, mengandung huruf besar, huruf kecil, angka, dan simbol.", "danger")
            return redirect(url_for('add_admin'))

        # Hash password
        hashed_password = sha256_crypt.hash(password)

        try:
            # Simpan data ke database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (nama, username, password, role) 
                VALUES (%s, %s, %s, %s)
            """, (nama, username, hashed_password, role))
            conn.commit()
            flash("Admin berhasil ditambahkan!", "success")
        except psycopg2.IntegrityError:
            conn.rollback()  # Pastikan perubahan dibatalkan jika terjadi error
            flash("Username sudah terdaftar.", "danger")
            return redirect(url_for('add_admin'))
        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
            return redirect(url_for('add_admin'))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('add_admin'))

    return render_template('add_admin.html')


# Route untuk mengatur durasi blocking
@app.route('/blocking_settings', methods=['GET', 'POST'])
@role_required(['super_admin'])
def blocking_settings():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_duration = request.form.get('blocking_duration')
        try:
            cursor.execute(
                "UPDATE global_settings SET setting_value = %s WHERE setting_key = 'blocking_duration_minutes'",
                (new_duration,)
            )
            conn.commit()
            print("Blocking duration updated successfully.")
            flash('Durasi blocking berhasil diperbarui.', 'success')
        except Exception as e:
            flash(f'Gagal memperbarui durasi blocking: {e}', 'error')

    cursor.execute("SELECT setting_value FROM global_settings WHERE setting_key = 'blocking_duration_minutes'")
    current_duration = cursor.fetchone()[0]
    conn.close()

    return render_template('blocking_settings.html', current_duration=current_duration)

#@app.route('/delete_employee/<int:id_karyawan>', methods=['POST'])
#def delete_employee(id_karyawan):
#    try:
#        db_conn = get_db_connection()
#        cursor = db_conn.cursor()

        # Hapus data karyawan dari database
 #       cursor.execute("DELETE FROM employee WHERE id_karyawan = %s", (id_karyawan,))
 #       db_conn.commit()

        # Hapus foto-foto terkait dari folder 'Train'
  #      delete_employee_data(id_karyawan)

 #       cursor.close()
  #      db_conn.close()
 #       logging.info(f"Employee with ID {id_karyawan} has been deleted.")
 #       return redirect('/tampil_data')
 #   except Exception as e:
  #      logging.error(f"Error deleting employee: {e}")
  #      return "Error deleting employee", 500
                
@app.route('/loginsignup')
def loginsignup():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usr']
        password = request.form['pwd']

        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result and sha256_crypt.verify(password, result[0]):
                # Login berhasil
                role = result[1]
                session['username'] = username
                session['role'] = role

                cursor.close()
                db_conn.close()

                # Redirect berdasarkan role
                if role == 'admin':
                    return redirect('/admin_dashboard')
                elif role == 'super_admin':
                    return redirect('/super_admin_dashboard')
            else:
                cursor.close()
                db_conn.close()
                flash("Invalid username or password.", "danger")
                return render_template('login.html', error_message='Invalid username or password')
        except Exception as e:
            logging.error(f"Database connection error during login: {e}")
            return render_template('login.html', error_message='Database connection error')

    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Menghitung total pengguna dari tabel users
    total_pengguna = User.query.count()  # Menghitung total pengguna
    total_karyawan = Employee.query.count()  # Menghitung jumlah karyawan
    users = Employee.query.all()  # Ambil semua data karyawan

    return render_template('admin_dashboard.html', 
                           username=session['username'], 
                           total_pengguna=total_pengguna, 
                           total_karyawan=total_karyawan, 
                           users=users)

@app.route('/super_admin_dashboard')
def super_admin_dashboard():
    if 'username' not in session or session.get('role') != 'super_admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Menghitung total pengguna
    cursor.execute("SELECT COUNT(*) FROM users")
    total_pengguna = cursor.fetchone()[0]

    # Menghitung jumlah admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    total_admin = cursor.fetchone()[0]

    # Mengambil data pengguna terbaru berdasarkan ID atau kolom lain yang ada
    cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 10")  # Ganti 'id' dengan kolom yang sesuai
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('super_admin_dashboard.html', 
                           total_pengguna=total_pengguna, 
                           total_admin=total_admin, 
                           users=users,
                           nama=session['username'])
    
    
@app.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#@app.route('/signup', methods=['GET', 'POST'])
#def signup():
 #   if request.method == 'POST':
  #      username_up = request.form['usrup']
  #      password_up = request.form['pwdup']
  #      nama = request.form['nama']
  #      hashed_password = sha256_crypt.hash(password_up)
        
   #     try:
   #         db_conn = get_db_connection()
   #         cursor = db_conn.cursor()
   #         cursor.execute("INSERT INTO login (nama, username, password) VALUES (%s, %s, %s)", 
   #                        (nama, username_up, hashed_password))
    #        db_conn.commit()
    #        cursor.close()
   #         db_conn.close()
            
    #        logging.info("New user signed up successfully.")
     #       return redirect('/loginsignup')
     #   except Exception as e:
     #       logging.error(f"Database connection error during signup: {e}")
     #       return render_template('login.html', error_message='Database connection error')
   # return render_template('login.html')

# @app.route('/logout', methods=['GET', 'POST'])
# def logout():
#     session.clear()
#     logging.info("User logged out.")
#     return redirect('/loginsignup')

if __name__ == "__main__":
    load_known_faces()
    app.run(host='127.0.0.1', port=5000, debug=True)