import psycopg2
import logging

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",        # Host
            user="postgres",         # Username
            password="2655",               # Password
            dbname="attendancedbb"         # Nama database
        )
        logging.info("Koneksi ke database berhasil")
        return connection
    except psycopg2.Error as err:
        logging.error(f"Error connecting to database: {err}")
        return None