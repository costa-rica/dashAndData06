from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed #used for image uploading
from wtforms import StringField, PasswordField, SubmitField, BooleanField\
    , TextAreaField, DateTimeField, FloatField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from app_package.models import Users
from flask_login import current_user
from datetime import datetime
from app_package import db
from wtforms.widgets import PasswordInput
from flask import current_app, flash, redirect, url_for
from wtforms.widgets import TextArea
from datetime import datetime

class BlogPostForm(FlaskForm):
    # blog_title = StringField('Title', render_kw={"placeholder": "optional (takes word doc title)"})
    blog_description = StringField('Description', widget=TextArea(), render_kw={"placeholder": "optional (takes word doc 2nd/3rd paragraph)"})
    #for TextArea::: https://stackoverflow.com/questions/7979548/how-to-render-my-textarea-with-wtforms
    # date_published = DateField('Date', format='%Y-%m-%d', default=datetime.now().strftime("%Y-%m-%d"))
    date_published = DateField('Date', format='%Y-%m-%d', default=datetime.now())
    #https://stackoverflow.com/questions/62221044/wtforms-fields-html5-datefield-and-timefield-placeholder
    edited = StringField('Post has been edited?')
    link_to_app = StringField('Link to Application', render_kw={"placeholder": "Enter URL"})
