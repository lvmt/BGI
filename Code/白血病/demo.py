#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author lvmengting
# @Time   2020/12/24 15:17
# @Email  13554221497@163.com
# @File   demo.py


"""
测试装饰器的使用
"""


import datetime
import time


def logger(func):
    def wrapper(self, *args, **kwargs):
        print('=={}==, 程序开始时间: {}'.format(func.__name__,  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        result = func(self, *args, **kwargs)
        print('=={}==, 程序结束时间: {}'.format(func.__name__, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        return result
    return wrapper


class Demo:

    @logger
    def add(self, a, b):
        return a + b


print(Demo().add(5, 6))