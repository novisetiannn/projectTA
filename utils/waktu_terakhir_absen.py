from database import get_db_connection

def get_last_absence_time(employee_id, region_id):
    """ Fungsi untuk mengambil waktu absensi terakhir dari database berdasarkan karyawan dan region """
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT check_in FROM absensi WHERE id_karyawan = %s AND region_id = %s ORDER BY check_in DESC LIMIT 1", 
        (employee_id, region_id)
    )
    result = cursor.fetchone()
    cursor.close()
    db_conn.close()
    
    if result:
        return result[0]
    return None