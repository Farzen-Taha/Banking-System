from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin,BaseView,expose
from flask_admin.contrib.sqla import ModelView


app=Flask(__name__)
app.config['SECRET_KEY']="436ef4721d03cc15224c24af0a6b2a4f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)


# from bankingsystem.models import SystemUser
# admin=Admin(app,template_mode='bootstrap4')

# class NotificationsView(BaseView):
#     @expose('/')
#     def notification(self):
#         return self.render('admin/notification.html')
   

# admin.add_view(ModelView(SystemUser,db.session))
# admin.add_view(NotificationsView(name='Notifications',endpoint='notification'))
from bankingsystem import routes