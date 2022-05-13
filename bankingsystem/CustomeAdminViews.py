import re
from wsgiref.validate import validator
from flask import flash, request, redirect, url_for
from flask_admin.babel import gettext
from flask_admin.contrib.sqla.view import log
from flask_login import current_user, login_required
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from bankingsystem.models import Customer, SuperAdmin

from bankingsystem.utilities import set_account_number, set_password, set_account_number, check_for_username, \
    check_for_email
from wtforms import SelectField
from wtforms.validators import ValidationError
from bankingsystem.form import User
from bankingsystem import db


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_type == "superadmin" or current_user.user_type == "systemuser")

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home'))


class NotificationsView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_type == "superadmin" or current_user.user_type == "systemuser")

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home'))

    @expose("/")
    @login_required
    def notification(self):
        return self.render("admin/notification.html")


class accountMenueLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home'))


class LogoutMenueLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class SuperAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == "superadmin"

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home'))

    form_extra_fields = {"state": SelectField(u'Change Account state',
                                              choices=[('active', 'activate'), ('deactive', 'deactivate')])
                         }
    column_list = ('id', 'user_type', 'username', 'email', "state")
    form_edit_rules = ("username", "email", "state")
    form_create_rules = ("username", "email", "password")
    form_excluded_columns = ("image_file")
    column_exclude_list = ("password", "image_file")
    can_export = True
    column_searchable_list = ('username',)

    def change_state(self, id, form):
        user = User.query.filter_by(id=id).first()
        if form.state.data == "deactivate":
            user.state = "active"
        elif form.state.data == "activate":
            user.state = "deactive"
        db.session.commit()

    def delete_model(self, model):
        if model.id != current_user.id:
            try:
                self.on_model_delete(model)
                self.session.flush()
                self.session.delete(model)
                self.session.commit()

            except Exception as ex:
                if not self.handle_view_exception(ex):
                    flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                    log.exception('Failed to delete record.')

                self.session.rollback()

                return False
            else:
                self.after_model_delete(model)
        else:
            flash("You can not delete yourself", "warning")

    # def on_model_delete(self, model):
    #     if model.id != current_user.id:
    #         return True
    #     else:
    #         flash("You can not delete yourself", "warning")
    #         return False

    def update_model(self, form, model):
        id = request.args.get("id")
        self.change_state(id, form)
        return super().update_model(form, model)

    def user_name_validation(form, field):
        size = len(field.data)
        if size < 3 or not re.match('^\w+$', field.data):
            raise ValidationError("Username must contain only letters numbers or underscore and bemore than 2 charcter")

    def email_validation(form, field):
        if not re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', field.data):
            raise ValidationError("Invalid email.Please enter valid email.")

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = set_password(form.password.data)
        # flash(request.args.id,"sucess")
        return super().on_model_change(form, model, is_created)

    def create_model(self, form):
        ur = check_for_username(form.username.data)
        ue = check_for_email(form.email.data)
        if not ur:
            if not ue:
                return super(SuperAdminView, self).create_model(form)
            else:
                flash("Emai already exits. Please enter another email!", "warning")
        else:
            flash("Username already exits. Please enter another username!", "warning")

    form_widget_args = {
        "user_type": {"readonly": True},
        "image_file": {"readonly": True},
    }
    form_args = {
        "username": {
            "validators": [user_name_validation]
        },
        "email": {
            "validators": [email_validation]
        },
        "user_type": {
            "render_kw": {"value": "superadmin"
                          },
        }, "password": {
            "render_kw": {"type": "password"
                          }
        },

    }


