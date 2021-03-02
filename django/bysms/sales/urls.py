#!/usr/bin/evn python
#-*- coding:utf-8 -*-


from django.urls import path 

from . import views



urlpatterns = [
    path('orders/', views.listorders),
    path('people/', views.people),
    path('customers/', views.listcustomers),
]