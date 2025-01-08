from flask import flash, request, session, url_for, redirect, render_template
from database import get_db_connection
import logging

def update_employee_admin(id_karyawan):
    if request.method == 'POST':
        new_name = request.form['name']
        try:
            update_by = session.get('user_name')
            db_conn = get_db_connection()
            cursor = db_conn.cursor()

            cursor.execute("""
                UPDATE employee 
                SET name = %s, update_by = %s
                WHERE id_karyawan = %s AND status != 'Deleted'
            """, (new_name, update_by, id_karyawan))
            db_conn.commit()

        except Exception as e:
            logging.error(f"Error updating employee name: {e}")
            flash('An error occurred while updating the data.', 'error')
            return redirect(url_for('tampil_data_admin'))  # Redirect after error

        finally:
            cursor.close()
            db_conn.close()

        return redirect(url_for('tampil_data_admin'))

    employee_data = None
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT id_karyawan, name
            FROM employee 
            WHERE id_karyawan = %s AND status != 'Deleted'
        """, (id_karyawan,))
        employee_data = cursor.fetchone()

    except Exception as e:
        logging.error(f"Error fetching employee data for update: {e}")
        flash('An error occurred while fetching data for the update.', 'error')
        return redirect(url_for('tampil_data_admin'))

    finally:
        cursor.close()
        db_conn.close()

    if employee_data is None:
        flash('Data karyawan tidak ditemukan.', 'error')
        return redirect(url_for('tampil_data_admin'))

    return render_template('update_employee_admin.html', employee_data=employee_data)