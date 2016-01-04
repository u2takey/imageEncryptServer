#! /usr/bin/env python
#-*- coding: utf-8 -*-

import os
import json
import time
import re
import threading
import string

class Result(object):
    def __init__(self, error=0, err_msg='', **kwargs):
        self.error = error
        self.err_msg = err_msg
        self.__dict__.update(kwargs)
        self._keys = kwargs.keys()

    def asDict(self):
        tmp = {}
        for k in self._keys + ["error", "err_msg"]:
            tmp[k] = self.__dict__[k]
        return tmp

    def __str__(self):
        return json.dumps(self.asDict())

