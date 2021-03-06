from datetime import datetime
from bankingsystem.models import SuperAdmin, SystemUser, Customer, Requests, TransactionLog, User
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, current_user
from sqlalchemy import or_
from bankingsystem.form import (
    RegistrationForm,
    LoginForm,
    DepositForm,
    TransferForm,
    WithdrawForm,
    UpdatAccountForm,
    UpdatePassword
)
from bankingsystem.utilities import validate_password, set_new_password, hash_user_password, set_account_number
from bankingsystem import app, db
import secrets
import os
from PIL import Image


def user_register():
    """
        This function registers users based on the following criteria:
        * if the user has chosen super admin from dropdown menu, this function creates an object of the SuperAdmin class and
        stores it in database.
        * if the user has chosen super system user from dropdown menu, this function creates an object of the System USer
        class and stores it in database.
        * if the user has chosen customer from dropdown menu, this function creates an object of the Customer class and
        stores it in database.
    :return:
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = hash_user_password(form.password.data)
        # if form.account_type.data == "SA":
        #     super_admin = SuperAdmin.query.first()
        #     # if there is not a super admin create one
        #     if super_admin is None:
        #         super_admin = SuperAdmin(username=form.username.data, email=form.email.data, password=hashed_pw,state="active")
        #         db.create_all()
        #         db.session.add(super_admin)
        #         db.session.commit()
        #         flash("Your account has been created. You can log in now!", "success")
        #         return redirect(url_for("login"))
        #     # else send a reques to the existing super admin
        #     else:
        #         request = Requests(
        #             username=form.username.data,
        #             email=form.email.data,
        #             password=hashed_pw,
        #             user_type="systemuser",
        #         )
        #         flash("There is already a Super Admin account. Please wait so that your account be verified.",
        #               "warning")
        #         db.create_all()
        #         db.session.add(request)
        #         db.session.commit()

        if form.account_type.data == "SU":
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
    """
    This function is used to login users to their accounts in the following way:
    * if the user was loged in and wants to login agen, the user will be redirected to th home page.
    * if the user was not loged in, the system will look for the user in the database.
        if found and their password matched the user will be redirected to users home page. otherwise the user will be
        shown in a flash message.
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        # sa = SuperAdmin.query.filter_by(email=form.email.data).first()
        # su = SystemUser.query.filter_by(email=form.email.data).first()
        # cu = Customer.query.filter_by(email=form.email.data).first()
        user = User.query.filter_by(email=form.email.data).first()
        user_request = Requests.query.filter_by(email=form.email.data).first()
        # if sa and validate_password(sa.password, form.password.data):
        #     if sa.state == "active":
        #         login_user(sa, remember=form.remember.data)
        #         next_page = request.args.get("next")
        #         return redirect(next_page) if next_page else redirect(url_for("admin.index"))
        #     else:
        #         flash("Your account is not active.Please contact super admin to activate your account!", "warning")
        if user_request:
            flash("Your account is not active.Please contact super admin to activate your account!", "warning")
        elif user and (user.user_type == "superadmin" or user.user_type == "systemuser") and validate_password(
                user.password, form.password.data):
            if user.state == "active":
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("admin.index"))
            else:
                flash("Your account is not active.Please contact super admin to activate your account!", "warning")
        # elif su and validate_password(su.password, form.password.data):
        #     if su.state == "active":
        #         login_user(su, remember=form.remember.data)
        #         next_page = request.args.get("next")
        #         return redirect(next_page) if next_page else redirect(url_for("admin.index"))
        #     else:
        #         flash("Your account is not active.Please contact super admin to activate your account!", "warning")
        # elif cu and validate_password(cu.password, form.password.data):
        #     if cu.state == "active":
        #         login_user(cu, remember=form.remember.data)
        #         next_page = request.args.get("next")
        #         return redirect(next_page) if next_page else redirect(url_for("users"))
        #     else:
        #         flash("Your account is not active.Please contact admin to activate your account!", "warning")

        elif user and (user.user_type == "customer") and validate_password(
                user.password, form.password.data):
            if user.state == "active":
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Your account is not active.Please contact super admin to activate your account!", "warning")
        else:
            flash("Login unsuccessful, incorrect email or password", "danger")
    return render_template("login.html", title="Login", form=form)


def log_transaction(sender_id, receiver_id, amount, type,date):
    """
     This function saves the customers' transaction history.
    :param sender_id: id of the customer who wants to send fund.
    :param receiver_id: id of the customer who wants to receive the fund.
    :param amount: the amount of the fund to be transferred
    :param type: type of the transaction.
    :return:
    """
    log = TransactionLog(sender_id=sender_id, receiver_id=receiver_id, fund_amount=amount, transaction_type=type,date=date)
    db.session.add(log)
    db.session.commit()


def show_fund():
    """
    * this function shows users balance amount to user based on users id.
    :return:
    """
    fund = Customer.query.filter_by(id=current_user.id).first()
    return fund.balance


def deposit_fund():
    """
    * This function adds some amount of fund to users balance.
    * It also stores the log of the transaction.
    :return:
    """
    form = DepositForm()
    if request.method == "POST":

        if validate_password(current_user.password, form.password.data) and form.amount.data > 0:
            user = Customer.query.filter_by(id=current_user.id).first()
            user.balance = user.balance + int(form.amount.data)
            tran_date = datetime.now().strftime("%b-%d-%Y %H:%M:%S %p")
            log_transaction(current_user.id, current_user.id, form.amount.data, "deposit",tran_date)
            db.session.commit()
            flash("Deposit was successful!", "info")
        else:
            flash("Wrong password or Amount!", "danger")
    return render_template("deposit.html", title="Deposit", form=form, fund=show_fund())


