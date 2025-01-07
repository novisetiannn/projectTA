from flask import Blueprint, render_template
from utils.login_signup import loginsignup

login_sign = Blueprint('login_sign', __name__)

@login_sign.route('/loginsignup')
def loginsignup():
    return render_template('login.html')