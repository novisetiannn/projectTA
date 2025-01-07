from flask import flash, session, request, redirect, render_template
from database import get_db_connection
from passlib.hash import sha256_crypt
import logging

def login():
    if request.method == 'POST':
        username = request.form['usr']
        password = request.form['pwd']

        try:
            db_conn = get_db_connection()
            cursor = db_conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result and sha256_crypt.verify(password, result[0]):
                # Login berhasil
                role = result[1]
                session['username'] = username
                session['role'] = role

                cursor.close()
                db_conn.close()

                # Redirect berdasarkan role
                if role == 'admin':
                    return redirect('/admin_dashboard')
                elif role == 'super_admin':
                    return redirect('/super_admin_dashboard')
            else:
                cursor.close()
                db_conn.close()
                flash("Invalid username or password.", "danger")
                return render_template('login.html', error_message='Invalid username or password')
        except Exception as e:
            logging.error(f"Database connection error during login: {e}")
            return render_template('login.html', error_message='Database connection error')

    return render_template('login.html')