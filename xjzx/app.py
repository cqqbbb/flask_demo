from flask import Flask
from views_admin import admin_bp
from views_news import news_bp
from views_user import user_bp


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(admin_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(user_bp)

    return app