class CustomerView(ModelView):
    column_display_pk = True
    can_export = True
    column_list = ('id', 'user_type', 'username', 'email', "balance", "state")
    form_excluded_columns = ("image_file", "user_type")
    column_exclude_list = ("password", "image_file")
    column_searchable_list = ('username',)
    form_edit_rules = ("username", "email", "state")
    form_create_rules = ("username", "email", "password")

    form_extra_fields = {"state": SelectField(u'Change Account state',
                                              choices=[('active', 'active'), ('deactive', 'deactive')])
                         }

    # THis function makes this tab visible to admin and systemuser.
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_type == "superadmin" or current_user.user_type == "systemuser")

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home'))

    # THis function is checks username field's  standards.
    def user_name_validation(form, field):
        size = len(field.data)
        if size < 3 or not re.match('^\w+$', field.data):
            raise ValidationError("Username must contain only letters numbers or underscore and bemore than 2 charcter")

    # THis function is checks email field's standards.
    def email_validation(form, field):
        if not re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', field.data):
            raise ValidationError("Invalid email.Please enter valid email.")

    # THis function change state of  a user from  active to deactivate or vicversa.
    def change_state(self, id, form):
        user = User.query.filter_by(id=id).first()
        if form.state.data == "deactive":
            user.state = "active"
            db.session.commit()

    def update_model(self, form, model):
        id = request.args.get("id")
        self.change_state(id, form)
        return super().update_model(form, model)

    def create_model(self, form):
        ur = check_for_username(form.username.data)
        ue = check_for_email(form.email.data)
        if not ur:
            if not ue:
                return super(CustomerView, self).create_model(form)
            else:
                flash("Emai already exits. Please enter another email!", "warning")
        else:
            flash("Username already exits. Please enter another username!", "warning")

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = set_password(form.password.data)
            model.account_number = set_account_number()
            return super().on_model_change(form, model, is_created)

    form_widget_args = {
        "user_type": {"readonly": True},
        "image_file": {"readonly": True},
        "account_number": {"readonly": True},
    }
    form_args = {
        "username": {
            "validators": [user_name_validation]
        },
        "email": {
            "validators": [email_validation]
        },
        "password": {
            "render_kw": {"type": "password"
                          }
        }
    }


class SystemUserView(ModelView):
    can_export = True
    column_list = ('id', 'user_type', 'username', 'email', "state")
    form_excluded_columns = ("image_file", "user_type")
    column_exclude_list = ("password", "image_file")
    column_searchable_list = ('username',)
    form_edit_rules = ("username", "email", "state")
    form_create_rules = ("username", "email", "password")

    form_extra_fields = {"state": SelectField(u'Change Account state',
                                              choices=[('active', 'active'), ('deactive', 'deactive')])
                         }

    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_type == "superadmin")

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home'))

    def user_name_validation(form, field):
        size = len(field.data)
        if size < 3 or not re.match('^\w+$', field.data):
            raise ValidationError("Username must contain only letters numbers or underscore and bemore than 2 charcter")

    def email_validation(form, field):
        if not re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', field.data):
            raise ValidationError("Invalid email.Please enter valid email.")

    def change_state(self, id, form):
        user = User.query.filter_by(id=id).first()
        if form.state.data == "deactive":
            user.state = "active"
            db.session.commit()

    def update_model(self, form, model):
        id = request.args.get("id")
        self.change_state(id, form)
        return super().update_model(form, model)

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = set_password(form.password.data)
        return super().on_model_change(form, model, is_created)

    def create_model(self, form):
        ur = check_for_username(form.username.data)
        ue = check_for_email(form.email.data)
        if not ur:
            if not ue:
                return super(SystemUserView, self).create_model(form)
            else:
                flash("Emai already exits. Please enter another email!", "warning")
        else:
            flash("Username already exits. Please enter another username!", "warning")

    form_widget_args = {
        "user_type": {"readonly": True},
        "image_file": {"readonly": True},
    }
    form_args = {
        "username": {
            "validators": [user_name_validation]
        },
        "email": {
            "validators": [email_validation]
        },
        "user_type": {
            "render_kw": {"placeholder": "Enter name", "value": "systemuser"},
        }, "password": {
            "render_kw": {"type": "password"
                          }
        }
    }
