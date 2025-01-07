from flask import session, redirect, url_for, render_template
from models.user import User
from models.employee import Employee

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