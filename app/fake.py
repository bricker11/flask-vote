# -*— coding:utf-8 -*—
from app import db
from app.models import User,Vote,VoteChoice,VoteRecord
from datetime import datetime,timedelta
import random

# 生成假数据
def create_fake():
    # 建表，删除表，首次部署时执行
    db.drop_all()
    db.create_all()

    # 添加管理员
    user =User(username='admin',password='123456',gender=1,birth=datetime.now()-timedelta(days=6000),province="1",user_type=0,date=datetime.now()-timedelta(days=100))
    db.session.add(user)
    db.session.commit()

    # 添加普通用户
    user_num=11
    for i in range(user_num):
        username = 'user' + str(i+1)
        password = str(i+1)*6
        user = User(username=username,password=password,gender=random.randint(0,1),birth=datetime.now()-timedelta(days=random.randint(5000,12000)),province=random.randint(0,30),user_type=1,date=datetime.now()-timedelta(days=random.randint(0,200)))
        db.session.add(user)
        db.session.commit()


    # 添加投票主题
    # 收入,是否有房,婚姻状况,孩子数量,汽车数量,是否购买自行车
    vote_num = 6
    vote = Vote(title='您的收入情况', content='您的收入情况,大家快来发表你的看法吧', total_choice=2, max_choice=1,
                 start_time=datetime.now(), end_time=datetime.now() + timedelta(days=3))
    db.session.add(vote)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote.id, choice='超过2600', code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote.id, choice='不足2600', code=2)
    db.session.add(vote_choice2)
    db.session.commit()

    vote = Vote(title='您是否有房', content='您是否有房,大家快来发表你的看法吧', total_choice=2, max_choice=1,
                start_time=datetime.now(), end_time=datetime.now() + timedelta(days=3))
    db.session.add(vote)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote.id, choice='有', code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote.id, choice='没有', code=2)
    db.session.add(vote_choice2)
    db.session.commit()

    vote = Vote(title='您的婚姻情况', content='您的婚姻情况,大家快来发表你的看法吧', total_choice=2, max_choice=1,
                start_time=datetime.now(), end_time=datetime.now() + timedelta(days=3))
    db.session.add(vote)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote.id, choice='已婚', code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote.id, choice='未婚', code=2)
    db.session.add(vote_choice2)
    db.session.commit()

    vote = Vote(title='您的孩子情况', content='您的孩子情况,大家快来发表你的看法吧', total_choice=3, max_choice=1,
                start_time=datetime.now(), end_time=datetime.now() + timedelta(days=3))
    db.session.add(vote)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote.id, choice='0个', code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote.id, choice='1个', code=2)
    db.session.add(vote_choice2)
    db.session.commit()
    vote_choice3 = VoteChoice(vote_id=vote.id, choice='2个以上', code=3)
    db.session.add(vote_choice3)
    db.session.commit()

    vote = Vote(title='您的汽车数量', content='您的汽车数量,大家快来发表你的看法吧', total_choice=2, max_choice=1,
                start_time=datetime.now(), end_time=datetime.now() + timedelta(days=3))
    db.session.add(vote)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote.id, choice='0辆', code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote.id, choice='1辆', code=2)
    db.session.add(vote_choice2)
    db.session.commit()

    vote = Vote(title='您是否购买了自行车', content='您是否购买了自行车,大家快来发表你的看法吧', total_choice=2, max_choice=1,
                start_time=datetime.now(), end_time=datetime.now() + timedelta(days=3))
    db.session.add(vote)
    db.session.commit()
    vote_choice1 = VoteChoice(vote_id=vote.id, choice='买了', code=1)
    db.session.add(vote_choice1)
    db.session.commit()
    vote_choice2 = VoteChoice(vote_id=vote.id, choice='没买', code=2)
    db.session.add(vote_choice2)
    db.session.commit()


    # 生成投票记录
    for i in range(user_num):
        username = 'user' + str(i+1)
        user = User.query.filter_by(username=username).first()
        for j in range(vote_num):
            vote = Vote.query.filter_by(id=j+1).first()
            vote_record = VoteRecord(user_id=user.id,vote_id=vote.id,result=random.randint(1,vote.total_choice),date=vote.end_time-timedelta(days=random.randint(0,4)))
            db.session.add(vote_record)
            db.session.commit()


    # 其他投票主题
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





