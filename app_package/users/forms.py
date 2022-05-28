from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed #used for image uploading
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app_package.models import Users
from flask_login import current_user
from datetime import datetime
from app_package import db
from wtforms.widgets import PasswordInput
from flask import current_app


def is_email_allowed(form, email):
    if email.data not in current_app.config['ADMIN_EMAILS']:
        raise ValidationError('This email has not been granted access')

class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),Email(), is_email_allowed])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign up')
    show_password = BooleanField('Show password')

    def validate_email(self, email):
        user=Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken')
    

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = StringField('Password', widget=PasswordInput(hide_value=False), validators=[DataRequired()])
    
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username')
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user=Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email already taken.')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    submit = SubmitField('Request password reset')


    def validate_email(self, email):
        user=Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')