from django.shortcuts import render, HttpResponse
from django.views.generic import View
from rest_framework.views import APIView
import requests
from member.models import UserInfo
from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
# from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile



class ChatRoom(View):
    template_name = 'room.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'index.html', {})

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'name': request.POST.get('name', 'NoName')
        })


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'ig_avatar', 'email']
        read_only_fields = fields

class UserInfo(APIView):
    def get(self, request, *args, **kwargs):

        queryset = UserInfo.objects.filter(username='me')
        ser = UserInfoSerializer(queryset, many=True)
        return Response({'data':ser.data})

def chat(request):
    return render(request, 'index_2.html')


def realtime(request):
    return render(request, 'realtime.html')


def user_list(request):
    users = UserProfile.objects.all()
    print(users)
    return render(request, 'user.html', {'users':users})


from django.contrib import auth


def post_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        print(user)
        if user:
            auth.login(request, user)
            return redirect('/chat/userlist/')
        else:
            print('非使用者')
            return redirect('/chat/login/')
    else:
        return render(request, 'log_in.html', locals())