from fileinput import filename
from sqlalchemy import delete
from bankingsystem.models import SuperAdmin, SystemUser, Customer, Requests, TransactionLog
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from random import randint
from bankingsystem.form import (
    RegistrationForm,
    LoginForm,
    DepositForm,
    TransferForm,
    WithdrawForm,
    WithdrawForm,
    UpdatAccountForm,

)
from bankingsystem.utilities import set_password, validate_password, set_new_password, hash_user_password, \
    set_account_number
from bankingsystem import app, db, bcrypt
import secrets
import os
from PIL import Image


def user_register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = hash_user_password(form.password.data)
        if form.account_type.data == "SA":
            super_admin = SuperAdmin.query.first()
            # if there is not a super admin create one
            if super_admin is None:
                super_admin = SuperAdmin(username=form.username.data, email=form.email.data, password=hashed_pw)
                db.create_all()
                db.session.add(super_admin)
                db.session.commit()
                flash("Your account has been created. You can log in now!", "success")
                return redirect(url_for("login"))
            # else send a reques to the existing super admin
            else:
                request = Requests(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw,
                    user_type="systemuser",
                )
                flash("There is already a Super Admin account. Please wait so that your account be verified.",
                      "warning")
                db.create_all()
                db.session.add(request)
                db.session.commit()

        elif form.account_type.data == "SU":
            account_request = Requests(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw,
                user_type="systemuser",
            )
            db.create_all()
            db.session.add(account_request)
            db.session.commit()
            flash("Your data saved. Please wait so that your account be verified.", "info")
            return redirect(url_for("login"))
        elif form.account_type.data == "CU":
            account_number = set_account_number()
            account_request = Requests(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw,
                account_number=account_number,
                user_type="customer",
            )
            db.create_all()
            # db.session.add(customer)
            db.session.add(account_request)
            db.session.commit()
            flash("Your account was created. Wait for admin's approval!", "info")
            return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


def user_login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        sa = SuperAdmin.query.filter_by(email=form.email.data).first()
        su = SystemUser.query.filter_by(email=form.email.data).first()
        cu = Customer.query.filter_by(email=form.email.data).first()

        if sa and validate_password(sa.password, form.password.data):
            login_user(sa, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("admin.index"))

        elif su and validate_password(su.password, form.password.data):
            login_user(su, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("admin.index"))
        elif cu and validate_password(cu.password, form.password.data):
            login_user(cu, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("users"))
        else:
            flash("Login unsuccessful, incorrect email or password", "danger")
    return render_template("login.html", title="Login", form=form)


def log_transaction(sender_id, receiver_id, amount, type):
    log = TransactionLog(sender_id=sender_id, receiver_id=receiver_id, fund_amount=amount, transaction_type=type)
    db.session.add(log)
    db.session.commit()


def show_fund():
    fund = Customer.query.filter_by(id=current_user.id).first()
    return fund.balance


def deposit_fund():
    form = DepositForm()
    if request.method == "POST":

        if validate_password(current_user.password, form.password.data) and form.amount.data > 0:
            user = Customer.query.filter_by(id=current_user.id).first()
            user.balance = user.balance + int(form.amount.data)
            log_transaction(current_user.id, current_user.id, form.amount.data, "deposit")
            db.session.commit()
            flash("Deposit was successful!", "info")
        else:
            flash("Wrong password or Amount!", "danger")
    return render_template("deposit.html", title="Deposit", form=form, fund=show_fund())


def withdraw_fund():
    form = WithdrawForm()
    if request.method == "POST":
        if validate_password(current_user.password, form.password.data) and form.amount.data > 0:
            user = Customer.query.filter_by(id=current_user.id).first()
            if current_user.balance >= form.amount.data:
                user.balance -= int(form.amount.data)
                log_transaction(current_user.id, current_user.id, form.amount.data, "withdraw")
                db.session.commit()
                flash("Withdrawl was successful!", "info")
            else:
                flash("Insufficient Funds to withdraw", "warning")
        else:
            flash("Wrong password or Amount!", "danger")
    return render_template("withdraw.html", title="Withdraw", form=form, fund=show_fund())


def transfer_fund():
    form = TransferForm()
    if request.method == "POST":
        if validate_password(current_user.password, form.password.data) and form.amount.data > 0:
            sender_customer = Customer.query.filter_by(id=current_user.id).first()
            receiver_customer = Customer.query.filter_by(account_number=form.account_number.data).first()
            if (current_user.balance >= form.amount.data) and (current_user.account_number != form.account_number.data):
                sender_customer.balance -= int(form.amount.data)
                receiver_customer.balance += int(form.amount.data)
                log_transaction(current_user.id, receiver_customer.id, form.amount.data, "transfer")
                db.session.commit()
                flash("Transfer was successful!", "info")
                return redirect(url_for("transfer"))
            else:
                flash("Insufficient Funds to transfer or Invalid account number!", "warning")
        else:
            flash("Wrong password or Amount!", "danger")
    return render_template("transfer.html", title="Transfer", form=form, fund=show_fund())


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pic", picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


def update_account():
    form = UpdatAccountForm()
    if form.validate_on_submit():
        if validate_password(current_user.password, form.current_password.data):
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            update_password_result = False
            if form.new_password.data:
                update_password_result = set_new_password(current_user.password, form.current_password.data,
                                                          form.new_password.data)
            if update_password_result:
                flash("Your account has updated succesfully and password changed!", "success")
            else:
                flash("Your profile updated successfuly!", "success")
            db.session.commit()
        else:
            flash("Invalid password", "danger")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pic/" + current_user.image_file)
    return render_template("account.html", title="Account", form=form, image_file=image_file)


def get_all_account_requests():
    requests = Requests.query.all()
    return render_template("admin/account_request.html", title="Request", requests=requests)


def accept_request(id):
    request = Requests.query.filter_by(id=id).first()
    user = None
    if request.user_type == "customer":
        user = Customer(username=request.username, email=request.email, password=request.password,
                        account_number=request.account_number)
    elif request.user_type == "systemuser":
        user = SystemUser(username=request.username, email=request.email, password=request.password)
    db.session.add(user)
    db.session.delete(request)
    db.session.commit()
    flash("Account Approved!", "info")
    return redirect(url_for("account_request"))


def reject_request():
    request = Requests.query.filter_by(id=id).first()
    db.session.delete(request)
    db.session.commit()
    flash("Account Rejected!", "warning")
    return redirect(url_for("account_request"))


def transactionshisory():
    transactions = TransactionLog.query.all()
    return render_template("admin/transactionslog.html", title="transactions history", transactions=transactions)
