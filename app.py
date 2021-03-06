import json
import os
import random
import time

import MySQLdb
import requests
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

    newsid = db.Column(db.Integer, nullable=False, primary_key=True)
    comment_detail=db.Column(db.String(255),nullable=False)
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
class videos(db.Model):
    __tablename__='video'
    Videonumber=db.Column(db.Integer,nullable=False,primary_key=True)
    Videotitle=db.Column(db.String(255))
    Videocontent=db.Column(db.String(255))
    Videourl=db.Column(db.String(1024))
    Videocount=db.Column(db.Integer)
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

db.create_all()
def get_json(url,num):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    params = {
        'page_size': 10,
        'next_offset':str(num),
        'tag': '今日热门',
        'platform': 'pc'
    }

    try:
        html = requests.get(url, params=params, headers=headers)
        return html.json()

    except BaseException:
        print('request error')
        pass
def bilibiliget():
    for i in range(10):
        url = 'http://api.vc.bilibili.com/board/v1/ranking/top?'
        num = i * 10 + 1
        html = get_json(url, num)
        infos = html['data']['items']
        for info in infos:
            title = info['item']['description']  # 小视频的标题
            video_url = info['item']['video_playurl']  # 小视频的下载链接
            videomaxid = findvideomaxid()
            videomaxiddetail = videomaxid[0][0]
            videomaxiddetail = videomaxiddetail + 1
            insertvideo = videos(Videonumber=videomaxiddetail, Videotitle=title, Videourl=video_url, Videocontent=title,
                                 Videocount=0)

            try:
                db.session.add(insertvideo)
                db.session.commit()
                print("over")
            except:
                db.rollback()
                print("insert error")

        time.sleep(int(format(random.randint(2, 8))))  # 设置随机等待时间
@app.route('/bilibili',methods=['GET','POST'])
def bilibili():
    bilibiliget()
    return "ok"
@app.route('/',methods=['GET'])
def sqllink():
    # 建立数据库连接
    new_detail=db.session.query(news).all()
    result=[]
    for row in new_detail:
        result.append(row.to_json())

    return jsonify(result)

@app.route('/video',methods=['GET','POST'])
def videolink():
    videolist= db.session.query(videos).all()
    result = []
    for row in videolist:
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
@app.route('/findnews',methods=['GET','POST'])
@login_required
def findnews():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='zys9970304', db='wechat', charset='utf8')
    cur = conn.cursor()
    inputdata = request.values.get("typesdesign")
    sql = "select * from newstwo "
    cur.execute(sql)
    u = cur.fetchall()
    conn.close()
    return render_template("findnews.html")

@app.route('/findvideo',methods=['GET','POST'])
@login_required
def findvideo():
    return render_template("findvideo.html")

@app.route('/design',methods=['GET','POST'])
@login_required
def design():
    conn=pymysql.connect(host='127.0.0.1',user='root',password='zys9970304',db='wechat',charset='utf8')
    cur=conn.cursor()
    type_design=request.values.get("typesdesign")
    sql="select * from newstwo"
    cur.execute(sql)
    u=cur.fetchall()
    conn.close()
    return render_template("design.html",u=u)

@app.route('/videotest',methods=['GET','POST'])
@login_required
def videotest():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='zys9970304', db='wechat', charset='utf8')
    cur = conn.cursor()
    sql = "select  * from video"
    cur.execute(sql)
    u = cur.fetchall()
    conn.close()
    return render_template("video.html",u=u)
global updatechageid
@app.route('/updatenews/<id>',methods=['GET','POST'])
@login_required
def updatenews(id):
        updateid=id
        global updatechageid
        updatechageid=id
        conn = pymysql.connect(host='127.0.0.1', user='root', password='zys9970304', db='wechat', charset='utf8')
        cur = conn.cursor()
        sql = "select * from newstwo where NewsID ={}".format(updateid)
        cur.execute(sql)
        u = cur.fetchall()
        conn.close()
        title = request.form.get("title")
        author = request.form.get("author")
        img = request.form.get("smallimg")
        content = request.form.get("content")
        if (title!=None):
            obj = news.query.filter(news.NewsID == updatechageid).first()
            obj.title = title
            obj.NewsTittle = title
            obj.CoverImage = img
            obj.NewsContent = content
            obj.AuthorName = author
            db.session.commit()
            print (updatechageid)
            print ("修改ok")
        print(u)
        return render_template("update.html",u=u)
