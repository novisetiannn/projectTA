from flask import Blueprint, render_template, request, redirect, url_for, flash
from decorators.decorators import role_required
from utils.add_admin_sadmin import process_add_admin

add_adm = Blueprint('add_adm', __name__)

@add_adm.route('/add_admin', methods=['GET', 'POST'])
@role_required(['super_admin'])
def add_admin_controller():
    if request.method == 'POST':
        # Proses input dan validasi di utils
        return process_add_admin(request)
    return render_template('add_admin.html')
