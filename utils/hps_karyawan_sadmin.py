from database import get_db_connection
from flask import session, redirect, url_for
import logging

def hapus_karyawan(id_karyawan):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        # Ambil nama superadmin yang sedang login
        delete_by = session.get('user_name')  # Ganti dengan current_user.name jika menggunakan Flask-Login

        cursor.execute("""
            UPDATE employee 
            SET status = 'N', tgl_delete = CURRENT_TIMESTAMP, delete_by = %s 
            WHERE id_karyawan = %s
        """, (delete_by, id_karyawan))
        
        db_conn.commit()
        
        if cursor.rowcount == 0:
            return "Karyawan tidak ditemukan atau sudah dinonaktifkan.", 404  # Jika tidak ada baris yang terpengaruh

    except Exception as e:
        logging.error(f"Error deleting employee: {e}")
        db_conn.rollback()
        return "Terjadi kesalahan saat menghapus karyawan.", 500  # Tampilkan pesan error jika terjadi kesalahan

    finally:
        cursor.close()
        db_conn.close()

    return redirect(url_for('tampil_data_superadmin'))  # Arahkan ke halaman data karyawan superadmin