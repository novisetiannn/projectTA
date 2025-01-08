from flask import Blueprint
from decorators.decorators import role_required
from utils.deact_reg_sadmin import deactivate_region_superadmin as deactivate_region_superadmin_util

deact_region_sadmin = Blueprint('deact_region_sadmin', __name__)

@deact_region_sadmin.route('/deactivate_region_superadmin/<int:id>', methods=['POST'])
@role_required(['super_admin'])
def deactivate_region_superadmin_view(id):
    return deactivate_region_superadmin_util(id)