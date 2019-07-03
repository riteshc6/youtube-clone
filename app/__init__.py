from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from elasticsearch import Elasticsearch
import certifi
from flask_babel import Babel, lazy_gettext as _l
from celery import Celery

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']], use_ssl=True, ca_certs=certifi.where(), http_auth=app.config['ELASTIC_AUTH'])\
            if app.config['ELASTICSEARCH_URL'] else None
babel = Babel(app)
celery = Celery(app.name, backend=app.config['CELERY_BROKER_URL'], broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(CELERY_IMPORTS='app.tasks')

from app import routes, models, errors, tasks
