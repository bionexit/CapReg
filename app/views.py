# -*- coding: utf-8 -*-

from app import app, db, models
from flask import render_template, flash, redirect, Blueprint, url_for, request, session
from .forms import *
from flask_login import current_user, login_required, login_user, logout_user,login_manager
import datetime
from app.extension.utils import redirect_back
from sqlalchemy import and_

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'warning')


@app.route('/')
@app.route('/index')
@login_required
def index(page=None):
    # user = {'nickname': 'Miguel'}# fake user
    # posts = [  # fake array of posts
    #     {
    #         'author': {'nickname': 'John'},
    #         'body': 'Beautiful day in Portland!'
    #     },
    #     {
    #         'author': { 'nickname': 'Susan' },
    #         'body': 'The Avengers movie was so cool!'
    #     }
    # ]
    #
    # ses = session.get('username')
    # return render_template("index.html",
    #     title='主页',
    #     user=ses,
    #     posts=posts)
    return redirect(url_for("posts"))


@app.route('/login',methods=['GET', 'POST'])
def login():
    import app.extension.api as ext  # 外部接口查询
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data.strip().lower()).first()
        user_has_password_bol = False
        if user is not None:  # 数据库中有用户名数据
            try:
                if (user.verify_password(form.password.data)):
                    user_has_password_bol = True
            except:
                pass
            if user_has_password_bol:  # 检查用户密码是否匹配

                if user._role.name == 'Administrator':
                    flash('管理員登录成功', 'info')
                    session['admin'] = True
                    login_user(user, form.remember_me.data)
                    session['username'] = user.username
                    return redirect(url_for('index'))
                else:
                    if app.config['ALLOW_LOCAL_USER_LOGIN']:
                        login_user(user, form.remember_me.data)
                        session['username'] = user.username
                        flash('普通用戶登录成功', 'info')
                        return redirect(request.args.get('next') or url_for('index'))
                    else:
                        flash('不允许内部用户登陆，请联系管理员', 'warning')
            else:
                result = ext.tradesysauth(username=form.username.data,password=form.password.data)
                if result is True:
                    login_user(user, form.remember_me.data)

                    # 读取当前可用数量[vlue_usble] def value,
                    value_usble = 0
                    print(user.username)
                    value_usble = []
                    value_usble = ext.tradesysvalue(username=form.username.data.strip().lower())
                    value_insert = value_usble[0]['postvalue']
                    print(value_insert)
                    user.value_usble = value_insert
                    db.session.commit()
                    # db.session.close()

                    flash('普通用戶外部記錄登录成功', 'info')
                    session['value_usble'] = value_usble
                    # session['username'] = user.username

                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    flash('密码错误', 'warning')

        else:
            result = ext.tradesysauth(username=form.username.data,password=form.password.data)
            # 从持仓库中查询是否有持仓记录
            if result is True:
                userinitinfo = ext.tradesysvalue(form.username.data)
                add_user = models.User(username=form.username.data.strip().lower(),reg_date=datetime.datetime.now(),
                                       phone=userinitinfo[0]['phone']+'abc',
                                       contact_name=userinitinfo[0]['contact_name'],
                                       trade_num=userinitinfo[0]['trade_num'],
                                       value_usble=userinitinfo[0]['postvalue'],)
                db.session.add(add_user)
                db.session.commit()
                # db.session.close()
                flash('首次登陆成功并完成数据同步，请重新登陆', 'info')
                return redirect(url_for('login'))
            else:
                flash('密码错误', 'warning')
    if current_user.is_authenticated is not True:
        return render_template('login.html',title='登陆', form = form)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/get/')
@login_required
def get():
    return session.get('admin')


@app.route('/postreq',methods=['GET', 'POST'])
@login_required
def postreq():
    form = PostForm()
    useble_value = 0
    post_amount = 0
    avalibe_value =0
    if form.postdirection.data == '1':
        postdirection=True
    else:
        postdirection=False
    if form.validate_on_submit():
        pyt = models.PostType.query.filter_by(description='发布中').first()
        post_req = models.Posts(userid=current_user.id, start_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                end_date=(datetime.datetime.now() + datetime.timedelta(days=+int(form.lasting_days.data))).strftime("%Y-%m-%d %H:%M:%S"),
                                post_value=form.postvalue.data, status=1, post_direction=postdirection,
                                posttypename=pyt,remark=form.remark.data)
        print(form.postdirection.data)
        db.session.add(post_req)
        db.session.commit()
        # db.session.close()
        flash('发布成功', 'info')
        return redirect(url_for('index'))
    else:
        try:
            flash_errors(form)
            useble_value = current_user.value_usble
            sqlstr = "select sum(posts.post_value) as pvsum from posts where posts.post_direction=0 and posts.status=1 and posts.post_type_id in (1,2) and posts.userid=" + str(
                current_user.id)
            x = db.engine.execute(sqlstr).first()
            # db.session.close()
            post_amount = x.values()[0]
            if post_amount is None:
                post_amount = 0
            avalibe_value = float(useble_value)-float(post_amount)
        except:
            pass
        print(useble_value,post_amount,avalibe_value)
    return render_template('newpost.html', title='需求发布', form=form,
                           direction_providers=app.config['POST_DIRECTION'], useble_value=useble_value, post_amount=post_amount, avalibe_value=avalibe_value)

@app.route('/postlist')
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POST_SHOW_PER_PAGE']
    pagination = models.Posts.query.filter(and_(models.Posts.status==1,models.Posts.post_type_id.in_([1, 2]))).order_by(models.Posts.start_date.desc()).paginate(page, per_page=per_page)
    postss = pagination.items
    #print(current_user._role.name=='User')
    return render_template('postslist.html', pagination=pagination, posts=postss,title='需求列表')



@app.route('/mypost')
@login_required
def myposts():
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POST_SHOW_PER_PAGE']
    pagination = models.Posts.query.filter(and_(models.Posts.userid==current_user.id,models.Posts.status==1)).order_by(models.Posts.start_date.desc()).paginate(page, per_page=per_page)
    postss = pagination.items
    #print(current_user._role.name=='User')
    return render_template('postslist.html', pagination=pagination, posts=postss,title='我的需求')


@app.route('/post/<int:post_id>/view', methods=['GET', 'POST'])
def show_post(post_id):
    post = models.Posts.query.get_or_404(post_id)
    return render_template('post.html',post=post,title="需求详情:"+str(post.id))


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = models.Posts.query.get_or_404(post_id)
    try:
        if (current_user.id == post.userid or current_user._role.permissions ==1) and (post.post_type_id ==1 or post.post_type_id ==2):

            post.status = False
            post.deal_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()
            flash('删除成功.', 'success')
            return redirect_back()
        else:
            flash('没有权限.', 'warning')
            return redirect_back()
    except:
        flash('权限异常.', 'warning')
        redirect(url_for('index'))

@app.route('/post/<int:post_id>/<int:status_id>/change', methods=['POST'])
@login_required
def post_status_change(post_id,status_id):
    post = models.Posts.query.get_or_404(post_id)
    try:
        if current_user.id == post.userid or current_user._role.permissions ==1:
            post.post_type_id = status_id
            post.deal_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()
            flash('操作成功', 'success')
            return redirect_back()
        else:
            flash('没有权限.', 'warning')
            return redirect_back()
    except:
        flash('权限异常.', 'warning')
        redirect(url_for('index'))



@app.route('/myinfo', methods=['GET'])
@login_required
def myinfo():
    return render_template('myinfo.html',title='我的信息')


@app.route('/admin/<int:user_id>/usersync', methods=['POST'])
@login_required
def adminsync(user_id):
    pass