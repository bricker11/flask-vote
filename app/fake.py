# -*— coding:utf-8 -*—
from app import db
from app.models import User,Vote,VoteChoice,VoteRecord
from datetime import datetime,timedelta

# 生成假数据
def create_fake():
    # 建表，删除表，首次部署时执行
    db.drop_all()
    db.create_all()

    user1 =User(username='admin',password='123456',gender=1,birth=datetime.now(),province="1",user_type=0,date=datetime.now())
    user2 =User(username='user1',password='111111',gender=1,birth=datetime.now(),province="7",user_type=1,date=datetime.now())
    user3 =User(username='user2',password='222222',gender=0,birth=datetime.now(),province="2",user_type=1,date=datetime.now())
    user4 =User(username='user3',password='333333',gender=1,birth=datetime.now(),province="3",user_type=1,date=datetime.now())
    user5 =User(username='user4',password='444444',gender=1,birth=datetime.now(),province="1",user_type=1,date=datetime.now())
    user6 =User(username='user5',password='555555',gender=0,birth=datetime.now(),province="4",user_type=1,date=datetime.now())
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.add(user5)
    db.session.add(user6)
    db.session.commit()



    vote1 = Vote(title='特斯拉有问题吗',content='特斯拉有问题吗,大家快来发表你的看法吧',total_choice=2,max_choice=1,start_time=datetime.now(),end_time=datetime.now()+timedelta(days=3))
    db.session.add(vote1)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote1.id,choice='有',code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote1.id,choice='没有',code=2)
    db.session.add(vote_choice2)
    db.session.commit()

    vote2 = Vote(title='股市还会继续涨吗',content='股市还会继续涨吗,大家快来发表你的看法吧',total_choice=2,max_choice=1,start_time=datetime.now(),end_time=datetime.now()-timedelta(days=1))
    db.session.add(vote2)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote2.id,choice='会',code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote2.id,choice='不会',code=2)
    db.session.add(vote_choice2)
    db.session.commit()

    vote3 = Vote(title='你最喜欢的水果',content='你最喜欢的水果,大家快来发表你的看法吧',total_choice=5,max_choice=3,start_time=datetime.now(),end_time=datetime.now()+timedelta(days=2))
    db.session.add(vote3)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote3.id,choice='西瓜',code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote3.id,choice='苹果',code=2)
    db.session.add(vote_choice2)
    db.session.commit()
    vote_choice3 = VoteChoice(vote_id=vote3.id,choice='橘子',code=3)
    db.session.add(vote_choice3)
    db.session.commit()
    vote_choice4 = VoteChoice(vote_id=vote3.id,choice='梨',code=4)
    db.session.add(vote_choice4)
    db.session.commit()
    vote_choice5 = VoteChoice(vote_id=vote3.id,choice='香蕉',code=5)
    db.session.add(vote_choice5)
    db.session.commit()

    vote_record = VoteRecord(user_id=2,vote_id=1,result=1,date=datetime.now())
    db.session.add(vote_record)
    db.session.commit()
    vote_record = VoteRecord(user_id=3,vote_id=1,result=2,date=datetime.now())
    db.session.add(vote_record)
    db.session.commit()
    vote_record = VoteRecord(user_id=4,vote_id=1,result=2,date=datetime.now())
    db.session.add(vote_record)
    db.session.commit()
    vote_record = VoteRecord(user_id=5,vote_id=1,result=2,date=datetime.now())
    db.session.add(vote_record)
    db.session.commit()
    vote_record = VoteRecord(user_id=2,vote_id=2,result=1,date=datetime.now())
    db.session.add(vote_record)
    db.session.commit()





