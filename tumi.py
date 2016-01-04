#! /usr/bin/env python
# -*- coding:utf8 -*-

import MySQLdb
import json
import os
import sys

from qiniu import Auth

from modules.api import *
from modules.dbm import DBM

from flask import Flask, g, request, render_template, abort, jsonify, send_from_directory

app = Flask(__name__)
app.debug = True

# 七牛凭证管理
access_key = 'Zxk6nc0R0YImqHtvK51PuwA0nKuOdsaaCCCa-HFF'
secret_key = '8wfzQs-lqnOb8C_ZJ6Q8Kju2TAI1S57t47gXP8Q2'
qn_auth = Auth(access_key, secret_key)

# 常量
bucket_name = 'tumi'
server_host = 'http://p2p2.sinaapp.com'
callback_url = '/images/add'

def get_db_config():
    from sae.const import MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_PORT, MYSQL_DB
    return {
        "host": MYSQL_HOST,
        "user": MYSQL_USER,
        "passwd": MYSQL_PASS,
        "port": int(MYSQL_PORT),
        "db": MYSQL_DB,
        "charset": "utf8"
    }


def init_db():
    db_conf = get_db_config()
    db = DBM().connect(**db_conf)
    cursor = g.db.cursor()

    cursor.execute("""create table if not exists `images`(
            image_id int auto_increment primary key,
            user_id varchar(64) not NULL,
            title varchar(64) not NULL default "",
            detail varchar(256) not NULL default "",
            pic_url varchar(128) not NULL,
            pros int not NULL default 0,
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
           ) engine=MyISAM character set utf8""")

    # disconnect from server
    db.close()


@app.before_request
def before_request():
    db_conf = get_db_config()
    g.db = DBM().connect(**db_conf)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/images/get')
def get_image():
    try:
        user = request.args.get('user_id')
        cursor = g.db.get_cursor()

        # 使用fetchall函数，将结果集（多维元组）存入rows里面
        sql = "SELECT image_id, user_id, title ,detail, pic_url, pros, create_time FROM images WHERE share =  1 "
        if user is not None:
            sql += "AND user_id =" + MySQLdb.escape_string(user);
        sql += " ORDER BY create_time desc"
        cursor.execute(sql)
        rows = cursor.fetchall()

        # 依次遍历结果集，发现每个元素，就是表中的一条记录，用一个元组来显示
        keys = 'image_id user_id title detail pic_url pros create_time'.split(' ')

        result = []
        for row in rows:
            item = dict(zip(keys, row))
            item['create_time'] = item['create_time'].strftime('%F %T')
            result.append(item)
        result = Result(result=result)
    except Exception, e:
        result = Result(error=-1, err_msg=str(e))
    return jsonify(result.asDict())


@app.route('/images/dianzan')
def pro_image():
    try:
        image_id = request.args.get('image_id')
        if(image_id is None):
            result = Result(error=-1, err_msg="image_id is none")
        else:
            cursor = g.db.get_cursor()
          
            sql = "UPDATE images set pros=pros+1 WHERE image_id = '%s' " % MySQLdb.escape_string(image_id);
            cursor.execute(sql)
            result = Result(error=0)       
    except Exception, e:
        result = Result(error=-1, err_msg=str(e))
    return jsonify(result.asDict())


@app.route('/images/add', methods=['GET', 'POST'])
def add_image():
    try:
        if request.method == 'POST':
            user_id = request.values.get('user_id')
            title = request.values.get('title')
            pic_url = request.values.get('pic_url')
            share = request.values.get('share', default = '0')
        else:
            user_id = request.args.get('user_id')
            title = request.args.get('title')
            pic_url = request.args.get('pic_url')
            share = request.args.get('share', default = '0')
        g.db.get_cursor().execute(
            "INSERT INTO images(user_id,title,pic_url,share) VALUES('%s','%s','%s',%s)" % 
            (MySQLdb.escape_string(user_id), MySQLdb.escape_string(title), 
                MySQLdb.escape_string(pic_url), MySQLdb.escape_string(share))
        )
        result = Result(pic_url=pic_url)
    except Exception, e:
        result = Result(error=-1, err_msg=str(e))
    return jsonify(result.asDict())

@app.route('/post')
def post():
    user_id = request.values.get('user_id')
    pic_url = request.values.get('pic_url')
    title = request.values.get('title')
    if None in (user_id, pic_url, title):
        abort(404)
    return render_template('post.html', user_id=user_id, pic_url=pic_url, title=title)

@app.route('/')
@app.route('/ground')
def index():
    return send_from_directory('templates', 'tumi.html')

@app.route('/api/get_upload_token')
def get_upload_token():
    try:
        token = qn_auth.upload_token(
            bucket_name, None, 7200,
            {
                'callbackUrl': server_host + callback_url,
                'callbackBody': "name=$(fname)&hash=$(etag)&user_id=$(x:user_id)\
                &title=$(x:title)&pic_url=$(x:pic_url)&share=$(x:share)"
            }
        )
        result = Result(token=token)
    except Exception, e:
        result = Result(error=-1, err_msg=str(e))
    return jsonify(result.asDict())


if __name__ == '__main__':
    import sys
    reload(sys)
    app.run()