@app.route('/updatechage',methods=['GET','POST'])
@login_required
def updatechage():

    title = request.form.get("title")
    author = request.form.get("author")
    img = request.form.get("smallimg")
    content = request.form.get("content")
    obj = news.query.filter(news.NewsID == updatechageid).first()
    obj.title =title
    obj.NewsTittle=title
    obj.CoverImage=img
    obj.NewsContent=content
    obj.AuthorName=author
    db.session.commit()
    print (updatechageid)
    print ("修改ok")
    return render_template("design.html")

@app.route('/deleteget',methods=['GET',"POST"])
@login_required
def deleteget():
    deleteid=request.form.get("id")
    newsdelete = news.query.get(deleteid)
    db.session.delete(newsdelete)
    db.session.commit()
    return "ok"
@app.route('/videodeleteget',methods=['GET','POST'])
@login_required
def videodeleteget():
    videodeleteid=request.form.get("id")
    videosdelete=videos.query.get(videodeleteid)
    db.session.delete(videosdelete)
    db.session.commit()
    print("删除over")
    return "ok"
@app.route('/system')
@login_required
def system():
    return render_template("system.html")

def findmaxid():
    conn=pymysql.connect(host='127.0.0.1',user='root',password='zys9970304',db='wechat',charset='utf8')
    cur=conn.cursor()
    sql=" select NewsID from newstwo where NewsID=(select max(NewsID) from newstwo)"
    cur.execute(sql)
    u=cur.fetchall()
    print(u)
    conn.close()
    return u
def findvideomaxid():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='zys9970304', db='wechat', charset='utf8')
    cur = conn.cursor()
    sql = " select Videonumber from video where Videonumber=(select max(Videonumber) from video)"
    cur.execute(sql)
    u = cur.fetchall()
    print(u)
    conn.close()
    return u
def findcommentminumber():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='zys9970304', db='wechat', charset='utf8')
    cur = conn.cursor()
    sql = " select commentnumber from commentstore where commentnumber=(select max(commentnumber) from commentstore)"
    cur.execute(sql)
    u = cur.fetchall()
    print(u)
    conn.close()
    return u
@app.route('/insert',methods=['GET',"POST"])
@login_required
def insert():
    types=request.values.get("types")
    title=request.form.get("title")
    author=request.form.get("author")
    img=request.form.get("smallimg")
    content=request.form.get("content")
    if(types=='xinwen'):
        maxid = findmaxid()
        maxnewsid = maxid[0][0]
        maxnewsid = maxnewsid + 1
        insertnews=news(AdminID="1",AuthorName=author,CoverImage=img,Creattime="20190507",NewsContent=content,NewsID=maxnewsid,NewsTittle=title,NewsType="1",ReadCount=0)
        db.session.add(insertnews)
        db.session.commit()
    if(types=='shipin'):
        videomaxid=findvideomaxid()
        videomaxiddetail=videomaxid[0][0]
        videomaxiddetail=videomaxiddetail+1
        insertvideo=videos(Videonumber=videomaxiddetail,Videotitle=title,Videourl=img,Videocontent=content,Videocount=0)
        db.session.add(insertvideo)
        db.session.commit()
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

@app.route('/getcomment/<id>/<commentfromwechat>')
def getcomment(id,commentfromwechat):
    #insertnumber=findcommentminumber();
    #print(insertnumber)
    insertcomment = comment(newsid=id,comment_detail=commentfromwechat)
    db.session.add(insertcomment)
    db.session.commit()
    return "ok"
@app.route('/forcomment',methods=['GET','POST'])
def forcomment():
    comment_detail = db.session.query(comment).all()
    result = []
    for row in comment_detail:
        result.append(row.to_json())

    return jsonify(result)
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