import cv2
import logging
import datetime
from database import get_db_connection
from utils.mendeteksi_mengenali_frame import recognize_faces
from utils.latest_employee import get_latest_employee_name
from utils.employee_active import is_employee_active
from utils.get_region import get_region_allowed
from utils.periksa_wajah_sesuai_region import is_face_in_correct_region
from utils.waktu_terakhir_absen import get_last_absence_time
from utils.inisialisasi_antrian_suara import speech_queue

def generate_marked_frames(selected_region_id):
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    processed_employees = set()  # Melacak ID karyawan yang sudah diproses
    frame_skip = 5
    frame_count = 0

    # Cek apakah kamera terbuka
    if not camera.isOpened():
        logging.error("Kamera tidak dapat dibuka.")
        return

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
            blocking_duration = int(blocking_duration_result[0]) if blocking_duration_result else 10
        except Exception as e:
            logging.error(f"Error saat mengambil durasi blokir: {e}")
            blocking_duration = 10  # Default fallback
        finally:
            cursor.close()
            db_conn.close()

        for (top, right, bottom, left), name, roll in zip(faces, names, rolls):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            display_name = get_latest_employee_name(roll) or "Unknown"
            cv2.putText(frame, f"{display_name} ({roll})", (left, bottom + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)

            # Proses hanya jika wajah dikenal dan belum diproses
            if roll != "Unknown" and roll not in processed_employees:
                region_allowed = get_region_allowed(selected_region_id)
                last_absence_time = get_last_absence_time(roll, selected_region_id)

                try:
                    db_conn = get_db_connection()
                    cursor = db_conn.cursor()

                    # Cek apakah region diizinkan atau sesuai
                    if region_allowed or is_face_in_correct_region(roll, selected_region_id):
                        # Periksa apakah karyawan sudah absen dalam durasi blokir terakhir
                        if last_absence_time and (datetime.datetime.now() - last_absence_time).total_seconds() < blocking_duration * 60:
                            speech_queue.put("Akses diterima, terimakasih.")
                        else:
                            photo_filename = f"./Train/{name}_attendance.jpg"
                            cv2.imwrite(photo_filename, frame)

                            cursor.execute(
                                "INSERT INTO absensi (nama, id_karyawan, check_in, photo, region_id) VALUES (%s, %s, NOW(), %s, %s)",
                                (display_name, roll, photo_filename, selected_region_id)
                            )
                            db_conn.commit()
                            speech_queue.put("Berhasil.")

                        processed_employees.add(roll)  # Tandai wajah sebagai diproses
                    else:
                        speech_queue.put("Tidak sesuai area finger.")
                except Exception as e:
                    logging.error(f"Error menyimpan data absen: {e}")
                    speech_queue.put("Terjadi kesalahan saat mencatat absensi.")
                finally:
                    cursor.close()
                    db_conn.close()

            elif roll == "Unknown" and "Unknown" not in processed_employees:
                speech_queue.put("Wajah tidak dikenali, silahkan coba lagi.")
                processed_employees.add("Unknown")

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logging.error("Gagal mengubah frame ke format JPEG.")
            break

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()
