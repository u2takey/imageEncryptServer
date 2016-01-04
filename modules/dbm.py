#! /usr/bin/env python
#-*- coding: utf-8 -*-

import json
import re

try:
    import MySQLdb as mysql
except Exception, e:
    import pymysql as mysql


class DBM(object):
    def __init__(self):
        self.conn = None
        self._opts = None

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def connect(self, **kwargs):
        self._opts = kwargs
        return self.reconnect()

    def reconnect(self):
        if self._opts is None:
            raise Exception('Mysql options has not been set yet')
        self.conn = mysql.connect(**self._opts)
        return self

    def get_cursor(self):
        if self.conn is None:
            raise Exception("Not yet connected to a database")
        try:
            if not self.conn.ping():
                self.reconnect()
        except Exception as e:
            self.reconnect()
        return self.conn.cursor()

    def query(self, sql, values, get_raw_data=False):
        cursor = self.get_raw_cursor()
        cursor.execute('SET SESSION QUERY_CACHE_TYPE = 0;')
        cursor.execute(sql, values)

        data = cursor.fetchall()
        cursor.close()
        if get_raw_data:
            return data
        return self.insure_jsonifyable(data)



