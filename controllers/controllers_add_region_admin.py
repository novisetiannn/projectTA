from flask import Blueprint, render_template
from decorators.decorators import role_required
from utils.tambah_region import add_region

add_region_admin = Blueprint('add_region_admin', __name__)

@add_region_admin.route('/add_region', methods=['GET', 'POST'])
@role_required(['admin'])
def add_region():
    return render_template('add_region.html')

