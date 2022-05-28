from flask import Blueprint

from flask import render_template, url_for, redirect, flash, request, abort, session,\
    Response, current_app, send_from_directory
from app_package import db, bcrypt, mail, secure_headers
from app_package.models import Users
from app_package.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, \
    RequestResetForm, ResetPasswordForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os

from datetime import datetime, date, time
from sqlalchemy import func
import pandas as pd
import io
from wsgiref.util import FileWrapper
import xlsxwriter
from flask_mail import Message
from app_package.users.utils import send_reset_email
import pytz
import sqlalchemy as sa
import logging
from app_package.utils import logs_dir

#Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_user = logging.getLogger(__name__)
logger_user.setLevel(logging.DEBUG)


file_handler = logging.FileHandler(os.path.join(logs_dir,'users.log'))
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)


logger_user.addHandler(file_handler)
logger_user.addHandler(stream_handler)


users = Blueprint('users', __name__)

#This is to get the security headers on home page
@users.after_request
def set_secure_headers(response):
    secure_headers.framework.flask(response)
    return response

@users.route("/",methods=["GET"])
def home():
    return render_template('home.html')

@users.route("/DataTools")
def dataTools():
    return render_template('datatools/index.html')

@users.route("/about")
def about():
    return render_template('about.html')

@users.route("/pricing")
def pricing():
    return render_template('pricing.html')


@users.route("/blog_register", methods=["GET","POST"])
def register():
    if 'users' in sa.inspect(db.engine).get_table_names():
        logger_user.info(f'db already created')
    else:
        db.create_all()
        logger_user.info(f'db created')

    if current_user.is_authenticated:
        return redirect(url_for('blog.blog_user_home'))
    
    form= RegistrationForm()
    if request.method == 'POST':
        logger_user.info(f'blog_register, post')
        formDict = request.form.to_dict()
        if form.validate_on_submit():
            logger_user.info(f'blog_register, post, form.validate')
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user=Users(email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            flash(f'You are now registered! You can login.', 'success')
            return redirect(url_for('users.login'))

        elif 'This email has not been granted access' in form.errors.get('email'):
            logger_user.warning(f'Email not have permission: {form.errors}')
            flash(f'Email used does not have permission to register', 'warning')
            return redirect(url_for('users.register'))
        elif 'Email already taken' in form.errors.get('email'):
            logger_user.warning(f'Email already taken: {form.errors}')
            flash(f'Email is already taken', 'warning')
            return redirect(url_for('users.register'))
        else:
            logger_user.info(f'form did not validate, error(s): {form.errors}')
            logger_user.info(f'formDict: {formDict}')
            flash(f'No new users accepted at this time', 'warning')
            return redirect(url_for('users.register'))

    logger_user.info(f'blog_register, post, AFTER form.validate')
    return render_template('blog/register.html', title='Register',form=form)


@users.route("/blog_login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.blog_user_home'))
    form = LoginForm()
    email_entry=request.args.get('email_entry')
    pass_entry=request.args.get('pass_entry')
    if request.args.get('email_entry'):
        form.email.data=request.args.get('email_entry')
        form.password.data=request.args.get('pass_entry')

    if request.method == 'POST':
        if form.validate_on_submit():
            user=Users.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('blog.blog_user_home'))
                #^^^ another good thing turnary condition ^^^
        else:
            logger_user.info(f'unsuccessful login occurred')
            flash('Login unsuccessful', 'warning')

    return render_template('blog/login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/reset_password', methods = ["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('email has been sent with instructions to reset your password','info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', legend='Reset Password', form=form)

@users.route('/reset_password/<token>', methods = ["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You are now able to login', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', legend='Reset Password', form=form)

