# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy,inspect
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_simple_captcha import CAPTCHA
import config


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

CAPTCHA = CAPTCHA(config=config.CAPTCHA_CONFIG)
app = CAPTCHA.init_app(app)

Bootstrap(app)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message='请登录'
login_manager.login_message_category='warning'

login_manager.init_app(app)

csrf = CSRFProtect()
csrf.init_app(app)

from app import views,models
