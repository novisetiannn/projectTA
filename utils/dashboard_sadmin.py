from flask import session, redirect, render_template, url_for
from database import get_db_connection

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