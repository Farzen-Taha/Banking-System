from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_admin import Admin,BaseView,expose,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from bankingsystem.utilities import set_account_number,set_password
from bankingsystem.utilities import set_account_number

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_type=='superadmin' or current_user.user_type=='systemuser')

class NotificationsView(BaseView):
    @expose('/')
    def notification(self):
        return self.render('admin/notification.html')

class LogoutMenueLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

class SuperAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type=='superadmin'

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

class CustomerView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_type=='superadmin' or current_user.user_type=='systemuser')
    def on_model_change(self, form, model, is_created):
        model.password=set_password(form.password.data)
        model.account_number=set_account_number()
        return super().on_model_change(form, model, is_created)
    form_widget_args = {
        'user_type':{
            'readonly': True    
        },
        'image_file':{
            'readonly': True    
        },
        'account_number':{
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
class SystemUserView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_type=='superadmin')
    def on_model_change(self, form, model, is_created):
        model.password=set_password(form.password.data)
        return super().on_model_change(form, model, is_created)
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