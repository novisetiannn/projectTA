from flask import session, render_template, redirect
import logging
from database import get_db_connection

def index():
    if 'logged_in' in session:
        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM login")
            total_pengguna = cursor.fetchone()
            
            cursor.execute("SELECT * FROM login")
            users = cursor.fetchall()
            
            cursor.close()
            db_conn.close()
        except Exception as e:
            logging.error(f"Error fetching user data: {e}")
            total_pengguna = (0,)
            users = []

        return render_template('index.html', nama=session['nama'], username=session['username'], total_pengguna=total_pengguna, users=users)
    else:
        return redirect('/loginsignup')