from flask import session, redirect, url_for, render_template
from models.user import User
from models.employee import Employee
from sqlalchemy.exc import SQLAlchemyError

def render_admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))  # Pastikan nama blueprint login sesuai
    
    try:
        # Menghitung total pengguna dari tabel users
        total_pengguna = User.query.count()
        total_karyawan = Employee.query.count()
        users = Employee.query.all()  # Ambil semua data karyawan
        
        # Validasi data jika kosong
        if not total_pengguna or not total_karyawan:
            message = "Data pengguna atau karyawan kosong."
            return render_template('admin_dashboard.html', username=session['username'], 
                                   total_pengguna=0, total_karyawan=0, users=[], message=message)

        return render_template('admin_dashboard.html', 
                               username=session['username'], 
                               total_pengguna=total_pengguna, 
                               total_karyawan=total_karyawan, 
                               users=users)
    except SQLAlchemyError as e:
        error_message = f"Terjadi kesalahan saat mengakses database: {e}"
        return render_template('admin_dashboard.html', username=session['username'], 
                               total_pengguna=0, total_karyawan=0, users=[], error_message=error_message)
