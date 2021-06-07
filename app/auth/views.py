# -*— coding:utf-8 -*—
from flask import render_template,request,session,redirect,url_for,abort,flash,json,jsonify
from flask_login import login_required,current_user,login_user,logout_user
from . import auth
from .forms import SearchUserForm1,SearchUserForm,SearchVoteForm,AddVoteForm,UserInfoForm,VoteAnalysForm
from app import db
from app.models import User,Vote,VoteChoice,VoteRecord
from sqlalchemy import or_,and_
from datetime import datetime,timedelta
from app.dctree import saveData,generateDctree
import time

########################################## 管理员区 ######################################
#                                                                                      #
########################################################################################
# 管理员首页
@auth.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    return render_template('admin/index.html',username=current_user.username)

# 管理账号页
@auth.route('/admin/usermanage', methods=['GET','POST'])
@login_required
def usermanage():
    form = SearchUserForm1()
    return render_template('admin/usermanage.html',form=form,username=current_user.username,page_id='1')

# 管理信息页
@auth.route('/admin/infomanage', methods=['GET','POST'])
@login_required
def infomanage():
    form = SearchUserForm()
    return render_template('admin/infomanage.html',form=form,username=current_user.username,page_id='2')

# 发布投票页
@auth.route('/admin/voteadd', methods=['GET','POST'])
@login_required
def voteadd():
    form = AddVoteForm()
    if form.validate_on_submit():
        choices = form.choices.data[0:-1].split('^')
        total_choice = int(form.total_choice.data)
        max_choice = int(form.max_choice.data)
        end_time = datetime.strptime(form.end_time.data, '%Y-%m-%d %H:%M:%S')
        vote = Vote.query.filter_by(title=form.title.data).first()
        if vote:
            flash('发布失败，该主题的投票已经存在，请输入新主题')
        else:
            if len(choices) < total_choice:
                flash('发布失败，选项不足，请正确设置选项')
            elif end_time < datetime.now():
                flash('发布失败，截止时间必须在当前时间之后')
            else:
                vote = Vote(title=form.title.data,content=form.content.data,total_choice=total_choice,
                            max_choice = max_choice,end_time=end_time)
                vote.start_time = datetime.now()
                db.session.add(vote)
                db.session.commit()
                i = 1
                for choice in choices:
                    votechoice = VoteChoice(vote_id=vote.id,choice=choice,code=i)
                    db.session.add(votechoice)
                    db.session.commit()
                    i = i + 1
                flash('发布成功')
        return redirect(url_for('auth.voteadd'))
    return render_template('admin/voteadd.html',form=form,username=current_user.username,page_id='3')

# 投票管理页
@auth.route('/admin/votemanage', methods=['GET','POST'])
@login_required
def votemanage():
    form = SearchVoteForm()
    return render_template('admin/votemanage.html',form=form,username=current_user.username,page_id='4')

# 投票分析页
@auth.route('/admin/voteanalys', methods=['GET','POST'])
@login_required
def voteanalys():
    form = VoteAnalysForm()
    vote_id = session.get('vote_id')
    if vote_id == None:
        vote_id = 1
    if request.method == "POST":
        vote_id = form.titles.data
        session['vote_id'] = int(vote_id)
        return redirect(url_for('auth.voteanalys'))
    form.titles.data = str(vote_id)
    return render_template('admin/voteanalys.html', form=form, vote_id=vote_id, username=current_user.username,page_id='5')

# 数据挖掘页
@auth.route('/admin/datamine', methods=['GET','POST'])
@login_required
def datamine():
    votes = Vote.query.all()
    attributes = []
    for vote in votes:
        attributes.append(vote.title)
    return render_template('admin/datamine.html', attributes=attributes, username=current_user.username,page_id='6')

