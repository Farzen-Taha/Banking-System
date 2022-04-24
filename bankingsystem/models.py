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

    discriminator = db.Column("type", db.String(50))
    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return f"User ('{self.username}','{self.email}',Type=Admin)"


class SuperAdmin(User):
    __tablename__ = "super_admin"
    __mapper_args__ = {"polymorphic_identity": "superadmin"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)


class SystemUser(User):
    __tablename__ = "system_user"
    __mapper_args__ = {"polymorphic_identity": "systemuser"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)


class Customer(User):

    __tablename__ = "customer"
    __mapper_args__ = {"polymorphic_identity": "customer"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
    balance = db.Column(db.Integer)