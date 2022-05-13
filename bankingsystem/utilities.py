from flask_login import current_user
from bankingsystem import bcrypt
from random import randint
from bankingsystem.models import User


def hash_user_password(password):
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    return hashed_pw


def set_password(password):
    hashed_pw = hash_user_password(password)
    current_user.password = hashed_pw
    return hashed_pw


def validate_password(user_password, entered_password):
    check_password_result = bcrypt.check_password_hash(user_password, entered_password)
    return check_password_result


def set_new_password(current_password, entered_password, new_password):
    if validate_password(current_password, entered_password):
        current_user.password = hash_user_password(new_password)
        return True
    return False


def set_account_number():
    n = 10
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    account_number = randint(range_start, range_end)
    return account_number


def check_for_username(username):
    user = User.query.filter_by(username=username).first();
    if user:
        return True
    else:
        return False


def check_for_email(email):
    user = User.query.filter_by(email=email).first();
    if user:
        return True
    else:
        return False