# 根据所选属性和标签生成决策树的api
@auth.route('/api/admin/datamine', methods=['GET','POST'])
def api_admin_datamine():
    # 属性和标签的代码值
    attr_code = request.form['attr'].split(',')[0:-1]
    label_code = request.form['label'].split(',')[0:-1]
    attribute = []
    label = []
    # 获取属性和标签的文字值
    for i in range(len(attr_code)):
        vote = Vote.query.filter_by(id=int(attr_code[i])).first()
        attribute.append(vote.title)
    for i in range(len(label_code)):
        vote = Vote.query.filter_by(id=int(label_code[i])).first()
        label.append(vote.title)
    attribute.extend(label)
    # 所有普通用户数
    user_num = len(User.query.all()) - 1
    users = User.query.filter(User.id > 1).all()
    # 对每一个用户（一行数据的来源），遍历其相关投票结果
    choices = []
    for user in users:
        choice = []
        for vote_id in attr_code:
            vote_record = VoteRecord.query.filter(and_(VoteRecord.user_id==user.id,VoteRecord.vote_id==vote_id)).first()
            vote_result = VoteChoice.query.filter(and_(VoteChoice.vote_id==vote_id,VoteChoice.code==vote_record.result)).first()
            choice.append(vote_result.choice)
        for vote_id in label_code:
            vote_record = VoteRecord.query.filter(and_(VoteRecord.user_id==user.id,VoteRecord.vote_id==vote_id)).first()
            vote_result = VoteChoice.query.filter(and_(VoteChoice.vote_id==vote_id,VoteChoice.code==vote_record.result)).first()
            choice.append(vote_result.choice)
        choices.append(choice)
    # 结果写入数据表中
    saveData(attribute,choices)
    time.sleep(0.2)
    # 根据表生成决策树
    generateDctree()
    #决策树结果图保存的位置
    url = 'csv/img/dctree.jpg'
    result = {
        "status": 0,
        "url": url,
    }
    return jsonify(result)

