from flask import Blueprint, render_template, session, jsonify, request
from models import NewsCategory, UserInfo, NewsInfo

news_bp = Blueprint('news', __name__)


@news_bp.route('/')
def index():
    if 'user_id' in session:
        user = UserInfo.query.get(session['user_id'])
    else:
        user = None
    category_list = NewsCategory.query.all()
    count_list = NewsInfo.query.filter_by(status=2).order_by(NewsInfo.click_count.desc())[0:6]
    return render_template('news/index.html',
                           category_list=category_list,
                           user=user,
                           count_list=count_list)


@news_bp.route('/newsList')
def newsList():
    page = int(request.args.get('page', '1'))
    category_id = int(request.args.get('category_id', '0'))
    pagination = NewsInfo.query.filter_by(status=2)
    if category_id:
        pagination = pagination.filter_by(category_id=category_id)
    pagination = pagination.order_by(NewsInfo.update_time.desc()).paginate(page, 4, False)
    news_list = pagination.items

    news_list2 = []
    for news in news_list:
        news_dict = {
            'id': news.id,
            'pic': news.pic_url,
            'title': news.title,
            'summary': news.summary,
            'user_avatar': news.user.avatar_url,
            'user_nick_name': news.user.nick_name,
            'update_time': news.update_time.strftime('%Y-%m-%d'),
            'user_id': news.user.id,
            'category_id':category_id
        }
        news_list2.append(news_dict)
    return jsonify(news_list=news_list2)
