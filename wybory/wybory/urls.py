"""wybory URL Configuration

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
from django.conf.urls import patterns, include, url
from django.contrib import admin

handler404 = 'ewybory.views.handler404'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wybory.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^ewybory/', include('ewybory.urls')),
    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)
