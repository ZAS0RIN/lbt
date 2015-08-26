import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'mom, pridumai secrET key pLz!'


# email server

ADMINS = ['lolbets.mail@ya.ru']
MAIL_SERVER = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
LB_MAIL_SUBJECT_PREFIX = '[LOLBets]'
LB_MAIL_SENDER = 'LOLBets Admin <lolbets.mail@ya.ru>'
FLASKY_ADMIN = 'lolbets.mail@ya.ru'
MAIL_USERNAME = 'lolbets.mail'
MAIL_PASSWORD = 'ZaQ12WsX'

MINIMUM_BET = 10


if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
DATABASE_QUERY_TIMEOUT = 0.5
