
import re
from wsgiref.validate import validator
from flask import flash, request
from flask_login import current_user, login_required
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from bankingsystem.models import Customer,SuperAdmin
from bankingsystem.utilities import set_account_number, set_password
from bankingsystem.utilities import set_account_number
from wtforms import SelectField
from wtforms.validators import ValidationError
from bankingsystem.form import User
from bankingsystem import db
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and (
                    current_user.user_type == "superadmin" or current_user.user_type == "systemuser")


class NotificationsView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_type == "superadmin" or current_user.user_type == "systemuser")

    @expose("/")
    @login_required
    def notification(self):
        return self.render("admin/notification.html")


class LogoutMenueLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class SuperAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == "superadmin"
    form_extra_fields={"state" : SelectField(u'Change Account state',
                               choices=[ ('active', 'active'),('false', 'deactive')])
                    }
    form_edit_rules=("username","email","state")
    form_create_rules=("username","email","password")
    form_excluded_columns = ("image_file")
    column_exclude_list = ("password","image_file")

    column_searchable_list = ('username',)

    def change_state(self,id,form):
        user = User.query.filter_by(id=id).first()
        print("----------------------User is-------: ",user)
        if(form.state.data=="deactive"):
            user.state= "active"
            db.session.commit()
    
    def update_model(self, form, model):
        id = request.args.get("id")
        self.change_state(id,form)
        return super().update_model(form, model)


    def user_name_validation(form,field):
        size=len(field.data)
        if size<3 or not re.match('^\w+$',field.data) :
            raise ValidationError("Username must contain only letters numbers or underscore and bemore than 2 charcter")
    def email_validation(form,field):
        if not re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$' ,field.data):
            raise ValidationError("Invalid email.Please enter valid email.")

    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = set_password(form.password.data)
        # flash(request.args.id,"sucess")
        return super().on_model_change(form, model, is_created)

    form_widget_args = {
        "user_type": {"readonly": True},
        "image_file": {"readonly": True},
    }
    form_args = {
        "username":{
            "validators":[user_name_validation]
        },
        "email":{
            "validators":[email_validation]
        },
        "user_type": {
            "render_kw": {"value": "superadmin"
            },
        },"password": {
            "render_kw": {"type": "password"
            }
        },

      
        
    }


class CustomerView(ModelView):
    form_excluded_columns = "image_file"
    column_exclude_list = "password"
    column_searchable_list = ('username',)
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_type == "superadmin" or current_user.user_type == "systemuser")

    def on_model_change(self, form, model, is_created):
        model.password = set_password(form.password.data)
        model.account_number = set_account_number()
        return super().on_model_change(form, model, is_created)

    form_widget_args = {
        "user_type": {"readonly": True},
        "image_file": {"readonly": True},
        "account_number": {"readonly": True},
    }
    form_args = {
        "user_type": {
            "render_kw": {"value": "customer"},
        }, "password": {
            "render_kw": {"type": "password"
            }
        }
    }


class SystemUserView(ModelView):
    form_excluded_columns = "image_file"
    column_exclude_list = "password"

    column_searchable_list = ('username',)

  
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_type == "superadmin")

    def on_model_change(self, form, model, is_created):
        model.password = set_password(form.password.data)
        return super().on_model_change(form, model, is_created)

    form_widget_args = {
        "user_type": {"readonly": True},
        "image_file": {"readonly": True},
    }
    form_args = {
        "user_type": {
            "render_kw": {"placeholder": "Enter name", "value": "systemuser"},
        }, "password": {
            "render_kw": {"type": "password"
            }
        }
    }
