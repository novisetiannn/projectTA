from flask import Blueprint, render_template, request, redirect, url_for, flash
from decorators.decorators import role_required
from utils.tambah_region import process_add_region

add_region_admin_bp = Blueprint('add_region_admin', __name__)

@add_region_admin_bp.route('/add_region', methods=['GET', 'POST'])
@role_required(['admin'])
def add_region_controller():
    if request.method == 'POST':
        # Panggil fungsi utils untuk memproses input
        return process_add_region(request)
    return render_template('add_region.html')
