from django.shortcuts import render, HttpResponse
from django.views.generic import View
from rest_framework.views import APIView
import requests
from member.models import UserInfo
from rest_framework import serializers
from rest_framework.response import Response


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

def user(request):
    return render(request, 'user.html')

def get_friend_data(request):
    raw_data = UserInfo()
    info = raw_data['']




