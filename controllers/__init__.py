# controllers/__init__.py

from flask import Blueprint

# Inisialisasi blueprint untuk controller
auth = Blueprint('auth', __name__)
dashboard = Blueprint('dashboard', __name__)

# Anda bisa menambahkan import untuk controller di sini jika diperlukan
from . import auth
from . import dashboard