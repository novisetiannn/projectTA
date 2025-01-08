from flask import request, render_template
from database import get_db_connection
import logging

def tampil_data_superadmin():
    data_list = []
    query = request.args.get('query', '')  # Ambil parameter pencarian
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Query dengan filter pencarian yang tidak case sensitive
        if query:
            cursor.execute("""
                SELECT * 
                FROM employee 
                WHERE LOWER(name) LIKE LOWER(%s) 
                ORDER BY tgl_create DESC
            """, (f"%{query}%",))
        else:
            cursor.execute("SELECT * FROM employee ORDER BY tgl_create DESC")
        
        data_list = cursor.fetchall()
        
    except Exception as e:
        logging.error(f"Error fetching employee data for superadmin: {e}")
        
    finally:
        cursor.close()  # Pastikan cursor ditutup
        db_conn.close()  # Pastikan koneksi ditutup

    return render_template('tampil_data_superadmin.html', data_list=data_list)