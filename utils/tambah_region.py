from flask import flash, redirect, url_for
from database import get_db_connection
import logging

def process_add_region(request):
    try:
        name = request.form.get('name')  # Ambil nilai dari form
        if not name:
            flash("Nama region wajib diisi!", "danger")
            return redirect(url_for('add_region_admin.add_region_controller'))

        # Simpan region ke database
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO region (name) VALUES (%s)", (name,))
        db_conn.commit()
        flash("Region berhasil ditambahkan!", "success")

    except Exception as e:
        logging.error(f"Error adding region: {e}")
        flash("Terjadi kesalahan saat menambahkan region.", "danger")
        return redirect(url_for('add_region_admin.add_region_controller'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db_conn' in locals():
            db_conn.close()

    return redirect(url_for('add_region_admin.add_region_controller'))
