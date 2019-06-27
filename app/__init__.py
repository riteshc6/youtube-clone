from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from elasticsearch import Elasticsearch
import certifi
from flask_babel import Babel, lazy_gettext as _l

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

from app import routes
