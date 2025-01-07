from flask import render_template
from database import get_db_connection
import logging

def report_admin():
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        cursor.execute("SELECT nama, id_karyawan, check_in, region_id FROM absensi")
        report_data = cursor.fetchall()
        
        cursor.close()
        db_conn.close()
        
        if not report_data:
            logging.warning("No data found for attendance report for admin.")
    except Exception as e:
        logging.error(f"Error fetching attendance report data for admin: {e}")
        report_data = []

    return render_template('report_admin.html', report_data=report_data)