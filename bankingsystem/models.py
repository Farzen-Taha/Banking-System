from bankingsystem import db, login_manager
from flask_login import UserMixin
from sqlalchemy import event

from werkzeug.security import generate_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from bankingsystem import bcrypt
import os
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # salt = db.Column(db.Binary, default=lambda: os.urandom(512))
    user_type = db.Column("type", db.String(50))
    __mapper_args__ = {"polymorphic_on": user_type}

    def __repr__(self):
        return f"User ('{self.username}','{self.email}',Type=Admin)"
    
    # def compute_password_hash(new_Value):
    #     hashed_pw = bcrypt.generate_password_hash(new_Value).decode("utf-8")
    #     return hashed_pw
class SuperAdmin(User):
    __tablename__ = "super_admin"
    __mapper_args__ = {"polymorphic_identity": "superadmin"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True,autoincrement=True)


class SystemUser(User):
    __tablename__ = "system_user"
    __mapper_args__ = {"polymorphic_identity": "systemuser"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)


class Customer(User):

    __tablename__ = "customer"
    __mapper_args__ = {"polymorphic_identity": "customer"}
    id = db.Column("id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
    balance = db.Column(db.Integer)