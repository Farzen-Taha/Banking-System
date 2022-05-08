from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin,BaseView,expose,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

app=Flask(__name__)
app.config['SECRET_KEY']="436ef4721d03cc15224c24af0a6b2a4f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'
from bankingsystem.models import Customer, SuperAdmin, SystemUser
from bankingsystem.CustomeAdminViews import MyAdminIndexView,SuperAdminView,SystemUserView,CustomerView,LogoutMenueLink,NotificationsView
admin=Admin(app,template_mode='bootstrap4',index_view=MyAdminIndexView())

admin.add_link(LogoutMenueLink(name='Logout',category='',url='/logout'))
admin.add_view(SuperAdminView(SuperAdmin,db.session))
admin.add_view(SystemUserView(SystemUser,db.session))
admin.add_view(CustomerView(Customer,db.session))
admin.add_view(NotificationsView(name='Notifications',endpoint='notification'))


from bankingsystem import routes
db.create_all()