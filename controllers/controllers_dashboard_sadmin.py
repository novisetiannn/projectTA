from flask import Blueprint
from decorators.decorators import role_required
from utils.dashboard_sadmin import super_admin_dashboard

sadmin_dashboard = Blueprint('sadmin_dashboard', __name__)

@sadmin_dashboard.route('/super_admin_dashboard')
def super_admin_dashboard():
    return super_admin_dashboard()