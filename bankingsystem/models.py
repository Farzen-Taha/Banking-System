from datetime import datetime 
from bankingsystem import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column("type", db.String(50))
    image_file = db.Column(db.String(60), nullable=False, default='default.jpg')
    state = db.Column(db.String(15), default="deactive")
    __mapper_args__ = {"polymorphic_on": user_type}

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.user_type}','{self.image_file}')"


class SuperAdmin(User):
    __tablename__ = "super_admin"
    __mapper_args__ = {"polymorphic_identity": "superadmin"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True, autoincrement=True)

    def __init__(self, username, email, password, user_type, image_file, state):
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type
        self.image_file = image_file
        self.state = state
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"SuperAdmin('{self.id}','{self.email}','{self.user_type}','{self.image_file})"


class SystemUser(User):
    __tablename__ = "system_user"
    __mapper_args__ = {"polymorphic_identity": "systemuser"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)


class Customer(User):
    __tablename__ = "customer"
    __mapper_args__ = {"polymorphic_identity": "customer"}

    def __init__(self, username, email, password, account_number, state):
        self.username = username
        self.email = email
        self.password = password
        self.account_number = account_number
        self.state = state

    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
    balance = db.Column(db.Integer, default=0)
    account_number = db.Column("account_number", db.Integer)


class Requests(db.Model):
    __tablename__ = "requests"
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column("type", db.String(50))
    image_file = db.Column(db.String(60), nullable=False, default='default.jpg')
    account_number = db.Column("account_number", db.Integer)

    def __repr__(self):
        return f"Requests('{self.username}','{self.email}','{self.user_type}','{self.image_file}')"


class TransactionLog(db.Model):
    __tablename__ = 'transactionlog'
    reference_number = db.Column("reference_number", db.Integer, primary_key=True)
    sender_id = db.Column("sender_id", db.Integer)
    receiver_id = db.Column("receiver_id", db.Integer)
    fund_amount = db.Column("amount", db.Integer)
    transaction_type = db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(60), nullable=False, default=datetime.now())
