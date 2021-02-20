import os,datetime
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS=False

#CACHE_TYPE = "null"

CSRF_ENABLED = True
SECRET_KEY = '4df9cd2016ce7fd0c35964ed7785ec409d21'

CAPTCHA_CONFIG = {'SECRET_CSRF_KEY':'e0bed4e87e2482cc1671e4242bbd2766df2cbd9b755c'}


PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=15)

POST_SHOW_PER_PAGE = 10

ALLOW_LOCAL_USER_LOGIN = True

POST_DIRECTION = [
    {'name': '买入', 'value': '1'},
    {'name': '卖出', 'value': '0'}
]