from flask import Blueprint
from decorators.decorators import role_required
from utils.region_admin import admin_regions as admin_regions_util

update_region_admin = Blueprint('update_region_admin', __name__)

@update_region_admin.route('/regions', methods=['GET', 'POST'])
@role_required(['admin'])
def admin_regions_view():
    return admin_regions_util()