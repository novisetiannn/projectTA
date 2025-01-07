from flask import Blueprint
from decorators.decorators import role_required
from utils.upd_region_sadmin import superadmin_regions

update_region_sadmin = Blueprint('update_region_sadmin', __name__)

@update_region_sadmin.route('/superadmin_regions', methods=['GET', 'POST'])
@role_required(['super_admin'])
def superadmin_regions():
    return superadmin_regions()