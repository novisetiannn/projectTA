import face_recognition
import pickle
import psycopg2

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