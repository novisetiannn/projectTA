from flask import Flask
from models import db
from utils.encoding_wajah_dikenal import load_known_faces
from controllers.contorllers_add_admin import add_adm
from controllers.controllers_add_region_admin import add_region_admin
from controllers.controllers_add_region_sadmin import add_sadmin_region
from controllers.controllers_attendance import absen_attendance
from controllers.controllers_dashboard_admin import dashboardadmin
from controllers.controllers_dashboard_sadmin import sadmin_dashboard
from controllers.controllers_deactivate_region_admin import deact_region_admin
from controllers.controllers_deactivate_region_sadmin import deact_region_sadmin
from controllers.controllers_download_report import downl_report
from controllers.controllers_hps_karyawan_admin import hps_karyawan_admin
from controllers.controllers_hps_karyawan_sadmin import hps_karyawan_sadmin
from controllers.controllers_index import indexx
from controllers.controllers_login import log_in
from controllers.controllers_loginsignup import login_sign
from controllers.controllers_logout import log_out
from controllers.controllers_report_admin import report_adm
from controllers.controllers_report_sadmin import report_sadmin
from controllers.controllers_sett_blocking_sadmin import sett_blocking
from controllers.controllers_tampil_data_admin import tampil_data_adm
from controllers.controllers_tampil_data_sadmin import tampil_data_sadmin
from controllers.controllers_tb_admin import tb_admin
from controllers.controllers_tb_sadmin import tb_sadmin
from controllers.controllers_upd_employee_admin import upd_employee_admin
from controllers.controllers_upd_employee_sadmin import update_employee_sadmin
from controllers.controllers_update_region_admin import update_region_admin
from controllers.controllers_update_region_sadmin import update_region_sadmin
from controllers.controllers_upload_admin import upd_admin
from controllers.controllers_upload_sadmin import upd_sadmin
from controllers.controllers_video import videoAttendance

#ini nanti di app.py
app = Flask(__name__)
# Atur ukuran maksimal (contoh: 50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2655@localhost:5432/attendancedbb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
app.register_blueprint(add_adm)
app.register_blueprint(add_region_admin)
app.register_blueprint(add_sadmin_region)
app.register_blueprint(absen_attendance)
app.register_blueprint(dashboardadmin)
app.register_blueprint(sadmin_dashboard)
app.register_blueprint(deact_region_admin)
app.register_blueprint(deact_region_sadmin)
app.register_blueprint(downl_report)
app.register_blueprint(hps_karyawan_admin)
app.register_blueprint(hps_karyawan_sadmin)
app.register_blueprint(indexx)
app.register_blueprint(log_in)
app.register_blueprint(login_sign)
app.register_blueprint(log_out)
app.register_blueprint(report_adm)
app.register_blueprint(report_sadmin)
app.register_blueprint(sett_blocking)
app.register_blueprint(tampil_data_adm)
app.register_blueprint(tampil_data_sadmin)
app.register_blueprint(tb_admin)
app.register_blueprint(tb_sadmin)
app.register_blueprint(upd_employee_admin)
app.register_blueprint(update_employee_sadmin)
app.register_blueprint(update_region_admin)
app.register_blueprint(update_region_sadmin)
app.register_blueprint(upd_admin)
app.register_blueprint(upd_sadmin)
app.register_blueprint(videoAttendance)

if __name__ == "__main__":
    load_known_faces()
    app.run(host='127.0.0.1', port=5000, debug=True)