from flask import Blueprint
from decorators.decorators import role_required
from utils.dashboard_admin import render_admin_dashboard

dashboardadmin = Blueprint('dashboardadmin', __name__)

@dashboardadmin.route('/admin_dashboard')
@role_required('admin')  # Middleware untuk memeriksa apakah pengguna memiliki akses admin
def admin_dashboard():
    return render_admin_dashboard()
