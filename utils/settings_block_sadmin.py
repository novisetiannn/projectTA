from flask import flash, request, render_template
from database import get_db_connection

def blocking_settings():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_duration = request.form.get('blocking_duration')
        try:
            cursor.execute(
                "UPDATE global_settings SET setting_value = %s WHERE setting_key = 'blocking_duration_minutes'",
                (new_duration,)
            )
            conn.commit()
            print("Blocking duration updated successfully.")
            flash('Durasi blocking berhasil diperbarui.', 'success')
        except Exception as e:
            flash(f'Gagal memperbarui durasi blocking: {e}', 'error')

    cursor.execute("SELECT setting_value FROM global_settings WHERE setting_key = 'blocking_duration_minutes'")
    current_duration = cursor.fetchone()[0]
    conn.close()

    return render_template('blocking_settings.html', current_duration=current_duration)