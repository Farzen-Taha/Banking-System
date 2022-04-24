from bankingsystem import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

class SuperAdmin(db.Model,UserMixin):

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}',Type=Admin)"
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }


class SystemUser(db.Model,UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}',Type=System User)"


class Customer(db.Model,UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    balance= db.Column(db.Integer)
    password=db.Column(db.String(60),nullable=False)
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}', Type=Customer)"