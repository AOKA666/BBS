"""BBS2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from blog import views
from django.views.static import serve
from BBS2 import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    # 生成验证码
    path('get_code/', views.get_code),
    # 重置密码
    path('reset_pwd/', views.reset_pwd),
    # 点赞
    url(r'^click_favor/', views.click_favor),
    # 评论
    url(r'^comment/', views.comment),
    # 自定义暴露media
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    # 删除文章
    url(r'^delete_article/', views.delete_article),
    # 个人站点
    url(r'^(?P<username>\w+)/$', views.site, name='site'),

    # 共用一个函数
    url(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/', views.site),

    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article),
    # 后台管理
    url(r'^\w+/backend/', views.backend),
    # 我的文章
    url(r'^\w+/article_list/', views.article_list),
    # 添加文章
    url(r'^(?P<username>\w+)/add_article/', views.add_article),
    # 上传图片
    url(r'^upload_img/', views.upload_img),
    # 修改头像
    url(r'^(?P<username>\w+)/change_avatar/$', views.change_avatar),

]
