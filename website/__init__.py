from msilib.schema import Directory
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import sys
sys.path.append('../../')
import config
from config import Config

db = SQLAlchemy()

def create_app():
    directory = '%s'%os.getcwd
    #UPLOAD_FOLDER = directory+'\static\images'
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chaindomain.db'
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["SESSION_TYPE"] = "filesystem"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/chaindomain.db'):
        db.create_all(app=app)
        print('Created Database!')