################################### api ################################
# 获取账户管理页的表格数据
@auth.route('/api/admin/usermanage', methods=['GET','POST'])
def api_admin_usermanage():
    users = User.query.all()
    data = []
    i = 0
    for user in users:
        i = i + 1
        # 得到每个用户的信息
        if user.user_type == 0:
            usertype = '管理员'
        else:
            usertype = '用户'
        data_row = {'sno': i,
                    'username': user.username,
                    'password': user.password,
                    'usertype': usertype,
                    'date': user.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(data_row)
    count = len(users)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 模糊查找用户的api接口
@auth.route('/api/admin/searchuser1', methods=['GET','POST'])
def api_admin_searchuser1():
    option = int(request.form['option'])
    key = request.form['key']
    if option == 1:
        users = User.query.filter(User.username.like('%'+key+'%')).all()
    else:
        users = User.query.filter(User.password.like('%'+key+'%')).all()
    data = []
    i = 0
    for user in users:
        i = i + 1
        # 得到每个用户的信息
        if user.user_type == 0:
            usertype = '管理员'
        else:
            usertype = '用户'
        data_row = {'sno': i,
                    'username': user.username,
                    'password': user.password,
                    'usertype': usertype,
                    'date': user.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(data_row)
    count = len(users)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 获取需要修改的用户的信息
@auth.route('/api/admin/edituser', methods=['GET','POST'])
def api_admin_edituser():
    username = request.get_data().decode().split('=')[1]
    user = User.query.filter_by(username=username).first()
    if user:
        result = {"username": user.username,
                  "password": user.password}
        return jsonify(result)

# 真正完成用户信息修改的api接口
@auth.route('/api/admin/edituser2', methods=['GET','POST'])
def api_admin_edituser2():
    username = request.form['username']
    password = request.form['password']
    if len(password) < 6:
        flash("密码长度不能小于6位")
        return redirect(url_for('auth.usermanage'))
    else:
        user = User.query.filter_by(username=username).first()
        user.password = password
        db.session.commit()
        flash("修改成功")
        return redirect(url_for('auth.usermanage'))

# 删除用户的api接口
@auth.route('/api/admin/deleteuser', methods=['GET','POST'])
def api_admin_deleteuser():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user.user_type == 0:
        result = {"status": 1}
    else:
        db.session.delete(user)
        db.session.commit()
        result = {"status": 0}
    return jsonify(result)

# 获取信息管理页的表格数据
@auth.route('/api/admin/infomanage', methods=['GET','POST'])
def api_admin_infomanage():
    users = User.query.filter_by(user_type=1).all()
    data = []
    i = 0
    for user in users:
        i = i + 1
        # 得到每个用户的信息
        if user.gender == 0:
            gender = '女'
        else:
            gender = '男'
        for p in UserInfoForm.provinces:
            if user.province == p[0]:
                province = p[1]
        data_row = {'sno': i,
                    'username': user.username,
                    'gender': gender,
                    'birth': user.birth.strftime("%Y-%m-%d"),
                    'province': province,
                    'date': user.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(data_row)
    count = len(users)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 模糊查找用户的api接口
@auth.route('/api/admin/searchuser', methods=['GET','POST'])
def api_admin_searchuser():
    option = int(request.form['option'])
    key = request.form['key']
    if option == 1:
        users = User.query.filter(and_(User.username.like('%'+key+'%'),User.user_type==1)).all()
    else:
        if key == '男':
            gender = 1
        else:
            gender = 0
        users = User.query.filter(and_(User.gender==gender, User.user_type == 1)).all()
    data = []
    i = 0
    for user in users:
        i = i + 1
        # 得到每个用户的信息
        if user.gender == 0:
            gender = '女'
        else:
            gender = '男'
        data_row = {'sno': i,
                    'username': user.username,
                    'gender': gender,
                    'birth': user.birth.strftime("%Y-%m-%d"),
                    'province': user.province,
                    'date': user.date.strftime("%Y-%m-%d %H:%M:%S")}
        data.append(data_row)
    count = len(users)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 获取投票话题列表的api接口
@auth.route('/api/admin/votemanage', methods=['GET','POST'])
def api_admin_votemanage():
    votes = Vote.query.all()
    data = []
    i = 0
    for vote in votes:
        i = i + 1
        vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
        choices = ''
        for vote_choice in vote_choices:
            choices = choices + '[ ' + str(vote_choice.code) + ': ' + vote_choice.choice + ' ] '
        if vote.end_time > datetime.now():
            status = '进行中'
        else:
            status = '已截止'
        data_row = {'sno': i,
                    'title': vote.title,
                    'content': vote.content,
                    'choices': choices,
                    'total':vote.total_choice,
                    'max': vote.max_choice,
                    'start_time': vote.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'end_time': vote.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'status': status}
        data.append(data_row)
    count = len(votes)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 模糊查找投票的api
@auth.route('/api/admin/searchvote', methods=['GET','POST'])
def api_admin_searchvote():
    option = int(request.form['option'])
    key = request.form['key']
    if option == 0:
        votes = Vote.query.filter(Vote.title.like('%' + key + '%')).all()
    elif option == 1:
        votes = Vote.query.filter(and_(Vote.title.like('%'+key+'%'),Vote.end_time > datetime.now())).all()
    else:
        votes = Vote.query.filter(and_(Vote.title.like('%' + key + '%'), Vote.end_time < datetime.now())).all()
    data = []
    i = 0
    for vote in votes:
        i = i + 1
        vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
        choices = ''
        for vote_choice in vote_choices:
            choices = choices + '[ ' + str(vote_choice.code) + ': ' + vote_choice.choice + ' ] '
        if vote.end_time > datetime.now():
            status = '进行中'
        else:
            status = '已截止'
        data_row = {'sno': i,
                    'title': vote.title,
                    'content': vote.content,
                    'choices': choices,
                    'total': vote.total_choice,
                    'max': vote.max_choice,
                    'start_time': vote.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'end_time': vote.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'status': status}
        data.append(data_row)
    count = len(votes)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 获取需要修改的用户的信息
@auth.route('/api/admin/editvote', methods=['GET','POST'])
def api_admin_editvote():
    title = request.form['title']
    vote = Vote.query.filter_by(title=title).first()
    if vote:
        result = {"title": vote.title,
                  "end_time": vote.end_time.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify(result)

# 真正完成用户信息修改的api接口
@auth.route('/api/admin/editvote2', methods=['GET','POST'])
def api_admin_editvote2():
    title = request.form['title']
    end_time = request.form['endtime']
    try:
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        vote = Vote.query.filter_by(title=title).first()
        vote.end_time = end_time
        db.session.commit()
        flash("修改成功")
        return redirect(url_for('auth.votemanage'))
    except:
        flash("截止时间格式不正确")
        return redirect(url_for('auth.votemanage'))


# 删除投票话题的api接口
@auth.route('/api/admin/deletevote', methods=['GET','POST'])
def api_admin_deletevote():
    title = request.form['title']
    vote = Vote.query.filter_by(title=title).first()
    if vote:
        db.session.delete(vote)
        db.session.commit()
        vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
        for vote_choice in vote_choices:
            db.session.delete(vote_choice)
            db.session.commit()
        vote_records = VoteRecord.query.filter_by(vote_id=vote.id).all()
        for vote_record in vote_records:
            db.session.delete(vote_record)
            db.session.commit()
        result = {"status": 0}
        return jsonify(result)

# 投票分析->获取柱状图数据
@auth.route('/api/votechoice_record', methods=['GET','POST'])
def api_votechoice_record():
    vote_id = int(request.form['vote_id'])
    vote = Vote.query.filter_by(id=vote_id).first()
    total_choice = vote.total_choice
    choice_records = [0]*total_choice
    vote_records = VoteRecord.query.filter_by(vote_id=vote_id).all()
    for vote_record in vote_records:
        choice_records[vote_record.result-1] = choice_records[vote_record.result-1] + 1
    vote_choices = VoteChoice.query.filter_by(vote_id=vote_id).all()
    choices = []
    for vote_choice in vote_choices:
        choices.append(vote_choice.choice)
    result = {"choices": choices,
              "records": choice_records}
    return jsonify(result)

# 投票分析->获取饼图数据
@auth.route('/api/votegender_record', methods=['GET','POST'])
def api_votegender_record():
    vote_id = int(request.form['vote_id'])
    vote_records = VoteRecord.query.filter_by(vote_id=vote_id).group_by(VoteRecord.user_id).all()
    gender = [0,0]
    for vote_record in vote_records:
        user = User.query.filter_by(id=vote_record.user_id).first()
        if user.gender == 0:
            gender[0] = gender[0] + 1
        else:
            gender[1] = gender[1] + 1
    result = {"gender": gender}
    return jsonify(result)
    return jsonify({"gender": [0,1]})

# 投票分析->获取折线图数据
@auth.route('/api/votegrow_record', methods=['GET','POST'])
def api_votegrow_record():
    vote_id = int(request.form['vote_id'])
    vote = Vote.query.filter_by(id=vote_id).first()
    choices_name = []
    vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
    for vote_choice in vote_choices:
        choices_name.append(vote_choice.choice)
    # 总选项数
    total_choice = vote.total_choice
    # 总天数
    day_num = (vote.end_time - vote.start_time).days + 1
    # 选项序号
    choices = []
    for i in range(1, total_choice + 1):
        choices.append(i)
    # 选项得票数
    choice_records = [0] * total_choice
    # 日期数组
    choice_date_item_date = []
    for i in range(day_num):
        choice_date_item_date.append((vote.start_time + timedelta(days=i)).strftime("%Y-%m-%d"))
    # 当前总票数数组
    choice_date_item_count = [0]*day_num
    # 选项 日期-总票数 字典(注意变量名引用，深拷贝，浅拷贝问题)
    choice_date_count = []
    for i in range(total_choice):
        choice_date_count.append({"date": choice_date_item_date,"count": [0]*day_num})
    vote_records = VoteRecord.query.filter_by(vote_id=vote_id).all()
    for vote_record in vote_records:
        for i in range(len(choice_date_count[vote_record.result-1]["date"])):
            if vote_record.date.strftime("%Y-%m-%d") == choice_date_count[vote_record.result-1]["date"][i]:
                choice_date_count[vote_record.result-1]["count"][i] = choice_date_count[vote_record.result-1]["count"][i] + 1
                break
    # 逐日累加
    choice_date_count2 = []
    for i in range(total_choice):
        choice_date_count2.append({"date": choice_date_item_date, "count": [0] * day_num})
    for j in range(total_choice):
        for i in range(len(choice_date_count[j]["date"])):
            choice_date_count2[j]["count"][i] = sum(choice_date_count[j]["count"][0:i+1])
    count = []
    for i in range(total_choice):
        count.append(choice_date_count2[i]['count'])
    result = {"choices": choices,
              "choices_name":choices_name,
              "date": choice_date_count2[0]['date'],
              "count": count}
    return jsonify(result)

# 投票分析->获取雷达图数据
@auth.route('/api/voteradar_record', methods=['GET','POST'])
def api_votemap_record():
    vote_id = int(request.form['vote_id'])
    vote_records = VoteRecord.query.filter_by(vote_id=vote_id).group_by(VoteRecord.user_id).all()
    # 省份列表
    provinces = []
    # 省份人数列表
    count = []
    for vote_record in vote_records:
        user = User.query.filter_by(id=vote_record.user_id).first()
        if user.province in provinces:
            for i in range(len(provinces)):
                if user.province == provinces[i]:
                    count[i] = count[i] + 1
        else:
            provinces.append(user.province)
            count.append(1)
    # 将省份代码转换成省份名
    for i in range(len(provinces)):
        for item in UserInfoForm.provinces:
            if provinces[i] == item[0]:
                provinces[i] = item[1]
    total_count = 0
    for c in count:
        total_count = total_count + c
    result = {"provinces": provinces,
              "count": count,
              "total_count": total_count}
    return jsonify(result)





########################################## 用户区 #######################################
#                                                                                      #
########################################################################################
# 用户首页
@auth.route('/user', methods=['GET','POST'])
@login_required
def user():
    return render_template('user/index.html',username=current_user.username)

# 用户个人中心页面
@auth.route('/user/userinfo', methods=['GET','POST'])
@login_required
def userinfo():
    form = UserInfoForm()
    user = User.query.filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        birth = datetime.strptime(form.birth.data, '%Y-%m-%d')
        if birth > datetime.now():
            flash('生日不能大于当前年份')
        else:
            user.gender = int(form.gender.data)
            user.birth = birth
            user.province = int(form.province.data)
            if form.old_password.data != '':
                if form.old_password.data != user.password:
                    flash('原始密码不正确')
                    return redirect(url_for('auth.userinfo'))
                elif len(form.new_password.data) < 6:
                    flash('密码长度不能少于6位')
                    return redirect(url_for('auth.userinfo'))
                else:
                    user.password = form.new_password.data
            db.session.commit()
            flash('修改成功')
            return redirect(url_for('auth.userinfo'))
    form.username.data = user.username
    form.gender.data = str(user.gender)
    if user.birth != None:
        form.birth.data = user.birth.strftime('%Y-%m-%d')
    form.province.data = user.province
    return render_template('user/userinfo.html',form=form,username=current_user.username,page_id='1')

# 所有投票信息页面
@auth.route('/user/votelist', methods=['GET','POST'])
@login_required
def votelist():
    form = SearchVoteForm()
    return render_template('user/votelist.html', form=form, username=current_user.username,page_id='2')

# 我的投票页面
@auth.route('/user/myvote', methods=['GET','POST'])
@login_required
def myvote():
    form = SearchVoteForm()
    return render_template('user/myvote.html',form=form,username=current_user.username,page_id='3')

# 投票分析页面
@auth.route('/user/voteanalys', methods=['GET','POST'])
@login_required
def voteanalys2():
    form = VoteAnalysForm()
    votes = Vote.query.all()
    form_choices = []
    for vote in votes:
        if VoteRecord.query.filter(and_(VoteRecord.vote_id==vote.id,VoteRecord.user_id==current_user.id)).all() and vote.end_time < datetime.now():
            form_choices.append((str(vote.id), vote.title + '（已截止，我已参与）'))
        elif VoteRecord.query.filter(and_(VoteRecord.vote_id==vote.id,VoteRecord.user_id==current_user.id)).all():
            form_choices.append((str(vote.id), vote.title+'（我已参与）'))
        elif vote.end_time < datetime.now():
            form_choices.append((str(vote.id), vote.title+'（已截止，未参与）'))
    form.titles.choices = form_choices
    vote_id = session.get('vote_id')
    if vote_id == None:
        vote_id = 1
    if request.method == "POST":
        vote_id = form.titles.data
        session['vote_id'] = int(vote_id)
        return redirect(url_for('auth.voteanalys2'))
    form.titles.data = str(vote_id)
    return render_template('user/voteanalys.html', form=form, vote_id=vote_id, username=current_user.username,page_id='4')

# 投票iframe子页面（点击投票后弹出的页面）
@auth.route('/user/dovote/<title>', methods=['GET','POST'])
@login_required
def dovote(title):
    if request.method == "GET":
        vote = Vote.query.filter_by(title=title).first()
        total_choice = vote.total_choice
        max_choice = vote.max_choice
        vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
        choices = []
        for vote_choice in vote_choices:
            choices.append(vote_choice.choice)
        return render_template('user/dovote.html', title=vote.title, content=vote.content,
                               total_choice=total_choice, max_choice=max_choice, choices=choices)
    else:
        vote = Vote.query.filter_by(title=title).first()
        vote_records = VoteRecord.query.filter(and_(VoteRecord.user_id==current_user.id,VoteRecord.vote_id==vote.id)).all()
        if vote_records:
            flash('您已参加过此投票，不能再投')
            return redirect(url_for('auth.dovote',title=title))
        if vote.max_choice == 1:
            choice = request.form['schoice']
            new_record = VoteRecord(user_id=current_user.id,vote_id=vote.id,result=choice,date=datetime.now())
            db.session.add(new_record)
            db.session.commit()
        else:
            count = 0
            # 判断选项有没有超过最大可选数
            for i in range(vote.total_choice):
                index = 'mchoice' + str(i+1)
                try:
                    if request.form[index] == 'on':
                        count = count + 1
                except:
                    pass
            if count > vote.max_choice:
                flash('您的选项不能超过' + str(vote.max_choice) + '个')
                return redirect(url_for('auth.dovote', title=title))
            for i in range(vote.total_choice):
                index = 'mchoice' + str(i+1)
                try:
                    if request.form[index] == 'on':
                        new_record = VoteRecord(user_id=current_user.id, vote_id=vote.id,
                                                result=i+1, date=datetime.now())
                        db.session.add(new_record)
                        db.session.commit()
                except:
                    pass
        flash('投票成功')
        return redirect(url_for('auth.dovote',title=title))

# 投票结果详情iframe子页面（点击详情后弹出的页面）
@auth.route('/user/voteresult/<title>', methods=['GET','POST'])
@login_required
def voteresult(title):
    vote = Vote.query.filter_by(title=title).first()
    if vote.end_time > datetime.now():
        status = 0
    else:
        status = 1
    vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
    my_records = VoteRecord.query.filter(and_(VoteRecord.user_id==current_user.id,VoteRecord.vote_id==vote.id)).all()
    choices = []
    mychoices = []
    for vote_choice in vote_choices:
        choices.append(vote_choice.choice)
    for my_record in my_records:
        mychoices.append(choices[my_record.result-1])
    return render_template('user/voteresult.html', title=vote.title, content=vote.content,
                           choices=choices, mychoices=mychoices, status=status)

################################### api ################################
# 我的投票列表的api接口
@auth.route('/api/user/myvote', methods=['GET','POST'])
def api_user_myvote():
    my_records = VoteRecord.query.filter_by(user_id=current_user.id).group_by(VoteRecord.vote_id).all()
    data = []
    i = 0
    for my_record in my_records:
        vote = Vote.query.filter_by(id=my_record.vote_id).first()
        i = i + 1
        vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
        choices = ''
        for vote_choice in vote_choices:
            choices = choices + '[ ' + str(vote_choice.code) + ': ' + vote_choice.choice + ' ] '
        if vote.end_time > datetime.now():
            status = '进行中'
        else:
            status = '已截止'
        data_row = {'sno': i,
                    'title': vote.title,
                    'content': vote.content,
                    'choices': choices,
                    'total':vote.total_choice,
                    'max': vote.max_choice,
                    'start_time': vote.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'end_time': vote.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'status': status}
        data.append(data_row)
    count = len(my_records)
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)

# 获取当前投票状态的api接口
@auth.route('/api/user/currentvote', methods=['GET','POST'])
def api_user_currentvote():
    title = request.form['title']
    vote = Vote.query.filter_by(title=title).first()
    if vote:
        if vote.end_time > datetime.now():
            result = {"status": 0}
        else:
            result = {"status": 1}
        return jsonify(result)

# 模糊查找用户投票的api接口
@auth.route('/api/user/searchvote', methods=['GET','POST'])
def api_user_searchvote():
    option = int(request.form['option'])
    key = request.form['key']
    my_records = VoteRecord.query.filter_by(user_id=current_user.id).group_by(VoteRecord.vote_id).all()
    data = []
    i = 0
    for my_record in my_records:
        if option == 0:
            vote = Vote.query.filter(and_(Vote.id==my_record.vote_id,Vote.title.like('%' + key + '%'))).first()
            if vote:
                i = i + 1
                vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
                choices = ''
                for vote_choice in vote_choices:
                    choices = choices + '[ ' + str(vote_choice.code) + ': ' + vote_choice.choice + ' ] '
                if vote.end_time > datetime.now():
                    status = '进行中'
                else:
                    status = '已截止'
                data_row = {'sno': i,
                            'title': vote.title,
                            'content': vote.content,
                            'choices': choices,
                            'total': vote.total_choice,
                            'max': vote.max_choice,
                            'start_time': vote.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'end_time': vote.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'status': status}
                data.append(data_row)
        elif option == 1:
            vote = Vote.query.filter(and_(Vote.id==my_record.vote_id,Vote.title.like('%' + key + '%'),Vote.end_time > datetime.now())).first()
            if vote:
                i = i + 1
                vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
                choices = ''
                for vote_choice in vote_choices:
                    choices = choices + '[ ' + str(vote_choice.code) + ': ' + vote_choice.choice + ' ] '
                if vote.end_time > datetime.now():
                    status = '进行中'
                else:
                    status = '已截止'
                data_row = {'sno': i,
                            'title': vote.title,
                            'content': vote.content,
                            'choices': choices,
                            'total': vote.total_choice,
                            'max': vote.max_choice,
                            'start_time': vote.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'end_time': vote.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'status': status}
                data.append(data_row)
        else:
            vote = Vote.query.filter(and_(Vote.id==my_record.vote_id,Vote.title.like('%' + key + '%'),Vote.end_time < datetime.now())).first()
            if vote:
                i = i + 1
                vote_choices = VoteChoice.query.filter_by(vote_id=vote.id).all()
                choices = ''
                for vote_choice in vote_choices:
                    choices = choices + '[ ' + str(vote_choice.code) + ': ' + vote_choice.choice + ' ] '
                if vote.end_time > datetime.now():
                    status = '进行中'
                else:
                    status = '已截止'
                data_row = {'sno': i,
                            'title': vote.title,
                            'content': vote.content,
                            'choices': choices,
                            'total': vote.total_choice,
                            'max': vote.max_choice,
                            'start_time': vote.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'end_time': vote.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                            'status': status}
                data.append(data_row)
    count = i
    result = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": data
    }
    return jsonify(result)
