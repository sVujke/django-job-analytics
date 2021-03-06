"""job_analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    #url(r'^tags/$', views.tags, name="tags"),
    url(r'^list/(?P<slug>[\w-]+)/$', views.list, name="list"),
    url(r'^timeline/', views.timeline, name="timeline"),
    url(r'^trending/', views.trending, name="trending"),
    url(r'^item/(?P<slug>[\w-]+)/(?P<id>[0-9]+)/$', views.item, name="item"),
    url(r'^compare/', views.compare, name="compare"),
    url(r'^admin/', admin.site.urls),
]
