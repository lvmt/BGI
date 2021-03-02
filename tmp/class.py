#!/usr/bin/python
# -*- coding:utf-8 -*-

#  构造函数的继承
#
# class Father:
#     def __init__(self):
#         print('Father')
#
# class Son(Father):
#     def __init__(self):
#         print('son')
#         #  super(Son, self).__init__()  #  子类
#         super().__init__()
#
# son = Son()
#
#
# class GrandFather:
#     def __init__(self):
#         print('GrandFather')
#
#
# class Father(GrandFather):
#     def __init__(self):
#         print('Father')
#
# class Son(Father):
#     def __init__(self):
#         print('son')
#         super(Son, self).__init__()
#         print('准备绕过父亲')
#         super(Father, self).__init__()  # 实际调用的是Father的父亲.
#
# s = Son()


#
# class A:
#     def __init__(self, age):
#         self.age = age
#
# class B(A):
#     def __init__(self, age, name):
#         super(B, self).__init__(age)
#         self.name = name
#
# b = B(12, 'mike')
# print(b.__dict__)


#  子类不重写__init__方法, 实例化子类时, 会自动调用父类定义的__init__
#
# class Father:
#     def __init__(self, name):
#         self.name = name
#         print('name: {}'.format(self.name))
#
#     def getName(self):
#         return 'Father ' + self.name
#
#
# class Son(Father):  # 直接继承,
#     def getName(self):
#         return 'Son: ' + self.name
#
# s = Son('mike')
# print(s.getName())


"""
重写了__init__ 时，实例化子类，就不会调用父类已经定义的 __init__，语法格式如下
"""
#
# class Father:
#     def __init__(self, name):
#         self.name = name
#         print('name: {}'.format(self.name))
#
#     def getName(self):
#         return 'Father ' + self.name
#
#
# class Son(Father):
#     def __init__(self, name):
#         print('Hi')
#         self.name = name
#
#     def getName(self):
#         return 'Son ' + self.name
#
#
# s = Son('mike')
# print(s.getName())


"""
如果重写了__init__ 时，要继承父类的构造方法，可以使用 super 关键字：
super(子类，self).__init__(参数1，参数2，....)
父类名称.__init__(self,参数1，参数2，...)
"""


class A:
    def __init__(self, age):
        self.age = age + 1


class B(A):
    def __init__(self, age, name):
        super(B, self).__init__(age)
        self.name = name


b = B(12, 'mike')
print(b.__dict__)
