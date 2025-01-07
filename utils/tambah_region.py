from flask import flash, request, redirect, url_for, render_template
from database import get_db_connection
import logging

def add_region():
    if request.method == 'POST':
        name = request.form['name']
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO region (name) VALUES (%s)", (name,))
            db_conn.commit()
            flash("Region berhasil ditambahkan!", "success")
        except Exception as e:
            logging.error(f"Error adding region: {e}")
            flash("Terjadi kesalahan saat menambahkan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()
        return redirect(url_for('admin_regions'))

    return render_template('add_region.html')