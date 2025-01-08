from flask import flash, redirect, url_for
from database import get_db_connection
from passlib.hash import sha256_crypt
import psycopg2
import re

def process_add_admin(request):
    try:
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']
        role = 'admin'

        # Validasi input
        if not nama or not username or not password:
            flash("Semua bidang wajib diisi!", "danger")
            return redirect(url_for('add_adm.add_admin_controller'))

        if not re.match(r"^[\w.%+-]+@gmail\.com$", username):
            flash("Username harus berupa email dengan domain @gmail.com.", "danger")
            return redirect(url_for('add_adm.add_admin_controller'))

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$", password):
            flash("Password harus memiliki minimal 8 karakter, mengandung huruf besar, huruf kecil, angka, dan simbol.", "danger")
            return redirect(url_for('add_adm.add_admin_controller'))

        # Hash password
        hashed_password = sha256_crypt.hash(password)

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
        flash("Username sudah terdaftar.", "danger")
        conn.rollback()  # Batalkan perubahan jika terjadi error
        return redirect(url_for('add_adm.add_admin_controller'))
    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}", "danger")
        return redirect(url_for('add_adm.add_admin_controller'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return redirect(url_for('add_adm.add_admin_controller'))
