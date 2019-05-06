import json
import os

import MySQLdb
from flask.json import jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, fresh_login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, current_app, render_template, request
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import *
import config
import pymysql
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, redirect, url_for, flash, abort
#from flask.ext.login import (LoginManager, UserMixin, login_user, logout_user,
                            #current_user, login_required, fresh_login_required)
app = Flask(__name__)
bootstrap=Bootstrap(app)
basedir = os.path.abspath(os.path.dirname(__file__))
login_manager = LoginManager(app)
# 设置登录视图的名称，如果一个未登录用户请求一个只有登录用户才能访问的视图，
# 则闪现一条错误消息，并重定向到这里设置的登录视图。
# 如果未设置登录视图，则直接返回401错误。
login_manager.login_view = 'login'
# 设置当未登录用户请求一个只有登录用户才能访问的视图时，闪现的错误消息的内容，
# 默认的错误消息是：Please log in to access this page.。
login_manager.login_message = 'Unauthorized User'
# 设置闪现的错误消息的类别
login_manager.login_message_category = "info"

users = [
    {'username': 'root', 'password': '123'},
    {'username': 'ting', 'password': '123'}
]

app.config.from_object(config)
db=SQLAlchemy(app)

class news(db.Model):
    __tablename__='newstwo'
    AdminID=db.Column(db.Integer,nullable=False)
    AuthorName=db.Column(db.String(255),nullable=False)
    CoverImage=db.Column(db.String(255),nullable=False)
    Creattime=db.Column(db.String(255),nullable=False)
    NewsContent=db.Column(db.String(255),nullable=False)
    NewsID=db.Column(db.Integer,primary_key=True,autoincrement=True,nullable=False)
    NewsTittle=db.Column(db.String(255),nullable=False)
    NewsType=db.Column(db.String(255),nullable=False)
    ReadCount=db.Column(db.Integer,nullable=False)
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
class comment(db.Model):
    __tablename__='commentstore'
    id=db.Column(db.Integer,nullable=False,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    reply_comment_id=db.Column(db.Integer,nullable=False)
    comment_detail=db.Column(db.String(255),nullable=False)
    insert_time=db.Column(db.Time,nullable=False)
    source_id=db.Column(db.Integer,nullable=False)
    username=db.Column(db.String(255),nullable=True)
    reply_user_name=db.Column(db.String(255),nullable=True)



db.create_all()

@app.route('/',methods=['GET'])
def sqllink():
    # 建立数据库连接
    new_detail=db.session.query(news).all()
    result=[]
    for row in new_detail:
        result.append(row.to_json())
    return jsonify(result)


def return_img_stream(img_local_path):
    """
    工具函数:
    获取本地图片流
    :param img_local_path:文件单张图片的本地绝对路径
    :return: 图片流
    """
    import base64
    img_stream = ''
    with open(img_local_path, 'r') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream)
    return img_stream
'''
下面后台管理网站的设置
'''
@app.route('/design')
@login_required
def design():
    conn=pymysql.connect(host='127.0.0.1',user='root',password='zys9970304',db='wechat',charset='utf8')
    cur=conn.cursor()
    sql="select * from newstwo"
    cur.execute(sql)

    u=cur.fetchall()
    print(u)
    conn.close()
    return render_template("design.html",u=u)

@app.route('/system')
@login_required
def system():
    return render_template("system.html")

@app.route('/insert',methods=['GET',"POST"])
@login_required
def insert():
    types=request.values.get("types")
    print(types)
    title=request.form.get("title")
    author=request.form.get("author")
    img=request.form.get("smallimg")
    content=request.form.get("content")
    return render_template("insert.html")

class User(UserMixin):
    pass

# 通过用户名，获取用户记录，如果不存在，则返回None
def query_user(username):
    for user in users:
        if user['username'] == username:
            return user

# 如果用户名存在则构建一个新的用户类对象，并使用用户名作为ID
# 如果不存在，必须返回None
@login_manager.user_loader
def load_user(username):
    if query_user(username) is not None:
        curr_user = User()
        curr_user.id = username
        return curr_user
    # Must return None if username not found

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/indexhoutai')
@login_required
def index():
    return render_template('indexhoutai.html')

@app.route('/home')
@fresh_login_required
def home():
    return 'Logged in as: %s' % current_user.get_id()

@app.route('/index',methods=["GET","POST"])
def form():
    if request.method == 'POST':
        username = request.form.get('fullname')
        user = query_user(username)
        print(username)
        # 验证表单中提交的用户名和密码
        if user is not None and request.form['fullpassword'] == user['password']:
            curr_user = User()
            curr_user.id = username

            # 通过Flask-Login的login_user方法登录用户
            login_user(curr_user, remember=True)

            # 如果请求中有next参数，则重定向到其指定的地址，
            # 没有next参数，则重定向到"index"视图
            next = request.args.get('next')
            return redirect(next or url_for('index'))
            #return render_template('hello.html')
        flash('Wrong username or password!')
    # GET 请求
    return render_template('index.html')

app.secret_key = '1234567'
if __name__ == '__main__':
    app.run(debug=True)