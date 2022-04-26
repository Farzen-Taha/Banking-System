
from flask_wtf import FlaskForm
from wtforms import SelectField,IntegerField, StringField, PasswordField, SubmitField, BooleanField,ValidationError
from wtforms.validators import DataRequired, Length, EqualTo,Email,ValidationError
from bankingsystem.models import SuperAdmin,SystemUser,Customer

class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # account_type=['Super Admin','System User','Customer']
    account_type=SelectField(u'Account Type', choices=[('SA', 'Super Admin'), ('SU', 'System User'), ('CU', 'Customer')])
    submit = SubmitField('Sign Up')


    def validate_username(self, username):
        SA = SuperAdmin.query.filter_by(username=username.data).first()
        SU=SystemUser.query.filter_by(username=username.data).first()
        CU=Customer.query.filter_by(username=username.data).first()
        if SA or SU or CU:
            raise ValidationError(
                'That name is taken. Please choose a different one.')

    def validate_email(self, email):
        SA = SuperAdmin.query.filter_by(email=email.data).first()
        SU = SystemUser.query.filter_by(email=email.data).first()
        CU = Customer.query.filter_by(email=email.data).first()
        if SA or SU or CU:
            raise ValidationError(
                'That email is taken. Please choose a different one.')
    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember=BooleanField('Remember me' )
    submit = SubmitField('Login')

class DepositForm(FlaskForm):
    amount=IntegerField("Amount",validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Deposit')

class WithdrawForm(FlaskForm):
    amount=IntegerField("Amount",validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Witdraw')

class TransferForm(FlaskForm):
    amount=IntegerField("Amount",validators=[DataRequired()])
    account_number=IntegerField("Account Number",validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Transfer')

