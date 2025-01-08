from flask import session, redirect, url_for

def logout():
    session.clear()  # Menghapus semua data sesi
    return redirect(url_for('log_in.login_view'))  # Mengarahkan kembali ke halaman login