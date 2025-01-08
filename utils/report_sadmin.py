from flask import render_template
from database import get_db_connection
import logging

def report_super_admin():
    report_data = []  # Inisialisasi variabel untuk data laporan
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        cursor.execute("SELECT nama, id_karyawan, check_in, region_id FROM absensi")
        report_data = cursor.fetchall()
        
        if not report_data:
            logging.warning("No data found for attendance report for super admin.")
        
    except Exception as e:
        logging.error(f"Error fetching attendance report data for super admin: {e}")
        
    finally:
        cursor.close()  # Pastikan cursor ditutup
        db_conn.close()  # Pastikan koneksi ditutup

    return render_template('report_superadmin.html', report_data=report_data)