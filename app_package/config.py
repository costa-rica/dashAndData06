import os
import json

if os.environ.get('COMPUTERNAME')=='CAPTAIN2020':
    with open(r"C:\Users\captian2020\Documents\config_files\config_dashAndData05.json") as config_file:
        config = json.load(config_file)
elif os.environ.get('COMPUTERNAME')=='NICKSURFACEPRO4':
    with open(r"C:\Users\Costa Rica\OneDrive\Documents\professional\config_files\config_dashAndData05.json") as config_file:
        config = json.load(config_file)
else:
    with open('/home/ubuntu/environments/config_dashAndData05.json') as config_file:
        config = json.load(config_file)


class ConfigDev:
    DEBUG = True
    PORT='5000'
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = config.get('MAIL_SERVER_MSOFFICE')
    MAIL_PORT = config.get('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('MAIL_EMAIL_DD')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD_DD')
    ADMIN_EMAILS = config.get('ADMIN_EMAILS')
    SQLALCHEMY_BINDS ={'dbCage':config.get('CAGE_DB'),
        'dbBls':config.get('BLS')}
    REGISTRATION_KEY =config.get('REGISTRATION_KEY')
    BLS_API_URL = config.get('BLS_API_URL')


class ConfigProd:
    DEBUG = False
    PORT='80'
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = config.get('MAIL_SERVER_MSOFFICE')
    MAIL_PORT = config.get('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('MAIL_EMAIL_DD')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD_DD')
    ADMIN_EMAILS = config.get('ADMIN_EMAILS')
    SQLALCHEMY_BINDS ={'dbCage':config.get('CAGE_DB'),
        'dbBls' : config.get('BLS')}
    REGISTRATION_KEY =config.get('REGISTRATION_KEY')
    BLS_API_URL = config.get('BLS_API_URL')

    