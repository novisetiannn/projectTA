from flask import flash, redirect, url_for
from database import get_db_connection
import logging

def deactivate_region_admin(id):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Tandai region sebagai tidak aktif
        cursor.execute("UPDATE region SET is_active = FALSE WHERE id = %s", (id,))
        db_conn.commit()
        flash("Region berhasil dinonaktifkan!", "success")
    except Exception as e:
        logging.error(f"Error deactivating region: {e}")
        flash("Terjadi kesalahan saat menonaktifkan region.", "danger")
    finally:
        cursor.close()
        db_conn.close()
    return redirect(url_for('admin_region'))