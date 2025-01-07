from flask import flash, request, redirect, url_for, render_template
import os
import cv2
import base64
import face_recognition
from utils.proses_gambar import process_images
from utils.save_ke_db import save_to_database
from utils.g_region import get_regions

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