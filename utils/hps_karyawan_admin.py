from flask import session, redirect, url_for
from database import get_db_connection
import logging

def hapus_karyawan_admin(id_karyawan):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Ambil nama admin yang sedang login
        delete_by = session.get('user_name')  # Ganti dengan current_user.name jika menggunakan Flask-Login

        # Update status menjadi 'N' untuk menandakan data tidak aktif dan catat siapa yang menghapus
        cursor.execute("""
            UPDATE employee 
            SET status = 'N', delete_by = %s
            WHERE id_karyawan = %s AND status != 'N'
        """, (delete_by, id_karyawan))
        
        db_conn.commit()  # Pastikan perubahan disimpan ke database

        if cursor.rowcount == 0:
            return "Karyawan tidak ditemukan atau sudah dinonaktifkan.", 404  # Jika tidak ada baris yang terpengaruh

    except Exception as e:
        db_conn.rollback()  # Jika terjadi error, batalkan perubahan
        logging.error(f"Error deleting employee: {e}")
        return "Terjadi kesalahan saat menghapus karyawan.", 500  # Tampilkan pesan error jika terjadi kesalahan

    finally:
        cursor.close()  # Menutup cursor
        db_conn.close()  # Menutup koneksi ke database

    return redirect(url_for('tampil_data_admin'))  # Arahkan ke halaman data karyawan admin