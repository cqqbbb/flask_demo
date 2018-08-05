import pymysql
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

pymysql.install_as_MySQLdb()

db = SQLAlchemy()


class BaseModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    isDelete = db.Column(db.Boolean, default=False)


tb_news_collect = db.Table(
    'tb_news_collect',
    db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('news_id', db.Integer, db.ForeignKey('news_info.id'), primary_key=True)
)
tb_user_follow = db.Table(
    'tb_user_follow',
    db.Column('origin_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('follow_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True)
)


class NewsInfo(db.Model, BaseModel):
    __tablename__ = 'news_info'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    pic = db.Column(db.String(50))
    title = db.Column(db.String(30))
    summary = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    click_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    reason = db.Column(db.String(100), default='')
    comments = db.relationship('NewsComment', backref='news', lazy='dynamic', order_by='NewsComment.id.desc()')

    @property
    def pic_url(self):
        return current_app.config.get('QINIU_URL') + self.pic


class NewsCategory(db.Model, BaseModel):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    news = db.relationship('NewsInfo', backref='category', lazy='dynamic')


class UserInfo(db.Model, BaseModel):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(50), default='user_pic.png')
    nick_name = db.Column(db.String(20))
    signature = db.Column(db.String(200), default='这家伙很懒什么都没写')
    public_count = db.Column(db.Integer, default=0)
    follow_count = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11))
    password_hash = db.Column(db.String(200))
    gender = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)
    news = db.relationship('NewsInfo', backref='user', lazy='dynamic')
    comments = db.relationship('NewsComment', backref='user')
    news_collect = db.relationship('NewsInfo', secondary=tb_news_collect, lazy='dynamic')
    follow_user = db.relationship(
        'UserInfo',
        secondary=tb_user_follow,
        lazy='dynamic',
        backref=db.backref('follow_by_user', lazy='dynamic'),
        primaryjoin=id == tb_user_follow.c.origin_user_id,
        secondaryjoin=id == tb_user_follow.c.follow_user_id
    )

    @property
    def password(self):
        pass

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    @property
    def avatar_url(self):
        # return "/static/news/images/" + self.avatar
        return current_app.config.get('QINIU_URL') + self.avatar


class NewsComment(db.Model, BaseModel):
    __tablename__ = 'news_comment'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    like_count = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, db.ForeignKey('news_comment.id'))
    msg = db.Column(db.String(200))
    comments = db.relationship('NewsComment', lazy='dynamic')
