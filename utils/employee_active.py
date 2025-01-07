from database import get_db_connection
import logging

def is_employee_active(roll):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT status FROM employee WHERE id_karyawan = %s", (roll,))
        status = cursor.fetchone()
        return status is not None and status[0] == 'A'
    except Exception as e:
        logging.error(f"Error checking employee status: {e}")
        return False
    finally:
        cursor.close()
        db_conn.close()    