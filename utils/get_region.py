from database import get_db_connection
import logging

def get_region_allowed(region_id):
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("SELECT allowed FROM region WHERE id = %s", (region_id,))
        result = cursor.fetchone()
        return result[0] if result else False
    except Exception as e:
        logging.error(f"Error mendapatkan status allowed: {e}")
        return False
    finally:
        cursor.close()
        db_conn.close()