# -*— coding:utf-8 -*—
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,RadioField,PasswordField,SelectField,TextAreaField,SelectMultipleField
from wtforms.validators import DataRequired,Length,Regexp,EqualTo
from app.models import User,Vote

# 搜索用户表单(账户管理)
class SearchUserForm1(FlaskForm):
    choices = [('1','用户名'),('2','密码')]
    option = SelectField('Option',validators=[DataRequired()],choices=choices,coerce=str)
    key = StringField('key',validators=[DataRequired()])
    submit = SubmitField('提交')

# 搜索用户表单（信息管理）
class SearchUserForm(FlaskForm):
    choices = [('1','用户名'),('2','性别')]
    option = SelectField('Option',validators=[DataRequired()],choices=choices,coerce=str)
    key = StringField('key',validators=[DataRequired()])
    submit = SubmitField('提交')

# 搜索投票表单
class SearchVoteForm(FlaskForm):
    choices = [('0','全部'),('1','进行中'),('2','已截止')]
    option = SelectField('Option',validators=[DataRequired()],choices=choices,coerce=str)
    key = StringField('key',validators=[DataRequired()])
    submit = SubmitField('提交')

# 添加投票表单
class AddVoteForm(FlaskForm):
    title = StringField('title',validators=[DataRequired()])
    content = TextAreaField('content', validators=[DataRequired()])
    choices = StringField('title',validators=[DataRequired()])
    total_choice = StringField('title',validators=[DataRequired()])
    max_choice = StringField('title', validators=[DataRequired()])
    end_time = StringField('title', validators=[DataRequired()])
    submit = SubmitField('发布')

# 修改用户信息表单
class UserInfoForm(FlaskForm):
    provinces = [('1','北京市'),('2','广东省'),('3','山东省'),('4','江苏省'),
                ('5','河南省'),('6','上海市'),('7','河北省'),('8','浙江省'),
                ('9','香港特别行政区'),('10','陕西省'),('11','湖南省'),('12','重庆市'),
                ('13','福建省'),('14','天津市'),('15','云南省'),('16','四川省'),
                ('17','广西壮族自治区'),('18','安徽省'),('19','海南省'),('20','江西省'),
                ('21','湖北省'),('22','山西省'),('23','辽宁省'),('24','台湾省'),
                ('25','黑龙江'),('26','内蒙古自治区'),('27','澳门特别行政区'),('28','贵州省'),
                ('29','甘肃省'),('30','青海省'),('31','新疆维吾尔自治区'),('32','西藏区'),
                ('33','吉林省'),('34','宁夏回族自治区')]
    username = StringField('username', validators=[DataRequired()])
    gender = SelectField('gender', validators=[DataRequired()], choices=[('0','女'),('1','男')] ,coerce=str)
    birth = StringField('birth', validators=[DataRequired()])
    province = SelectField('province', validators=[DataRequired()], choices=provinces, coerce=str)
    old_password = PasswordField('old_password')
    new_password = PasswordField('new_password')
    submit = SubmitField('修改')

# 投票分析选择表单
class VoteAnalysForm(FlaskForm):
    titles = SelectField('titles', validators=[DataRequired()], coerce=str)
    submit = SubmitField('分析')

    def __init__(self):
        super(VoteAnalysForm, self).__init__()
        self.titles.choices = [(str(v.id), v.title) for v in Vote.query.order_by('id')]