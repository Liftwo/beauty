import json
import uuid
from bs4 import BeautifulSoup
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from . import models
from rest_framework.authentication import BaseAuthentication
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import exceptions
from rest_framework import serializers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from requests.cookies import RequestsCookieJar
from headers import rua
import re
from rest_framework import status
from member.tasks import vote, add
from celery.result import AsyncResult
from django.db.models import F
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import TemplateHTMLRenderer

redis_connect = get_redis_connection()


class LoginView(APIView): # 會員認證
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            user_object = models.UserInfo.objects.get(username=data.get('username'))
        except ObjectDoesNotExist:
            return Response('帳號錯誤')

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
        user = json.loads(bytes.decode(request.user, "utf-8"))
        print(request.user)
        if user:
            return Response('登入所以可以看到')
        return Response('不是會員')


class Email(APIView):  # 報名參加後寄信通知
    authentication_classes = [Tokenauthentication]
    def post(self, request, *args, **kwargs):
        # 註記為參賽者
        user = json.loads(bytes.decode(request.user, "utf-8"))
        username = user.get('username')
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
    authentication_classes = [Tokenauthentication]
    def get(self, request, *args, **kwargs):
        # 列出所有參賽者
        query_set = models.UserInfo.objects.filter(candidate=1) # 參賽者標註為1
        ser = CandidateSerializer(query_set, many=True)
        return Response(ser.data)

    def post(self, request):  # 投票
        # user = json.loads(bytes.decode(request.user, "utf-8"))
        data = request.data
        vote.delay(data)  # 啟用celery

        queryset = models.UserInfo.objects.filter(username=data.get('candidate'))
        ser = CandidateSerializer(queryset, many=True)

        return Response(ser.data)

class IgSpider():
    def __init__(self):
        self.path = 'D:\DeepLearning\chromedriver.exe'
        self.sbaccount = ''
        self.sbpd = ''

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
            count = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count'] # 總文章數
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
            five_photos = []
            user = models.UserInfo.objects.get(username=username)
            # photo = user.igphoto_set.all()
            photo_r = models.IgPhoto.objects.filter(userinfo__username=username)
            # ser = CandidateDetailSerializer(photo_r, many=True)
            for i in photo_r:
                five_photos.append(i.ig_photo)
        except:
            return Response('查無此人帳號')
        return Response(five_photos)

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
        # visit_times = queryset[0].visit + 1
        visit_times = F('visit') + 1
        queryset.update(visit=visit_times)
        ser = PhotoVisitSerializer(instance=queryset, many=True)
        return Response(ser.data)


class PhotoRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IgPhoto
        fields = "__all__"


class PhotoRank(APIView):
    def get(self, request):
        query_set = models.IgPhoto.objects.order_by('-visit')[:5]
        ser = PhotoRankSerializer(query_set, many=True)
        return Response(ser.data)


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = "__all__"


class Search(APIView):
    def get(self, request):
        data = request.query_params.get('username')
        queryset = models.UserInfo.objects.filter(username__icontains=data)
        ser = SearchSerializer(queryset, many=True)
        return Response(ser.data)


def create_task(request):
    print('請求來了')


class TestCelery(APIView):
    # def get(self, request):
    #     data = add.delay(2,10)
    #     result = AsyncResult(data.task_id)
    #     # result = json.loads(bytes.decode(data, "utf-8"))
    #     return JsonResponse({'id':result.task_id})
    def post(self, request):
        time.sleep(3)

        data = request.data

        queryset = models.UserInfo.objects.get(username=data.get('candidate'))
        queryset.vote = F('vote') + 1
        queryset.save()
        return Response('成功')


class FriendListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserInfo
        fields = ['username', 'ig_avatar']
        read_only_fields = fields

    # def get_user(self, obj):
    #     if obj.user:
    #         return {"username": obj.username, "ig_avatar": obj.ig_avatar}


class FriendList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'friend.html'

    def get(self, request, *args, **kwargs):
        # uuid = request.query_params.get('username')
        uuid = 'me'
        print(uuid)
        try:
            user = models.UserInfo.objects.get(username=uuid)
            print(user)
        except:
            return Response({'無此人'})
        context = {'user': user.id}
        try:
            obj_friends = user.friend_set.all().values()
        except:
            return Response({'沒朋友'})
        # 找出該人的朋友們的頭像
        friends_info = []
        for i in obj_friends:
            friend_name = i['friend']
            ig_avatar = list(models.UserInfo.objects.filter(username=friend_name).values_list('ig_avatar', flat=True))
            for j in ig_avatar:
                d = {'friend':friend_name, 'ig_avatar':j}
            friends_info.append(d)
        # 使用序列化
        # data_ = models.Friend.objects.select_related('user').filter(user=user)
        # print('friend', data_)
        # ser = FriendListSerializer(data_, many=True)
        # print('結果',ser.data)

        return Response({'data': friends_info})


class IgCommentsSerializer(serializers.Serializer):
    post = serializers.CharField(max_length=1000)
    poster = serializers.CharField(max_length=200)


class IgComments(APIView):
    def __init__(self):
        self.path = '/Applications/chromedriver'
        self.sbaccount = '帳號'
        self.sbpd = '密碼'

    def post(self, request):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(self.path, options=options)
        driver.implicitly_wait(3)
        driver.get('https://www.instagram.com/') # 直接跳轉到文章
        time.sleep(2)
        account = driver.find_elements_by_name('username')[0]
        pd = driver.find_elements_by_name('password')[0]
        account.send_keys(self.sbaccount)
        pd.send_keys(self.sbpd)
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click()  # 登入
        time.sleep(3)
        driver.get('https://www.instagram.com/p/CYXqAMuBX0e/')
        more_xpath = '//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/li/div/button/div'
        time.sleep(3)
        while True:
            try:
                time.sleep(2)
                driver.find_element_by_xpath(more_xpath).click()
                print('下一頁')
            except:
                print('最後一頁')
                break
        crawl_comments = []
        comments = driver.find_element_by_class_name("XQXOT").find_elements_by_class_name("Mr508")
        n = 1
        for c in comments:
            poster = c.find_element_by_css_selector('h3._6lAjh span').text
            post_xpath = f'//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div[2]/div[1]/ul/ul[{n}]/div/li/div/div/div[2]/span'.format(n=n)
            time.sleep(2)
            post = c.find_element_by_xpath(post_xpath).text
            crawl_comments.append({'poster':poster, 'post':post})
            n+=1
        ser = IgCommentsSerializer(crawl_comments, many=True)
        return Response(ser.data)


class With_Celery(APIView):
    def post(self, request):
        add.delay(3, 5)
        return HttpResponse("Celery作業成功")


class No_Celery(APIView):
    def post(self, request):
        time.sleep(2)
        result = 3+5
        return HttpResponse(result)














