from flask import flash, request, render_template
from database import get_db_connection

def blocking_settings():
    conn = get_db_connection()
    cursor = conn.cursor()

    current_duration = None  # Inisialisasi variabel untuk durasi saat ini

    if request.method == 'POST':
        new_duration = request.form.get('blocking_duration')
        try:
            cursor.execute(
                "UPDATE global_settings SET setting_value = %s WHERE setting_key = 'blocking_duration_minutes'",
                (new_duration,)
            )
            conn.commit()
            flash('Durasi blocking berhasil diperbarui.', 'success')
        except Exception as e:
            flash(f'Gagal memperbarui durasi blocking: {e}', 'error')

    try:
        cursor.execute("SELECT setting_value FROM global_settings WHERE setting_key = 'blocking_duration_minutes'")
        current_duration = cursor.fetchone()[0]
    except Exception as e:
        flash(f'Gagal mengambil durasi saat ini: {e}', 'error')

    finally:
        cursor.close()  # Pastikan cursor ditutup
        conn.close()  # Pastikan koneksi ditutup

    return render_template('blocking_settings.html', current_duration=current_duration)