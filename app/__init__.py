from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail
from elasticsearch import Elasticsearch

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
moment = Moment()
mail = Mail()
login.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    from app.auth import auth_bp
    from app.general import general_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(general_bp)

    return app


from app.models import *
