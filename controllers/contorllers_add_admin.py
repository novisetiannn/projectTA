from flask import Blueprint, render_template
from decorators.decorators import role_required
from utils.add_admin_sadmin import add_admin

add_adm = Blueprint('add_adm', __name__)

@add_adm.route('/add_admin', methods=['GET', 'POST'])
@role_required(['super_admin'])
def add_admin():
    return render_template('add_admin.html')
