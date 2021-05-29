# -*— coding:utf-8 -*—
from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    # 0:女 1:男
    gender = db.Column(db.Integer, default=1)
    birth = db.Column(db.DateTime,default=datetime.now())
    province = db.Column(db.String(64),default='1')
    date = db.Column(db.DateTime)
    # 0:管理员 1:用户
    user_type = db.Column(db.Integer, default=1)

class Vote(db.Model):
    __tablename__ = 'votes'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(256), unique=True, index=True)
    content = db.Column(db.Text)
    total_choice = db.Column(db.Integer, default=2)
    max_choice = db.Column(db.Integer, default=1)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

class VoteChoice(db.Model):
    __tablename__ = 'votechoices'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'))
    choice = db.Column(db.String(256))
    code = db.Column(db.Integer, default=1)

class VoteRecord(db.Model):
    __tablename__ = 'voterecords'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'))
    result = db.Column(db.Integer)
    date = db.Column(db.DateTime)

# LoginManager需要的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

