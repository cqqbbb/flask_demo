import random
from flask import Blueprint, session, make_response, request, jsonify
from flask import current_app
from flask import redirect
from flask import render_template
from models import UserInfo, db, NewsInfo, NewsCategory
from utils.captcha.captcha import captcha
from utils.ytx_sdk.ytx_send import sendTemplateSMS
from utils.qiniu_xjzx import upload_pic
import re
import functools
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/image_code')
def image_code():
    name, yzm, image = captcha.generate_captcha()
    session['image_yzm'] = yzm
    response = make_response(image)
    response.mimetype = 'image/png'
    return response


@user_bp.route('/sms_yzm')
def sms_yzm():
    dict1 = request.args
    mobile = dict1.get('mobile')
    yzm = dict1.get('yzm')
    if yzm != session['image_yzm']:
        return jsonify(result=1)
    yzm2 = random.randint(1000, 9999)
    session['sms_yzm'] = yzm2
    sendTemplateSMS(mobile, {yzm2, 5}, 1)
    print(" ==========================%s" % yzm2)
    return jsonify(result=2)


@user_bp.route('/register', methods=['POST'])
def register():
    dict1 = request.form
    mobile = dict1.get('mobile')
    yzm_image = dict1.get('yzm_image')
    yzm_sms = dict1.get('yzm_sms')
    pwd = dict1.get('pwd')
    if not all([mobile, yzm_image, yzm_sms, pwd]):
        return jsonify(result=1)
    if yzm_image != session['image_yzm']:
        return jsonify(result=2)
    if int(yzm_sms) != session['sms_yzm']:
        return jsonify(result=3)
    if not re.match(r'[a-zA-Z0-9_]{6,20}', pwd):
        return jsonify(result=4)
    mobile_count = UserInfo.query.filter_by(mobile=mobile).count()
    if mobile_count > 0:
        return jsonify(result=5)
    user = UserInfo()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = pwd
    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('用户注册访问数据库失败')
        return jsonify(result=7)
    return jsonify(result=6)


def login_time_count():
    now = datetime.now()
    redis_client = current_app.redis_client
    login_key = 'login%d_%d_%d' % (now.year, now.month, now.day)
    time_list = ["08:15", "09:15", "10:15", "11:15", "12:15", "13:15", "14:15", "15:15", "16:15", "17:15", "18:15",
                 "19:15"]
    for index, time in enumerate(time_list):
        if now.hour < index + 8 or (now.hour == index + 8 and now.minute <= 15):
            redis_client.hincrby(login_key, time, 1)
            break
    else:
        redis_client.hincrby(login_key, '19:15', 1)


@user_bp.route('/login', methods=['POST'])
def login():
    dict1 = request.form
    mobile = dict1.get('mobile')
    pwd = dict1.get('pwd')
    if not all([mobile, pwd]):
        return jsonify(result=1)
    user = UserInfo.query.filter_by(mobile=mobile).first()
    if user:
        if user.check_pwd(pwd):
            # 将当前时段的登陆数量加一,供后台admin图表展示
            login_time_count()
            session['user_id'] = user.id
            return jsonify(result=4, avatar=user.avatar_url, nick_name=user.nick_name)
        else:
            return jsonify(result=3)
    else:
        return jsonify(result=2)


@user_bp.route('/logout', methods=['POST'])
def logout():
    del session['user_id']
    return jsonify(result=1)


def login_required(view_fun):
    @functools.wraps(view_fun)
    def fun2(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('')
        return view_fun(*args, **kwargs)

    return fun2


@user_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    return render_template('news/user.html', user=user)


@user_bp.route('/base', methods=['GET', 'POST'])
@login_required
def base():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    if request.method == 'GET':
        return render_template('news/user_base_info.html', user=user)
    elif request.method == 'POST':
        dict1 = request.form
        signature = dict1.get('signature')
        nick_name = dict1.get('nick_name')
        gender = dict1.get('gender')
        if gender == 'True':
            gender = True
        elif gender == 'False':
            gender = False
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender
        db.session.commit()
        return jsonify(result=1, user=user)


@user_bp.route('/pic', methods=['GET', 'POST'])
@login_required
def pic():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    if request.method == 'GET':
        return render_template('news/user_pic_info.html', user=user)
    elif request.method == 'POST':
        avatar = request.files.get('avatar')
        filename = upload_pic(avatar)
        user.avatar = filename
        db.session.commit()
        return jsonify(result=1, avatar=user.avatar_url)


@user_bp.route('/follow')
@login_required
def follow():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    page = int(request.args.get('page', 1))
    pagination = user.follow_user.paginate(page, 4, False)
    user_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_follow.html',
                           user_list=user_list,
                           total_page=total_page,
                           page=page)


