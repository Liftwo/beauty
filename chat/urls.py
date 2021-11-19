from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from chat import views


urlpatterns = [
    # path('chat/', views.ChatRoom.as_view(), name='chat'),
    path('chat/', views.chat),
    path('realtime/', views.realtime),
    # path('friend/', views.friend),
]