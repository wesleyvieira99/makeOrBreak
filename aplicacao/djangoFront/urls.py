from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', include('djangoFrontApp.urls')),
    path('admin/', admin.site.urls),
]


handler404 = 'djangoFrontApp.views.handlerNotFound'