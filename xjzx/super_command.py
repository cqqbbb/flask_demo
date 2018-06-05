from datetime import datetime

from flask import current_app
from flask_script.commands import Command
from models import db, UserInfo
import random


class CreateAdminCommand(Command):
    def run(self):
        """创建管理员"""
        mobile = input('请输入账号:')
        pwd = input('请输入密码')
        user_exists = UserInfo.query.filter_by(mobile=mobile).count()
        if user_exists > 0:
            print('此账号已经存在')
            return
        user = UserInfo()
        user.mobile = mobile
        user.password = pwd
        user.isAdmin = True
        db.session.add(user)
        db.session.commit()
        print('管理员创建成功')


class RegisterUserCommand(Command):
    def run(self):
        user_list = []
        for i in range(1000):
            user = UserInfo()
            user.mobile = str(i)
            user.create_time = datetime(2018,random.randint(1,6),random.randint(1,28))
            user.update_time = datetime(2018,random.randint(1,6),random.randint(1,28))
            user_list.append(user)
        db.session.add_all(user_list)
        db.session.commit()


class LoginCountCommand(Command):
    def run(self):
        time_list = ["08:15", "09:15", "10:15", "11:15", "12:15", "13:15", "14:15", "15:15", "16:15", "17:15", "18:15", "19:15"]
        login_key='login2018_6_5'
        redis_client=current_app.redis_client
        for time in time_list:
            redis_client.hset(login_key,time,random.randint(100,500))
