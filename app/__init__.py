from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'the one piece is real'

    from .views import views
    from .auth import auth

    # customize the url and where to find different pages on the website

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app