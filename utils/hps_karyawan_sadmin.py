from database import get_db_connection
from flask import session, redirect, url_for
import logging

def hapus_karyawan(id_karyawan):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()

    try:
        # Ambil nama superadmin yang sedang login
        delete_by = session.get('user_name')  # Jika menggunakan Flask-Login, bisa ganti dengan current_user.name

        cursor.execute("""
            UPDATE employee 
            SET status = 'N', tgl_delete = CURRENT_TIMESTAMP, delete_by = %s 
            WHERE id_karyawan = %s
        """, (delete_by, id_karyawan))
        db_conn.commit()
    except Exception as e:
        logging.error(f"Error deleting employee: {e}")
        db_conn.rollback()

    finally:
        cursor.close()
        db_conn.close()

    return redirect(url_for('tampil_data_superadmin'))