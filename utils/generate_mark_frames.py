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
from utils.inisialisasi_antrian_suara import speech_queue, error_announced, error_timestamp

def generate_marked_frames(selected_region_id):
    global speech_queue, error_announced, error_timestamp
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    recognized_names = set()
    unknown_face_alerted = False
    region_mismatch_alerted = False
    frame_skip = 5
    frame_count = 0
    processed_employees = set()  # Menyimpan nama yang sudah diproses untuk speech

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
                        if last_absence_time and (datetime.datetime.now() - last_absence_time).total_seconds() < blocking_duration * 60:
                            if roll not in processed_employees:
                                speech_queue.put("Akses diterima, terimakasih.")
                                processed_employees.add(roll)
                        else:
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
