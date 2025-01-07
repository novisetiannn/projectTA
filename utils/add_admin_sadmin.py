from flask import flash, request, redirect, url_for, render_template
import psycopg2
from database import get_db_connection
from passlib.hash import sha256_crypt
import re

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

        return redirect(url_for('add_adm.add_admin'))

    return render_template('add_admin.html')

