from flask import Flask,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
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

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_type=='superadmin' or current_user.user_type=='systemuser')
admin=Admin(app,template_mode='bootstrap4',index_view=MyAdminIndexView())

class NotificationsView(BaseView):
    @expose('/')
    def notification(self):
        return self.render('admin/notification.html')


class CreateCustomerView(ModelView):   
    form_widget_args = {
        'user_type':{
            'readonly': True
            
        }
    }
    form_args = {
    'user_type': {
        'render_kw': {
                'value':'customer'
            },
    }
}
class CreateSuperAdminView(ModelView):   
    form_widget_args = {
        'user_type':{
            'readonly': True
        }
    }
    form_args = {
    'user_type': {
        'render_kw': {
                'value':'superadmin'
            },
    }
}
class CreateSystemUserView(ModelView):   
    form_widget_args = {
        'user_type':{
            'readonly': True
            
        }
    }
    form_args = {
    'user_type': {
        'render_kw': {
                'placeholder': 'Enter name',
                'value':'systemuser'
            },
    }
}   

class LogoutMenueLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated



class MySuperAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type=='superadmin'

admin.add_link(LogoutMenueLink(name='logout',category='',url='/logout'))
admin.add_view(MySuperAdminView(SuperAdmin,db.session))
admin.add_view(CreateSystemUserView(SystemUser,db.session))
admin.add_view(CreateCustomerView(Customer,db.session))
admin.add_view(NotificationsView(name='Notifications',endpoint='notification'))
# 


from bankingsystem import routes