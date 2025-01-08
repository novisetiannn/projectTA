from flask import request, render_template
from database import get_db_connection
import logging

def fetch_admin_data():
    search_query = request.args.get('search', '')  # Ambil kata kunci pencarian dari URL
    data_list = []

    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Query SQL untuk mencari karyawan berdasarkan nama dan memastikan status aktif
        if search_query:
            cursor.execute("""
                SELECT id_karyawan, name
                FROM employee 
                WHERE LOWER(name) LIKE LOWER(%s) AND status != 'N'
            """, ('%' + search_query + '%',))  # Menambahkan wildcard '%' di sekitar kata kunci
        else:
            cursor.execute("""
                SELECT id_karyawan, name
                FROM employee 
                WHERE status != 'N'
            """)

        data_list = cursor.fetchall()  # Ambil hasil query

    except Exception as e:
        logging.error(f"Error fetching employee data for admin: {e}")
        return None, str(e)

    finally:
        cursor.close()
        db_conn.close()

    return data_list, None
