from flask import flash, request, session, redirect, render_template, url_for
from database import get_db_connection
import logging

def update_employee_superadmin(id_karyawan):
    global current_employee_name_superadmin  # Deklarasi variabel global

    if request.method == 'POST':
        nama = request.form['nama']
        region_id = request.form['region_id']
        
        try:
            update_by = session.get('user_name')
            db_conn = get_db_connection()
            cursor = db_conn.cursor()

            cursor.execute("""
                UPDATE employee 
                SET name = %s, region_id = %s, tgl_update = CURRENT_TIMESTAMP, update_by = %s
                WHERE id_karyawan = %s
            """, (nama, region_id, update_by, id_karyawan))
            db_conn.commit()

            current_employee_name_superadmin = nama  # Perbarui nama
            return redirect(url_for('tampil_data_superadmin'))
        except Exception as e:
            logging.error(f"Error updating employee data: {e}")
            db_conn.rollback()
            flash("Terjadi kesalahan saat memperbarui data karyawan.", "danger")
        finally:
            cursor.close()
            db_conn.close()

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee WHERE id_karyawan = %s", (id_karyawan,))
    karyawan = cursor.fetchone()

    cursor.close()
    db_conn.close()

    return render_template('update_employee_superadmin.html', karyawan=karyawan)