from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from chat import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # path('chat/', views.ChatRoom.as_view(), name='chat'),
    path('chat/', views.chat),
    path('realtime/', views.realtime),
    path('login/', views.post_login),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('userlist/', views.user_list),

]