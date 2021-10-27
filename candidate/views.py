from django.shortcuts import render
from requests.cookies import RequestsCookieJar
from selenium import webdriver
import time
import re
import random
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry


def rua():
    pool = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125",
    ]
    return random.choice(pool)


class IgFansSpider():
    def __init__(self):
        self.path = 'D:\DeepLearning\chromedriver.exe'
        self.sbaccount = 'tsaizooey'
        self.sbpd = 'jondae350'

    def ig_token(self):  # 獲得登入後的cookie
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=%s' % rua())
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 1}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(executable_path=self.path, options=options)
        driver.implicitly_wait(5)
        driver.get('https://www.instagram.com/')
        account = driver.find_elements_by_name('username')[0]
        pd = driver.find_elements_by_name('password')[0]
        time.sleep(5)
        account.send_keys(self.sbaccount)
        pd.send_keys(self.sbpd)
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button').click() #登入
        driver.implicitly_wait(5)
        try:
            driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/section/div/button').click()
        except:
            pass
        time.sleep(1)
        cookie = driver.get_cookies()
        jar = RequestsCookieJar()
        for i in cookie:
            jar.set(i['name'], i['value'])
        driver.close()
        return jar

    def sendReq(self, data):
        cookies = self.ig_token()
        s = requests.session()  # 把requests都算在同一個session
        s.mount('https://', HTTPAdapter(max_retries=Retry(total=3, method_whitelist=frozenset(['GET', 'POST']))))

        for i in data:
            print(i)
            headers = {"User-Agent": rua(),
                       }
            try:
                res = s.get(url=i['Pid'], headers=headers, cookies=cookies).text
                pat = '"logging_page_id".*?"profile_pic_url_hd":"(.*?)"'
                res = re.compile(pat, re.S).findall(res)
                avatar = res[0].replace('\\u0026', '&')
                time.sleep(1)
                if avatar == []:
                    print('....')
                    continue
                form = {
                    'user_uuid': i['uuid'],
                    'platform': 'ig',
                    'url': avatar
                }

                header = {
                    'Content-Type': 'application/json',
                    'Authorization': 'token 10b6f0b81d7d4b23e75587198c675d054436d2d7'
                }
                print(form)
                # 儲存資料
                resp = s.post(url=self.api2, headers=header, json=form, timeout=10, verify=False)
                time.sleep(1.5)
                if resp.status_code == 200:
                    form = {
                        'avatar': resp.json()['data']['cached_path'],
                        'userid': i['uuid'],
                        'platform': 'ig'}
                    s.post(url=self.api3, data=form, timeout=10, verify=False)
                    time.sleep(1)
            except Exception as e:
                print(e)
                print('error ' + i['Pid'])
                continue
            time.sleep(random.uniform(2.5, 5.5))
