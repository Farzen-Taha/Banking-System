
from flask import redirect, flash, url_for
from wtforms.validators import ValidationError
from flask_login import current_user
from functools import wraps
from bankingsystem.models import User,Requests


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user and (current_user.user_type == "superadmin" or current_user.user_type == "systemuser"):
            return f(*args, **kwargs)
        flash("You need admin rights to access this page!", "info")
        return redirect(url_for('home'))
    return wrap


def is_customer(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user and current_user.user_type == "customer":
            return f(*args, **kwargs)
        flash("You need admin rights to access this page!", "info")
        return redirect(url_for('home'))
    return wrap

