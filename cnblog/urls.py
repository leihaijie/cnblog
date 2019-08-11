"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from blog import views
from django.views.static import serve
from cnblog import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
    url(r'^get_valid_img/', views.get_valid_img),
    url(r'^index/', views.index),
    url(r'^$', views.index),
    url(r'^reg/', views.reg),
    url(r'^blog/', include("blog.urls")),
    # media配置,对外公开
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # 文件上传
    url(r'^upload_img/', views.upload_img),
    # 删除文章
    url(r'delete_article/', views.delete_article),
    # 编辑文章
    url(r'edit_article/', views.edit_article),
    # 用户注销
    url(r'logout/', views.logout),
    # 修改用户密码
    url(r'change_password/', views.change_password),
    # 修改用户头像
    url(r'modify_avatar/', views.modify_avatar),



]
