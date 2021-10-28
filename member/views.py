import json
import uuid

from bs4 import BeautifulSoup
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from django_redis import get_redis_connection
from . import models
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import exceptions
from rest_framework import serializers
from selenium import webdriver
import time
import requests
from requests.cookies import RequestsCookieJar
from headers import rua
import re
from rest_framework import status

redis_connect = get_redis_connection()
# class CreateAccountView(APIView):
#     redis_conn = get_redis_connection('loginapp')

    # def post(self, request, *args, **kwargs):
    #     username = request.data.get('username')
    #     password = request.data.get('password')
    #     nickname = request.data.get('nickname')
    #     email = request.data.get('email')


class LoginView(APIView): # 會員認證
    def post(self, request, *args, **kwargs):
        data = request.data
        user_object = models.UserInfo.objects.get(username=data.get('username'))
        if not user_object:
            return Response('登入失敗')
        random_stirng = str(uuid.uuid4())
        d = {'id': user_object.id, 'username': user_object.username}
        redis_connect.set(random_stirng, json.dumps(d), 259200) # token設為key
        # 259200秒等於72小時
        return Response({'code': 0, 'data': d}, status=status.HTTP_200_OK)


class Tokenauthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            token_q = request.query_params.get('token')
            print('token:',token_q)
        # user_object = models.UserInfo.objects.filter(token=token).first()
            user_data = redis_connect.get(token_q)
        except Exception as e:
            raise exceptions.AuthenticationFailed({'code':405, 'error':'請求錯誤<請重新登錄'})
        if user_data:
            return (user_data, token_q)
        return (None, None)


class UserView(APIView):  # 登入後傳送到的頁面
    authentication_classes = [Tokenauthentication]

    def get(self, request, *args, **kwargs):
        print(request.user)  # UserInfo object (1)
        print(request.auth)
        if request.user:
            return Response('登入所以可以看到')
        return Response('不是會員')


class Email(APIView):  # 報名參加後寄信通知
    authentication_classes = [Tokenauthentication]
    def post(self, request, *args, **kwargs):
        # 註記為參賽者
        username = request.user.username
        models.UserInfo.objects.filter(username=username).update(candidate=1)
        # 獲取該會員的信箱
        email = request.user.email
        # 發送信件
        send_mail('已成功參加比賽', '參加比賽', 'tsaizooey@gmail', [email],)
        return Response({'success':'已通知'})


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = "__all__"


class Candidate(APIView):
    def get(self, request, *args, **kwargs):
        # 列出所有參賽者
        query_set = models.UserInfo.objects.filter(candidate=1) # 參賽者標註為1
        ser = CandidateSerializer(query_set, many=True)
        return Response(ser.data)


class IgSpider():
    def __init__(self):
        self.path = 'D:\DeepLearning\chromedriver.exe'
        self.sbaccount = 'tsaizooey'
        self.sbpd = 'jondae350'

    def ig_token(self):  # 獲得登入後的cookie
        driver = webdriver.Chrome(self.path)
        driver.implicitly_wait(3)
        driver.get('https://www.instagram.com/')
        time.sleep(5)
        account = driver.find_elements_by_name('username')[0]
        pd = driver.find_elements_by_name('password')[0]
        time.sleep(5)
        account.send_keys(self.sbaccount)
        pd.send_keys(self.sbpd)
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click()  # 登入
        driver.implicitly_wait(3)
        driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/section/div/button').click()
        time.sleep(3)
        cookie = driver.get_cookies()
        jar = RequestsCookieJar()
        for i in cookie:
            jar.set(i['name'], i['value'])
        driver.close()
        return jar

    def download_avatar(self, id, request):
        cookies = self.ig_token()
        s = requests.session()
        headers = {"User-Agent": rua(),
                   }

        res = s.get(url=f"https://www.instagram.com/{id}/", headers=headers, cookies=cookies).text
        final_res = res.replace('\\u0026', '&')
        pat_id = '"logging_page_id":"profilePage_(.*?)"'
        pat_avatar = '"logging_page_id".*?"profile_pic_url_hd":"(.*?)"'
        id = re.compile(pat_id, re.S).findall(res)
        profile_pic_url = re.compile(pat_avatar, re.S).findall(final_res)[0] # 頭像
        return profile_pic_url

    def download_photo(self, url, request):
        # url = f"https://www.instagram.com/{id}/"
        s = requests.session()
        cookies = self.ig_token()
        headers = {"User-Agent": rua(),
                   }
        res = s.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(res.text, 'html.parser')
        json_part = soup.find_all("script", type="text/javascript")[3].string
        try:
            json_part = json_part[json_part.find('=') + 2:-1]
            data = json.loads(json_part)
            a = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
            # 總文章數
            count = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
            userid = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
            print('輸入的帳號為：', id, '共有', count, '篇貼文')
            all_photo_link = []
            for i in range(5):
                photo_link = f"https://www.instagram.com/p/{a[i]['node']['shortcode']}/"
                all_photo_link.append(photo_link)
            print(len(all_photo_link))
            return all_photo_link
        except:
            return Response('錯誤')


class CandidateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IgPhoto
        fields = "__all__"


class CandidateDetail(APIView):

    def get(self, request, username, *args, **kwargs):
        # 每位候選人列出五張ig照片
        try:
            five_photo = []
            queryset = models.IgPhoto.objects.filter(username=username)
            ser = CandidateDetailSerializer(queryset, many=True)
            for i in queryset:
                five_photo.append(i.ig_photo)
        except:
            return Response('查無此人帳號')
        return Response(ser.data)

    def post(self, request, username):
        # 爬完存到資料庫
        # 假設註冊時已填寫過ig帳號
        queryset = models.UserInfo.objects.get(username=username)
        ig_account = queryset.ig_account
        ig_avatar = IgSpider().download_avatar(ig_account, request)
        models.UserInfo.objects.filter(username=username).update(ig_avatar=ig_avatar)
        ig_photo = IgSpider().download_photo(ig_account, request) # 為一個list
        u = models.UserInfo.objects.get(username=username)
        for i in ig_photo:
            u.igphoto_set.create(ig_photo=i, username=u)
        return Response(ig_photo)


class PhotoVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IgPhoto
        fields = "__all__"


class PhotoVisit(APIView):
    def get(self, request, id):  # 列出瀏覽數
        queryset = models.IgPhoto.objects.filter(id=id)
        visit_times = queryset[0].visit + 1
        queryset.update(visit=visit_times)
        ser = PhotoVisitSerializer(instance=queryset, many=True)
        return Response(ser.data)


class PhotoRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IgPhoto
        fields = "__all__"


class PhotoRank(APIView):
    def get(self, request):
        query_set = models.IgPhoto.objects.order_by('visit')[::-5]
        ser = PhotoRankSerializer(query_set, many=True)
        return Response(ser.data)








