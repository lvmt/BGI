"""bysms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include



# 记得导入listorders函数
from sales.views import listorders
from sales.views import helloworld

# 静态文件服务
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # # 添加如下路由
    # path('sales/orders/', listorders),

    # 凡是url以sales/开头的， 都根据sales.urls里面的 子路由表进行路由

    path('sales/', include('sales.urls')),

    path('lmt/test/', helloworld),
    
    # 凡是 url 以 api/mgr  开头的，
    # 都根据 mgr.urls 里面的 子路由表进行路由
    path('api/mgr/', include('mgr.urls'))

    
] + static("/", document_root="./z_dist")
