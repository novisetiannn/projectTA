from flask import Blueprint
from decorators.decorators import role_required
from utils.dashboard_admin import admin_dashboard

dashboardadmin = Blueprint('dashboardadmin', __name__)

@dashboardadmin.route('/admin_dashboard')
def admin_dashboard():
    return admin_dashboard()