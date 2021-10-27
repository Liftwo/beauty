from bs4 import BeautifulSoup
import requests
from headers import rua
import json


path = 'D:\DeepLearning\chromedriver.exe'
sbaccount = 'tsaizooey'
sbpd = 'jondae350'
headers = {"User-Agent": rua(),}
id = 'instagram'
url =f"https://www.instagram.com/{id}/"

from selenium import webdriver
import time
import requests
from requests.cookies import RequestsCookieJar

def ig_token():  # 獲得登入後的cookie
    driver = webdriver.Chrome(path)
    driver.implicitly_wait(3)
    driver.get('https://www.instagram.com/')
    time.sleep(5)
    account = driver.find_elements_by_name('username')[0]
    pd = driver.find_elements_by_name('password')[0]
    time.sleep(5)
    account.send_keys(sbaccount)
    pd.send_keys(sbpd)
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

s = requests.session()
cookies = ig_token()
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
    print('輸入的帳號為：',id ,'共有',count,'篇貼文')
    all_photo_link = []
    for i in range(5):
        photo_link = f"https://www.instagram.com/p/{a[i]['node']['shortcode']}/"
        all_photo_link.append(photo_link)
    print(len(all_photo_link))
except:
    print('錯誤')
