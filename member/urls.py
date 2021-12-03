"""beauty URL Configuration

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
from django.urls import path
from django.conf.urls import include
from member import views


urlpatterns = [
    path('login/', views.LoginView.as_view()), # 會員登入認證
    path('user/', views.UserView.as_view()),
    path('email/', views.Email.as_view()),     # 參賽後寄電子郵件
    path('candidate/', views.Candidate.as_view()), # 候選人列表
    path('candidatedetail/<username>', views.CandidateDetail.as_view()), # 每位候選人資料(包含照片)
    path('photovisit/<id>', views.PhotoVisit.as_view()), # 照片瀏覽數
    path('photorank/', views.PhotoRank.as_view()), # 照片排行榜前五名
    path('search/', views.Search.as_view()), # 搜尋功能
    path('task/', views.create_task),
    path('testcelery/', views.TestCelery.as_view()),
    path('ooo/'),

]
