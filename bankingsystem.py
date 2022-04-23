
from flask import Flask,render_template,url_for,redirect,flash
from form import RegistrationForm,LoginForm,DepositForm, TransferForm, WithdrawForm,WithdrawForm
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.config['SECRET_KEY']="436ef4721d03cc15224c24af0a6b2a4f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class SuperAdmin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}',Type=Admin)"


class SystemUser(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}',Type=System User)"


class Cusomer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    balance= db.Column(db.Integer)
    password=db.Column(db.String(60),nullable=False)
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}', Type=Customer)"



@app.route("/")
@app.route("/transactions")
def transactions():

    return render_template('transactions.html',title='Transactions')

@app.route("/users")
def users():
    return render_template('users.html',title="users")

@app.route("/register", methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        flash('Your account has been created. You can log in now!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title="Register",form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        if form.email.data=="admin@blog.com" and form.password.data=="password":
            flash('You loged in successfully','success')
            return redirect(url_for('users'))
        else:
            flash('Login unsuccessful, incorrect email or password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/deposit")
def deposit():
    form=DepositForm()
    return render_template('deposit.html',title="Deposit",form=form)

@app.route("/withdraw")
def withdraw():
    form=WithdrawForm()
    return render_template('withdraw.html',title="Withdraw",form=form)


@app.route("/transfer")
def transfer():
    form=TransferForm()
    return render_template('transfer.html',title="Transfer",form=form)

if __name__=='__main__':
    app.run(debug=True)