from flask import Blueprint, render_template
from utils.login_signup import loginsignup as loginsignup_util

login_sign = Blueprint('login_sign', __name__)

@login_sign.route('/loginsignup')
def loginsignup_view():
    return loginsignup_util()