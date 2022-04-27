
from flask_wtf import FlaskForm
from wtforms import SelectField,IntegerField, StringField, PasswordField, SubmitField, BooleanField,ValidationError
from wtforms.validators import DataRequired, Length, EqualTo,Email,ValidationError
from bankingsystem.models import SuperAdmin,SystemUser,Customer
from flask_login import current_user
from bankingsystem.models import User
from flask_wtf.file import FileField, FileAllowed
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
    account_number=IntegerField("Reciever's Account Number",validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Transfer')

class UpdatAccountForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That name is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')
