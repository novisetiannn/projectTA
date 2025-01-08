from flask import Blueprint
from decorators.decorators import role_required
from utils.dashboard_sadmin import render_super_admin_dashboard

sadmin_dashboard = Blueprint('sadmin_dashboard', __name__)

@sadmin_dashboard.route('/super_admin_dashboard')
@role_required('super_admin')  # Mengasumsikan dekorator memeriksa peran
def super_admin_dashboard_view():
    return render_super_admin_dashboard()