from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from momentjs import momentjs



app = Flask(__name__)
app.config.from_object('config')
bootstrap = Bootstrap(app)

app.jinja_env.globals['momentjs'] = momentjs

mail = Mail(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
app.secret_key = 'mom, generate plz this key'

NEWS_API = []

db = SQLAlchemy(app)


from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from .admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix='/admin')

from .api import api as api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')


login_manager.init_app(app)

from app import views, models
