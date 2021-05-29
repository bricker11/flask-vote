# -*— coding:utf-8 -*—
from flask import render_template,request,session,redirect,url_for,abort,flash,json,jsonify
from flask_login import login_required,current_user,login_user,logout_user
from . import main
from .forms import LoginForm,RegisterForm
from app.utils import generate_vapic
from app import db
from app.models import User
from sqlalchemy import or_,and_
from datetime import datetime
import os, time

# 登录页面
@main.route('/', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if int(form.usertype.data) == 0:
            user = User.query.filter(and_(User.username == form.username.data, User.user_type == 0)).first()
            if user and user.password == form.password.data:
                login_user(user, True)
                return redirect(url_for('auth.admin'))
            else:
                flash('登录失败，账号或密码错误')
        else:
            user = User.query.filter(and_(User.username == form.username.data, User.user_type == 1)).first()
            if user and user.password == form.password.data:
                login_user(user, True)
                return redirect(url_for('auth.user'))
            else:
                flash('登录失败，账号或密码错误')
    return render_template('login.html',form=form)

# 注册页面
@main.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    path = os.path.abspath(os.path.dirname(__file__))[0:-4]
    try:
        path = path + '/static/img/vapic/' + session.get('origincode') + '.jpg'
    except:
        pass
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('用户名已存在')
        else:
            if len(form.password.data) < 6:
                flash('密码不能少于6位')
            elif form.password.data != form.password2.data:
                flash('两次密码不一致')
            elif form.validcode.data.lower() != session.get('validcode'):
                flash('验证码不正确')
            else:
                user = User(username=form.username.data,password=form.password.data,
                            date=datetime.now(),user_type=1)
                db.session.add(user)
                db.session.commit()
                flash('注册成功')
                # 清除验证码缓存
                try:
                    os.remove(path)
                except:
                    pass
        return redirect(url_for('main.register'))
    # 清除验证码缓存
    try:
        os.remove(path)
    except:
        pass
    return render_template('register.html',form=form)

# 退出登录，跳转登录页面
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出')
    return redirect(url_for('main.login'))

########################################### api ##############################################
# 获取并更新验证码
@main.route('/api/validate_picture', methods=['GET','POST'])
def api_validate_picture():
    path = os.path.abspath(os.path.dirname(__file__))[0:-4]
    path = path + '/static/img/vapic/'
    text = generate_vapic(path=path)
    session['origincode'] = text
    session['validcode'] = text.lower()
    url = 'img/vapic/' + text + '.jpg'
    result = {"url": url}
    return jsonify(result)
