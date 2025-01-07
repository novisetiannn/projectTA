from flask import request, render_template
import logging
from database import get_db_connection

def fetch_absensi_data(template_name):
    absensi_data = []  # Inisialisasi data absensi
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        region = request.args.get('region')

        # Query untuk mengambil data absensi
        query = "SELECT nama, id_karyawan, check_in, photo, region_id FROM absensi WHERE 1=1"
        params = []

        # Tambahkan filter berdasarkan tanggal
        if start_date and end_date:
            query += " AND check_in BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        # Tambahkan filter berdasarkan region
        if region:
            query += " AND region_id = %s"
            params.append(region)

        cursor.execute(query, params)
        absensi_data = cursor.fetchall()

    except Exception as e:
        logging.error(f"Error fetching attendance data: {e}")
    finally:
        cursor.close()
        db_conn.close()

    # Menyediakan data ke template
    return render_template(template_name, data=absensi_data)