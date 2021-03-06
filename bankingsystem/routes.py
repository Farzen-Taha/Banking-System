from flask import render_template, url_for, redirect
from flask_login import login_required, logout_user, current_user
from bankingsystem.View import (
    accept_request,
    get_all_account_requests,
    reject_request,
    update_account,
    user_register,
    user_login,
    deposit_fund,
    withdraw_fund,
    transfer_fund,
    transactionshisory,
    user_transaction_history,
    update_user_password
)
from bankingsystem.privilege import is_admin,is_customer
from bankingsystem import app


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")

# TODO: Restrict this rout only to users
@app.route("/transactions")
@login_required
@is_customer
def transactions():
    return render_template("transactions.html", title="Transactions")


@app.route("/users")
def users():
    return render_template("users.html", title="users")


@app.route("/register", methods=["GET", "POST"])
def register():
    return user_register()


@app.route("/login", methods=["GET", "POST"])
def login():
    return user_login()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/deposit", methods=["POST", "GET"])
@login_required
@is_customer
def deposit():
    return deposit_fund()


@app.route("/withdraw", methods=["POST", "GET"])
@login_required
@is_customer
def withdraw():
    return withdraw_fund()


@app.route("/transfer", methods=["POST", "GET"])
@login_required
@is_customer
def transfer():
    return transfer_fund()


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    return update_account()


@app.route("/admin/notification/requests", methods=["GET"])
@login_required
def account_request():
    return get_all_account_requests()


@app.route("/admin/notification/acc_requests/<id>", methods=["GET"])
@login_required
def accept_account_request(id):
    return accept_request(id)


@app.route("/admin/notification/rej_requests/<id>", methods=["GET"])
@login_required
def reject_account_request(id):
    return reject_request(id)


@app.route("/admin/notification/transactionslog", methods=["POST","GET"])
@login_required
def transactionslog():
    return transactionshisory()


@app.route("/transactions/alltransactions", methods=["POST","GET"])
@login_required
def user_transactions_hist():
    return user_transaction_history()


@app.route("/changepassword", methods=["POST","GET"])
@login_required
def change_password():
    return update_user_password()