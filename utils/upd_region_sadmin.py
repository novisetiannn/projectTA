from flask import flash, request, render_template
from database import get_db_connection
import logging
from utils.g_region import get_regions

def superadmin_regions():
    if request.method == 'POST':
        allowed_ids = request.form.getlist('allowed_region')
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("UPDATE region SET allowed = FALSE")
            if allowed_ids:
                cursor.execute("UPDATE region SET allowed = TRUE WHERE id IN %s", (tuple(allowed_ids),))
            db_conn.commit()
            flash("Pengaturan region berhasil diperbarui!", "success")
        except Exception as e:
            logging.error(f"Error updating allowed regions: {e}")
            flash("Terjadi kesalahan saat memperbarui pengaturan region.", "danger")
        finally:
            cursor.close()
            db_conn.close()

    regions = get_regions()
    return render_template('superadmin_regions.html', regions=regions)