def withdraw_fund():
    """
    * This function withdraw some amount of fund from user's account and decrease it in the database.
    * It also stores the log of the transaction.
    :return:
    """
    form = WithdrawForm()
    if request.method == "POST":
        if validate_password(current_user.password, form.password.data):
            if form.amount.data >= 500:

                user = Customer.query.filter_by(id=current_user.id).first()
                if current_user.balance >= form.amount.data and (
                        current_user.balance - form.amount.data) >= 500:
                    user.balance -= int(form.amount.data)
                    tran_date = datetime.now().strftime("%b-%d-%Y %H:%M:%S %p")
                    log_transaction(current_user.id, current_user.id, form.amount.data, "withdraw",tran_date)
                    db.session.commit()
                    flash("Withdrawal was successful!", "info")
                else:
                    flash("Insufficient Funds to withdraw. The remaining balance should be greater than 500AFs!",
                          "warning")
            else:
                flash("Insufficient Funds to withdraw. The remaining balance should be more or equal to 500AFs!",
                      "warning")

        else:
            flash("Wrong password!", "danger")

    return render_template("withdraw.html", title="Withdraw", form=form, fund=show_fund())


def transfer_fund():
    """
    * This function transfer some amount of fund from one customer to the other customer based on their account numbers.
    * It also stores the log of the transaction.
    :return:
    """
    form = TransferForm()
    if request.method == "POST":
        if validate_password(current_user.password, form.password.data):
            if form.amount.data >= 500:
                if form.amount.data <= 500000:
                    sender_customer = Customer.query.filter_by(id=current_user.id).first()
                    receiver_customer = Customer.query.filter_by(account_number=form.account_number.data).first()
                    if receiver_customer:
                        if receiver_customer.state == "active":
                            if current_user.balance >= form.amount.data and (
                                    current_user.balance - form.amount.data) >= 500:
                                if current_user.account_number != form.account_number.data:
                                    sender_customer.balance -= int(form.amount.data)
                                    receiver_customer.balance += int(form.amount.data)
                                    tran_date = datetime.now().strftime("%b-%d-%Y %H:%M:%S %p")
                                    log_transaction(current_user.id, receiver_customer.id, form.amount.data, "transfer",tran_date)
                                    db.session.commit()
                                    flash("Transfer was successful!", "info")
                                    return redirect(url_for("transfer"))
                                else:
                                    flash("Self transfer not allowed!", "warning")
                            else:
                                flash("Insufficient funds to transfer!", "warning")
                        else:
                            flash("The account with this account number is not active. Please contact with receiver!",
                                  "warning")
                    else:
                        flash("Not valid account number!", "warning")
                else:
                    flash(
                        "Too much fund to transfer. The fund should be more or equal to 500AFs. "
                        "Please refer to our withdrawal policy!", "warning")

            else:
                flash("Not valid fund. The fund should be more than 500AFs. Please refer to our transfer policy!",
                      "warning")
        else:
            flash("Wrong password!", "danger")

    return render_template("transfer.html", title="Transfer", form=form, fund=show_fund())


def save_picture(form_picture):
    """
    * This function changes the name of the picture to a random 8bit plus its extension .
    * This function also resizes the picture to 125*125 pixels and saves to a directory.
    * As output it returns the new name of the picture.

    :param form_picture:
    :return:
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pic", picture_file_name)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_file_name


def update_account():
    form = UpdatAccountForm()
    if form.validate_on_submit():
        if validate_password(current_user.password, form.password.data):
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
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
    if current_user.user_type == "superadmin":
        requests = Requests.query.all()
    else:
        requests = Requests.query.filter_by(user_type="customer").all()
    return render_template("admin/account_request.html", title="Request", requests=requests, request_size=len(requests))


def accept_request(id):
    request = Requests.query.filter_by(id=id).first()
    user = None
    if request.user_type == "customer":
        user = Customer(username=request.username, email=request.email, password=request.password,
                        account_number=request.account_number, state="active")
    elif request.user_type == "systemuser":
        user = SystemUser(username=request.username, email=request.email, password=request.password, state="active")
    db.session.add(user)
    db.session.delete(request)
    db.session.commit()
    flash("Account Approved!", "info")
    return redirect(url_for("account_request"))


def reject_request(id):
    request = Requests.query.filter_by(id=id).first()
    db.session.delete(request)
    db.session.commit()
    flash("Account Rejected!", "warning")
    return redirect(url_for("account_request"))


def transactionshisory():
    page = request.args.get('page', 1, type=int)

    transactions = TransactionLog.query.order_by(
        TransactionLog.reference_number.desc()).paginate(page, per_page=int(app.config.get('POSTS_PER_PAGE')))
    next_url = url_for('transactionslog', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('transactionslog', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template("admin/transactionslog.html", title="transactions history", transactions=transactions,
                           next_url=next_url, prev_url=prev_url)


def user_transaction_history():
    page = request.args.get('page', 1, type=int)
    transactions = TransactionLog.query.filter(
        or_(TransactionLog.sender_id == current_user.id, TransactionLog.receiver_id == current_user.id)).order_by(
        TransactionLog.reference_number.desc()).paginate(page, per_page=int(app.config.get('POSTS_PER_PAGE')))
    next_url = url_for('user_transactions_hist', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('user_transactions_hist', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template("userstransactionslog.html", title="transactions history", transactions=transactions,
                           next_url=next_url, prev_url=prev_url)


def update_user_password():
    form = UpdatePassword()
    if form.validate_on_submit():
        update_password_result = set_new_password(current_user.password, form.password.data, form.new_password.data)
        db.session.commit()
        if update_password_result:
            flash("Your password changed. Please login with your new password!", "success")
            return redirect(url_for('logout'))
        else:
            flash("Your password was not changed!", "warning")
    return render_template("change_password.html", title="change password", form=form)
