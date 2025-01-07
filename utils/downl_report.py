from flask import request, render_template, send_file, app
from database import get_db_connection
import pdfkit
import tempfile
import pandas as pd


def download_report():
    format_type = request.args.get('format')
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("SELECT nama, id_karyawan, check_in, region_id FROM absensi")
        report_data = cursor.fetchall()
        cursor.close()
        db_conn.close()

        if not report_data:
            return "Tidak ada data untuk membuat laporan", 404

        if format_type == 'pdf':
            html_content = render_template('report_pdf.html', report_data=report_data)
            path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                pdfkit.from_string(html_content, temp_pdf.name, configuration=config)
                response = send_file(
                    temp_pdf.name,
                    as_attachment=True,
                    download_name='laporan_absensi.pdf'
                )

            return response  # File temp_pdf akan dihapus setelah request selesai

        elif format_type == 'excel':
            df = pd.DataFrame(report_data, columns=['Nama Karyawan', 'ID Karyawan', 'Waktu Check-in', 'Region'])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
                df.to_excel(temp_excel.name, index=False)
                response = send_file(
                    temp_excel.name,
                    as_attachment=True,
                    download_name='laporan_absensi.xlsx'
                )

            return response  # File temp_excel akan dihapus setelah request selesai

        else:
            return "Format tidak valid", 400

    except Exception as e:
        app.logger.error(f"Error generating report: {e}")
        return "Terjadi kesalahan saat membuat laporan", 500