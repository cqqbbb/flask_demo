import redis
from flask import Flask,render_template
from views_admin import admin_bp
from views_news import news_bp
from views_user import user_bp
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf import CSRFProtect
from flask_session import Session


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(admin_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(user_bp)
    logging.basicConfig(level=logging.DEBUG)
    file_log_handler = RotatingFileHandler(config.BASE_DIR + "/logs/xjzx.log", maxBytes=1024 * 1024 * 100,
                                           backupCount=10
                                           )
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)
    app.logger_xjzx = logging
    CSRFProtect(app)
    Session(app)
    host = app.config.get('REDIS_HOST')
    port = app.config.get('REDIS_PORT')
    redis_db = app.config.get('REDIS_DB')
    app.redis_client = redis.StrictRedis(host=host, port=port, db=redis_db)

    @app.errorhandler(404)
    def handle404(e):
        return render_template('news/404.html')

    return app
