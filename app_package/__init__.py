from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app_package.config import ConfigDev, ConfigProd
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import sys
import logging
from app_package.utils import logs_dir
import os
import secure
from logging.handlers import RotatingFileHandler

#Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_init = logging.getLogger('app_package')
logger_init.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(logs_dir,'__init__.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

# print('file_handler:::', dir(file_handler))
# print('file_handler.name:::', file_handler.name)
# print('file_handler.get_name:::', file_handler.get_name())



logger_init.addHandler(file_handler)
logger_init.addHandler(stream_handler)

#set werkzeug handler
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('werkzeug').addHandler(file_handler)
#End set up logger

logger_init.info(f'Starting App')


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager= LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

secure_headers = secure.Secure()


if os.environ.get('COMPUTERNAME')=='CAPTAIN2020':
    config_class=ConfigDev
#TODO: get ubuntu computer name, let's not just have else here
else:
    config_class=ConfigProd


def create_app(Config=config_class):
    app = Flask(__name__)
    
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    
    from app_package.users.routes import users
    from app_package.error_handlers.routes import eh
    from app_package.blog.routes import blog
    # from app_package.datatools.routes import datatools
    # from app_package.main.routes import main
    from app_package.datatools.cage_search.routes import datatools_cage
    from app_package.datatools.security.routes import datatools_security
    from app_package.datatools.blsSearch.routes import datatools_bls
    
    
    app.register_blueprint(users)
    app.register_blueprint(eh)
    app.register_blueprint(blog)
    # app.register_blueprint(datatools)
    # app.register_blueprint(main)
    app.register_blueprint(datatools_cage)
    app.register_blueprint(datatools_security)
    app.register_blueprint(datatools_bls)
    

    return app