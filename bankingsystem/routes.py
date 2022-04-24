
from bankingsystem.models import SuperAdmin, SystemUser, Customer
from flask import render_template, url_for, redirect, flash
from flask_login import login_user, logout_user, current_user
from bankingsystem.form import (
    RegistrationForm,
    LoginForm,
    DepositForm,
    TransferForm,
    WithdrawForm,
    WithdrawForm,
)
from bankingsystem import app, db, bcrypt



@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")

@app.route("/transactions")
def transactions():

    return render_template("transactions.html", title="Transactions")


@app.route("/users")
def users():
    return render_template("users.html", title="users")


@app.route("/register", methods=["GET", "POST"])
def register():
  
    if current_user.is_authenticated:
        return redirect(url_for('transactions'))
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
                username=form.username.data, email=form.email.data, password=hashed_pw
            )
            db.create_all()
            db.session.add(system_user)
            db.session.commit()
            flash(
                "Your data saved. Please wait so that your account be verified.", "info"
            )
            return redirect(url_for("login"))
        elif form.account_type.data == "CU":
            customer = Customer(
                username=form.username.data, email=form.email.data, password=hashed_pw
            )
            db.create_all()
            db.session.add(customer)
            db.session.commit()
            flash(
                "Your data saved. Please wait so that your account be verified.", "info"
            )
            return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["POST", "GET"])

def login():
    if current_user.is_authenticated:
        flash("Account authenticated", "success")
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # if form.email.data == "admin@blog.com" and form.password.data == "password":
        #     flash("You loged in successfully", "success")
        #     return redirect(url_for("users"))
        # else:
        # SA = SuperAdmin.query.filter_by(email=form.email.data).first()
        # SU = SystemUser.query.filter_by(email=form.email.data).first()
        # CU = Customer.query.filter_by(email=form.email.data).first()

        # if SA and bcrypt.check_password_hash(SA.password, form.password.data):
        #     login_user(SA, remember=form.remember.data)
        #     return redirect(url_for('admin'))
        # elif SU and bcrypt.check_password_hash(SU.password, form.password.data):
        #     login_user(SU, remember=form.remember.data)
        #     return redirect(url_for('admin'))
        # elif CU and bcrypt.check_password_hash(CU.password, form.password.data):
        #     login_user(CU, remember=form.remember.data)
        #     return redirect(url_for('users'))  
        # else:    
        #     flash("Login unsuccessful, incorrect email or password", "danger")
      
        CU = Customer.query.filter_by(email=form.email.data).first()
        if CU and bcrypt.check_password_hash(CU.password, form.password.data):
            login_user(CU, remember=form.remember.data)
            
            return redirect(url_for('users'))  
        else:    
            flash("Login unsuccessful, incorrect email or password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))  



@app.route("/deposit")
def deposit():
    form = DepositForm()
    return render_template("deposit.html", title="Deposit", form=form)


@app.route("/withdraw")
def withdraw():
    form = WithdrawForm()
    return render_template("withdraw.html", title="Withdraw", form=form)


@app.route("/transfer")
def transfer():
    form = TransferForm()
    return render_template("transfer.html", title="Transfer", form=form)
@app.route("/admin")
def admin():
    
    return render_template("admin.html", title="Admin")
