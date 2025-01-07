from database import get_db_connection
import logging

def is_face_in_correct_region(roll, selected_region_id):
    """
    Memeriksa apakah karyawan dengan roll tertentu terdaftar di region yang sesuai.

    :param roll: ID karyawan (roll number)
    :param selected_region_id: ID region yang dipilih
    :return: True jika karyawan terdaftar di region, False sebaliknya
    """
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()

        # Query untuk memeriksa apakah karyawan terdaftar di region yang sesuai
        cursor.execute("""
            SELECT COUNT(*) 
            FROM employee 
            WHERE id_karyawan = %s AND region_id = %s
        """, (roll, selected_region_id))

        count = cursor.fetchone()[0]
        return count > 0  # Kembali True jika ada kecocokan, False jika tidak ada
    except Exception as e:
        logging.error(f"Error memeriksa kecocokan region: {e}")
        return False  # Kembali False jika terjadi kesalahan
    finally:
        cursor.close()  # Pastikan cursor ditutup
        db_conn.close()  # Pastikan koneksi ditutup
