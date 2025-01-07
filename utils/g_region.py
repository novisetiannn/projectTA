from database import get_db_connection

def get_regions():
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, name, allowed FROM region WHERE is_active = TRUE")
    regions = cursor.fetchall()
    cursor.close()
    db_conn.close()
    return regions
