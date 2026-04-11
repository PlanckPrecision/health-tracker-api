import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates")

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    app.config["SECRET_KEY"] = secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "entries.index"

    with app.app_context():
        from app.models import User, Entry, Goal, DimDate  # noqa: F401 — required for Migrate to detect models

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.entries import entries_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(entries_bp)


    return app
