from flask import Blueprint, request, render_template
from decorators.decorators import role_required
from utils.add_sadmin_region import process_add_superadmin_region

add_sadmin_region_bp = Blueprint('add_sadmin_region', __name__)

@add_sadmin_region_bp.route('/add_superadmin_region', methods=['GET', 'POST'])
@role_required(['super_admin'])
def add_region_controller():
    if request.method == 'POST':
        # Panggil fungsi utils untuk memproses input
        return process_add_superadmin_region(request)
    return render_template('add_superadmin_region.html')
