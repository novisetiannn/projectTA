from flask import Blueprint
from decorators.decorators import role_required
from utils.deact_reg_admin import deactivate_region_admin as deactivate_region_admin_util

deact_region_admin = Blueprint('deact_region_admin', __name__)

@deact_region_admin.route('/deactivate_region_admin/<int:id>', methods=['POST'])
@role_required(['admin'])
def deactivate_region_admin_view(id):
    return deactivate_region_admin_util(id)