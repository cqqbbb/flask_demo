from flask import Blueprint,render_template

news_bp = Blueprint('news', __name__)


@news_bp.route('/')
def index():
    return render_template('news/index.html')