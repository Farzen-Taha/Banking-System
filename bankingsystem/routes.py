from fileinput import filename
from bankingsystem.models import SuperAdmin, SystemUser, Customer
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from functools import wraps
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
from bankingsystem import app, db, bcrypt
import secrets
import os
from PIL import Image

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


@app.route("/transactions")
@login_required
def transactions():
    return render_template("transactions.html", title="Transactions")


@app.route("/users")
def users():
    return render_template("users.html", title="users")


@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("transactions"))
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        if form.account_type.data == "SA":
            super_admin = SuperAdmin.query.first()
            # if there is not a super admin create one
            if super_admin is None:
                super_admin = SuperAdmin(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw,
                )
                db.create_all()
                db.session.add(super_admin)
                db.session.commit()
                flash("Your account has been created. You can log in now!", "success")
                return redirect(url_for("login"))
            # else send a reques to the existing super admin
            else:
                flash(
                    "There is already a Super Admin account. Please wait so that your account be verified.",
                    "warning",
                )
        elif form.account_type.data == "SU":
            system_user = SystemUser(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw,
            )
            db.create_all()

            db.session.add(system_user)
            db.session.commit()
            flash(
                "Your data saved. Please wait so that your account be verified.", "info"
            )
            return redirect(url_for("login"))
        elif form.account_type.data == "CU":
            n = 10
            range_start = 10**(n -1)
            range_end = (10**n )-1
            account_number= randint(range_start, range_end)
            customer = Customer(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw,
                account_number=account_number
            )

            db.create_all()
            db.session.add(customer)
            db.session.commit()
            flash(
                "Your account was created. Wait for admin's approval!", "info"
            )
            return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        SA = SuperAdmin.query.filter_by(email=form.email.data).first()
        SU = SystemUser.query.filter_by(email=form.email.data).first()
        CU = Customer.query.filter_by(email=form.email.data).first()

        if SA and bcrypt.check_password_hash(SA.password, form.password.data):
            login_user(SA, remember=form.remember.data)
            next_page = request.args.get("next")
            return (
                redirect(next_page) if next_page else redirect(url_for("admin.index"))
            )
        elif SU and bcrypt.check_password_hash(SU.password, form.password.data):
            login_user(SU, remember=form.remember.data)
            next_page = request.args.get("next")
            return (
                redirect(next_page) if next_page else redirect(url_for("admin.index"))
            )
        elif CU and bcrypt.check_password_hash(CU.password, form.password.data):
            login_user(CU, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("users"))
        else:
            flash("Login unsuccessful, incorrect email or password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/deposit",methods=["POST", "GET"],)
@login_required
def deposit():
    form = DepositForm()
    if request.method=="POST":
        if bcrypt.check_password_hash(current_user.password, form.password.data) and form.amount.data>0:
            user=Customer.query.filter_by(id=current_user.id).first()
            user.balance=user.balance+int(form.amount.data)
            db.session.commit()
            flash('Deposit was successful!','info')
        else:
            flash('Wrong password or Amount!','danger')
    return render_template("deposit.html", title="Deposit", form=form)


@app.route("/withdraw",methods=["POST", "GET"])
@login_required
def withdraw():
    form = WithdrawForm()
    if request.method=="POST":
            if bcrypt.check_password_hash(current_user.password, form.password.data) and form.amount.data>0:
                user=Customer.query.filter_by(id=current_user.id).first()
                if current_user.balance>=form.amount.data:
                    user.balance-=int(form.amount.data)
                    db.session.commit()
                    flash('Withdrawl was successful!','info')
                else:
                    flash('Insufficient Funds to withdraw','warning')
            else:
                flash('Wrong password or Amount!','danger')
    return render_template("withdraw.html", title="Withdraw", form=form)


@app.route("/transfer",methods=["POST", "GET"])
@login_required
def transfer():
    form = TransferForm()
    if request.method=="POST":
            if bcrypt.check_password_hash(current_user.password, form.password.data) and form.amount.data>0:
                sender_customer=Customer.query.filter_by(id=current_user.id).first()
                
                receiver_customer=Customer.query.filter_by(account_number=form.account_number.data).first()
                if current_user.balance>=form.amount.data:
                    sender_customer.balance-=int(form.amount.data)
                    receiver_customer.balance+=int (form.amount.data)
                    db.session.commit()
                    flash('Transfer was successful!','info')
                    return redirect(url_for('transfer'))
                else:
                    flash('Insufficient Funds to transfer!','warning')
            else:
                flash('Wrong password or Amount!','danger')
    return render_template("transfer.html", title="Transfer", form=form)


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


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():

    form = UpdatAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has updated succesfully!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pic/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", form=form, image_file=image_file
    )