@user_bp.route('/pwd', methods=['GET', 'POST'])
@login_required
def pwd():
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    elif request.method == 'POST':
        dict1 = request.form
        current_pwd = dict1.get('current_pwd')
        new_pwd = dict1.get('new_pwd')
        new_pwd2 = dict1.get('new_pwd2')
        if not all([current_pwd, new_pwd, new_pwd2]):
            return render_template('news/user_pass_info.html', msg="请填写完整密码")
        if not re.match(r'[a-zA-Z0-9]{6,20}', current_pwd):
            return render_template('news/user_pass_info.html', msg="密码错误")
        if not re.match(r'[a-zA-Z0-9]{6,20}', new_pwd):
            return render_template('news/user_pass_info.html', msg="新密码格式错误,只能为字母,数字,下划线")
        if new_pwd2 != new_pwd:
            return render_template('news/user_pass_info.html', msg='两次输入的密码不一致')
        user = UserInfo.query.get(session['user_id'])
        print(user.check_pwd(current_pwd))
        if not user.check_pwd(current_pwd):
            return render_template('news/user_pass_info.html', msg='用户密码错误')
        user.password = new_pwd2
        db.session.commit()
        return render_template('news/user_pass_info.html', msg='修改成功')


@user_bp.route('/collect')
@login_required
def collect():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    page = int(request.args.get('page', 1))
    pagination = user.news_collect.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_collection.html',
                           news_list=news_list,
                           total_page=total_page,
                           page=page
                           )


@user_bp.route('/release', methods=['GET', 'POST'])
@login_required
def release():
    category_list = NewsCategory.query.all()
    if request.method == 'GET':
        return render_template('news/user_news_release.html', category_list=category_list)
    elif request.method == 'POST':
        dict1 = request.form
        title = dict1.get('title')
        category_id = int(dict1.get('category'))
        summary = dict1.get('summary')
        content = dict1.get('content')
        news_pic = request.files.get('news_pic')
        if not all([title, category_id, summary, content, news_pic]):
            return render_template(
                'news/user_news_release.html',
                category_list=category_list,
                msg='数据不能为空'
            )
        filename = upload_pic(news_pic)
        news = NewsInfo()
        news.title = title
        news.category_id = category_id
        news.summary = summary
        news.content = content
        news.pic = filename
        news.user_id = session['user_id']

        db.session.add(news)
        db.session.commit()

        return redirect('/user/newsList')


@user_bp.route('/newsList')
@login_required
def newsList():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)
    page = int(request.args.get('page', 1))
    pagination = user.news.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/user_news_list.html',
                           news_list=news_list,
                           total_page=total_page,
                           page=page)


@user_bp.route('/release_update/<int:news_id>', methods=['GET', 'POST'])
@login_required
def release_update(news_id):
    news = NewsInfo.query.get(news_id)
    category_list = NewsCategory.query.all()
    if request.method == 'GET':
        return render_template('news/user_news_update.html',
                               news=news,
                               category_list=category_list)
    elif request.method == 'POST':
        dict1 = request.form
        title = dict1.get('title')
        category_id = int(dict1.get('category'))
        summary = dict1.get('summary')
        content = dict1.get('content')
        news_pic = request.files.get('news_pic')
        if not all([title, category_id, summary, content]):
            return render_template(
                'news/user_news_release.html',
                category_list=category_list,
                msg='数据不能为空'
            )
        if news_pic:
            filename = upload_pic(news_pic)
            news.pic = filename
        # 修改不需要创建新的对象
        news.title = title
        news.category_id = category_id
        news.summary = summary
        news.content = content
        news.user_id = session['user_id']
        news.update_time = datetime.now()
        news.status = 1

        db.session.add(news)
        db.session.commit()

        return redirect('/user/newsList')


@user_bp.route('/<int:user_id>')
def user(user_id):
    user = UserInfo.query.get(user_id)
    page = int(request.args.get('page', 1))
    pagination = user.news.order_by(NewsInfo.update_time.desc()).paginate(page, 6, False)
    news_list = pagination.items
    total_page = pagination.pages
    return render_template('news/other.html',
                           user=user,
                           news_list=news_list,
                           total_page=total_page,
                           page=page)
