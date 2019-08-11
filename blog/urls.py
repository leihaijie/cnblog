from django.conf.urls import url,include
from django.contrib import admin
from blog import views
from django.views.static import serve
from cnblog import settings


urlpatterns = [
    url(r'backend/$', views.backend),
    url(r'get_comment_tree/(\d+)$', views.get_comment_tree),
    url(r'add_article$', views.add_article),

    url(r'poll/$', views.poll),
    url(r'comment/$', views.comment),

    url(r'(?P<username>\w+)/(?P<condition>tag|cate|date)/(?P<param>.*)/', views.homesite),
    url(r'(?P<username>\w+)/articles/(?P<article_id>\d+)/', views.article_detail),
    url(r'(?P<username>\w+)/$', views.homesite),
]