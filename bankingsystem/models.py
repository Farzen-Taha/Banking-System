from bankingsystem import db
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


class Customer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    balance= db.Column(db.Integer)
    password=db.Column(db.String(60),nullable=False)
    def __repr__(self) :
        return f"User ('{self.username}','{self.email}', Type=Customer)"