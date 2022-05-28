from flask import Blueprint
from flask import render_template, current_app
import logging
from app_package.utils import logs_dir
from logging.handlers import RotatingFileHandler
import os


#Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_blog = logging.getLogger(__name__)
logger_blog.setLevel(logging.DEBUG)
logger_terminal = logging.getLogger('terminal logger')
logger_terminal.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(logs_dir,'error.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

logger_terminal.handlers.clear()
logger_blog.addHandler(file_handler)
logger_terminal.addHandler(stream_handler)

#End set up logger


eh = Blueprint('errors', __name__)

@eh.app_errorhandler(400)
def handle_400(err):
    logger_terminal.info(f'@eh.app_errorhandler(400), err: {err}')
    error_message = "Something went wrong. Maybe you entered something I wasn't expecting?"
    return render_template('error_template.html', error_number="400", error_message=error_message)
#messaged copied from: https://www.pingdom.com/blog/the-5-most-common-http-errors-according-to-google/

@eh.app_errorhandler(401)
def handle_401(err):
    logger_terminal.info(f'@eh.app_errorhandler(401), err: {err}')
    error_message = "This error happens when a website visitor tries to access a restricted web page but isn’t authorized to do so, usually because of a failed login attempt."
    return render_template('error_template.html', error_number="401", error_message=error_message)
#message copied form: https://www.pingdom.com/blog/the-5-most-common-http-errors-according-to-google/

@eh.app_errorhandler(404)
def handle_404(err):
    logger_terminal.info(f'@eh.app_errorhandler(404), err: {err}')
    error_message = "This page doesn't exist. Check what was typed in the address bar."
    return render_template('error_template.html', error_number="404", error_message=error_message)
#404 occurs if address isnt' right

@eh.app_errorhandler(500)
def handle_500(err):
    logger_terminal.info(f'@eh.app_errorhandler(500), err: {err}')
    error_message = f"Something wrong with webiste. Either try again or send email to {current_app.config['MAIL_USERNAME']}."
    return render_template('error_template.html', error_number="500", error_message=error_message)
