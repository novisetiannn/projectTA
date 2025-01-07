from database import get_db_connection

def get_latest_employee_name(roll):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM employee WHERE id_karyawan = %s", (roll,))
    result = cursor.fetchone()
    cursor.close()
    db_conn.close()
    
    return result[0] if result else None