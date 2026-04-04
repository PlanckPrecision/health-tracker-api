from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "the_one_piece_is_real"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "entries.index"

    with app.app_context():
        from app.models import User, Entry
        db.create_all()

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.entries import entries_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(entries_bp)


    return app