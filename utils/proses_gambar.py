import os
import cv2
import face_recognition
from utils.allow_file import allowed_file

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