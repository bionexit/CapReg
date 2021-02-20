import os,datetime
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS=False

#CACHE_TYPE = "null"

CSRF_ENABLED = True
SECRET_KEY = '08f684fc425c4b2f8af3195057a66b066353338637eb3ccf6b62266538a7e8a01820466d8b40048e8bcd1ebe79b7b776a487'

CAPTCHA_CONFIG = {'SECRET_CSRF_KEY':'329eee0d07053a4deedc73700f7984719635f87284818080591c72dbf6e4b1352d70bc60a8c5fa1125923541bbbb372a01cb'}


PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=15)

POST_SHOW_PER_PAGE = 10

ALLOW_LOCAL_USER_LOGIN = True

POST_DIRECTION = [
    {'name': '买入', 'value': '1'},
    {'name': '卖出', 'value': '0'}
]