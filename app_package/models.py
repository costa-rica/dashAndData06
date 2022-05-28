from app_package import db, login_manager
from datetime import datetime, date
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
    

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    timeStamp = db.Column(db.DateTime, default=datetime.now)
    permission = db.Column(db.Text)
    posts = db.relationship('Posts', backref='author', lazy=True)#ONE
    posts_to_html = db.relationship('Postshtml', backref='authorToHTML', lazy=True)#ONE

    def get_reset_token(self, expires_sec=1800):
        s=Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

    def __repr__(self):
        return f"User(id: {self.id},email: {self.email}, permission: {self.permission})"

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title= db.Column(db.Text)
    blog_description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    #timestamp is just record of when post is added to db
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.now)
    #date_published_to_site might be different if updated later on
    edited = db.Column(db.Text)
    link_to_app = db.Column(db.Text)
    word_doc = db.Column(db.Text,unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)#MANY
    posts_to_html = db.relationship('Postshtml', backref='postDetails', lazy=True)#ONE
    posts_to_html_chars = db.relationship('Postshtmltagchars', backref='postDetailsChars', lazy=True)#ONE

    def __repr__(self):
        return f"Posts(id: {self.id},blog_title: {self.blog_title}, " \
            f"date_published: {self.date_published.strftime('%Y-%m-%d')}, timestamp: {self.timestamp})"

class Postshtml(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_row_id = db.Column(db.Integer)#this would be the dict_key if i were still using dict/json method
    row_tag = db.Column(db.Text)
    row_going_into_html = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)#table with MANY
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)#table with MANY
    posts_to_html_tag = db.relationship('Postshtmltagchars', backref='postChars', lazy=True)#table with ONE
    
    def __repr__(self):
        return f"Postshtml(id: {self.id}, word_row_id: {self.word_row_id} , " \
            f"row_tag: {self.row_tag}, row_going_into_html: {self.row_going_into_html})"

class Postshtmltagchars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # posts_to_html_id = db.Column(db.Integer)
    post_tag_characters = db.Column(db.Text)
    word_row_id = db.Column(db.Integer, db.ForeignKey(Postshtml.id), nullable=False)#table with MANY
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)#table with MANY
    

    def __repr__(self):
        return f"Postshtmltagchars(id: {self.id}, " \
            f"posts_to_html_id: {self.posts_to_html_id}, " \
            f"post_tag_characters: {self.post_tag_characters})"
