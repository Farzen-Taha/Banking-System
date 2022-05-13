from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Regexp
from bankingsystem.models import SuperAdmin, SystemUser, Customer, Requests
from flask_login import current_user
from bankingsystem.models import User
from bankingsystem.utilities import validate_password
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20),
                                                   Regexp('^\w+$',
                                                          message='Username must contain only letters numbers or underscore')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    account_type = SelectField(u'Account Type',
                               choices=[('SU', 'System User'), ('CU', 'Customer')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # sa = SuperAdmin.query.filter_by(username=username.data).first()
        # su = SystemUser.query.filter_by(username=username.data).first()
        # cu = Customer.query.filter_by(username=username.data).first()
        user = User.query.filter_by(username=username.data).first()
        req = Requests.query.filter_by(username=username.data).first()
        if user or req:
            raise ValidationError('That name is taken. Please choose a different one.')
        # if sa or su or cu or req:
        #     raise ValidationError('That name is taken. Please choose a different one.')

    def validate_email(self, email):
        # sa = SuperAdmin.query.filter_by(email=email.data).first()
        # su = SystemUser.query.filter_by(email=email.data).first()
        # cu = Customer.query.filter_by(email=email.data).first()
        # req = Requests.query.filter_by(username=email.data).first()
        # if sa or su or cu or req:
        #     raise ValidationError('That email is taken. Please choose a different one.')
        user = User.query.filter_by(email=email.data).first()
        req = Requests.query.filter_by(email=email.data).first()
        if user or req:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class DepositForm(FlaskForm):
    amount = IntegerField("Amount", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Deposit')


class WithdrawForm(FlaskForm):
    amount = IntegerField("Amount", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Witdraw')


class TransferForm(FlaskForm):
    amount = IntegerField("Amount", validators=[DataRequired()])
    account_number = IntegerField("Recipient's account number", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Transfer')


class UpdatAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Regexp('^\w+$',
                                                                          message='Username must contain only letters numbers or underscore'),
                                                   Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            req = Requests.query.filter_by(username=username.data).first()
            if user or req:
                raise ValidationError('That name is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            req = Requests.query.filter_by(email=email.data).first()
            if user or req:
                raise ValidationError('That email is taken. Please choose a different one.')


class UpdatePassword(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField('Update')
