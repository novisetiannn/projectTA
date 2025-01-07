from flask import flash, request, redirect, render_template, url_for
from database import get_db_connection
import logging

def add_superadmin_region():
    if request.method == 'POST':
        name = request.form['name']
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO region (name) VALUES (%s)", (name,))
            db_conn.commit()
            flash("Region berhasil ditambahkan!", "success")
        except Exception as e:
            logging.error(f"Error adding superadmin region: {e}")
            flash("Terjadi kesalahan saat menambahkan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()
        return redirect(url_for('superadmin_regions'))

    return render_template('add_superadmin_region.html')