from flask import Blueprint
from decorators.decorators import role_required
from utils.add_sadmin_region import add_superadmin_region

add_sadmin_region = Blueprint('add_sadmin_region', __name__)

@add_sadmin_region.route('/add_superadmin_region', methods=['GET', 'POST'])
@role_required(['super_admin'])
def add_superadmin_region():
    return add_superadmin_region()