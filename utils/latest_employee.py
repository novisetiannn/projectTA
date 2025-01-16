from database import get_db_connection
import logging

def get_latest_employee_name(roll):
    if not isinstance(roll, int):
        return None  # Pastikan roll adalah integer
    
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT name FROM employee WHERE id_karyawan = %s", (roll,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"Error saat mengambil nama karyawan: {e}")
        return None
    finally:
        cursor.close()
        db_conn.close()
