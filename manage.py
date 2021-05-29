# -*— coding:utf-8 -*—
from app import create_app,db
from app.models import User,Vote,VoteChoice,VoteRecord
from app.fake import create_fake

# 不同配置选用不同的数据库
app = create_app('development')
# 生成假数据
create_fake()

# db.drop_all()
# db.create_all()
#
# user =User(username='admin',password='123456',gender=1,birth=datetime.now(),province="1",user_type=0,date=datetime.now())
# db.session.add(user)
# db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Vote=Vote, VoteChoice=VoteChoice, VoteRecord=VoteRecord)





