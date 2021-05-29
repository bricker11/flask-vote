# -*— coding:utf-8 -*—
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,RadioField,PasswordField
from wtforms.validators import DataRequired,Length,Regexp,EqualTo
from wtforms import ValidationError
from app.models import User

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    usertype = RadioField('usertype', choices=[('0','管理员'),('1','用户')])
    submit = SubmitField('登录')

# 注册表单
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),EqualTo('password2',message='密码不一致.')])
    password2 = PasswordField('Password2', validators=[DataRequired()])
    validcode = StringField('Validcode',validators=[DataRequired()])
    submit = SubmitField('注册')