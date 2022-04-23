
from crypt import methods
from flask import Flask,render_template,url_for,redirect,flash
from form import RegistrationForm,LoginForm,DepositForm, WithdrawForm,WithdrawForm
app=Flask(__name__)

app.config['SECRET_KEY']="436ef4721d03cc15224c24af0a6b2a4f"
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

if __name__=='__main__':
    app.run(debug=True)