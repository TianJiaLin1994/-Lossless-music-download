import os

import requests
import lxml
from bs4 import BeautifulSoup
import re
import json

from Lib.ConfigManager import ConfigManager

import threading


class HifiHelper(object):
    # 线程锁
    _instance_lock = threading.Lock()

    def __init__(self):
        self._main_url = 'https://www.hifini.com'
        pass

    def __new__(cls):
        if not hasattr(HifiHelper, "_instance"):
            with HifiHelper._instance_lock:
                if not hasattr(HifiHelper, "_instance"):
                    HifiHelper._instance = object.__new__(cls)
        return HifiHelper._instance
        pass

    def get_lanzhou_down_url(self, url:str, passwd=None):
        if passwd is not None:
            en_passwd_url = url[:url.rfind('/')] + '/ajaxm.php'
            en_passwd_json = {
                'action' : 'downprocess',
                'sign' : 'A2UCPFloDz4JAAs0AjJUaANrV2JWOgIwBzIEMlE_bUGUILlt4CGhUMQdnUTIAYwcyA29SY1E9V2ZXZA_c_c',
                'p' : passwd
            }
            strhtml = requests.post(en_passwd_url, data=en_passwd_json)
            print(strhtml.url)
            res = requests.get(strhtml.url)


        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36 Edg/79.0.309.51',
            'origin': 'https://www.lanzous.com'
        }
        # 请求下载页面
        strhtml = requests.get(url, headers=headers)
        soup = BeautifulSoup(strhtml.text)
        # 拿到iframe地址
        data = soup.select('body > div.d > div.d2 > div.ifr > iframe')
        dowhtml = requests.get('https://www.lanzous.com' + data[0]['src'], headers=headers)
        soup = BeautifulSoup(dowhtml.text)
        # 拿到ajax请求脚本
        data = soup.select('body > script')
        # 正则取签名
        searchObj = re.findall(r'(.*)\'sign\':\'(.*?)\'', data[0].text, re.M | re.I)
        # 请求ajax获取跳转地址
        dowjsonStr = requests.post('https://www.lanzous.com/ajaxm.php',
                                   data={'action': 'downprocess', 'sign': searchObj[1][1], 'ves': '1'}, headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36 Edg/79.0.309.51',
                'referer': 'https://www.lanzous.com/fn?' + searchObj[1][1],
            })
        dowjson = json.loads(dowjsonStr.text)
        # 请求跳转地址获取真实地址
        oragin = requests.get(dowjson['dom'] + '/file/' + dowjson['url'], allow_redirects=False, headers={
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        })
        # 拿到302跳转地址
        downUrl = oragin.next.url
        print(downUrl)
        return downUrl  # 调用

    def get_url_html(self, url):
        if ConfigManager().requests_proxies() is not None:
            url_ret = requests.get(url, proxies=ConfigManager().requests_proxies(), cookies=ConfigManager().hifi_cookies())
        else:
            url_ret = requests.get(url, cookies=ConfigManager().hifi_cookies())
        return url_ret

    def get_url_stream_html(self, url):
        if ConfigManager().requests_proxies() is not None:
            url_ret = requests.get(url, stream=True, proxies=ConfigManager().requests_proxies())
        else:
            url_ret = requests.get(url, stream=True)
        return url_ret

    def _parse_search_res(self, url_ret):
        res = {}
        soup = BeautifulSoup(url_ret.text, 'lxml')
        res_lst = soup.find_all(name='div', attrs={"class": "subject break-all"})
        for subject_break_all in res_lst:
            # print(subject_break_all.a)
            subject_url = subject_break_all.a.get('href')
            url = '{}/{}'.format(self._main_url, subject_url)
            res[url] = subject_break_all.a.get_text()
        return res
        pass

    def search(self, music_name:str):
        url = '{}/search-{}.htm'.format(self._main_url, music_name)
        search_url_ret = self.get_url_html(url)
        search_res_table = self._parse_search_res(search_url_ret)
        return search_res_table
        pass

    def parse_audition_url(self, url):
        audition_html = self.get_url_html(url)

        soup = BeautifulSoup(audition_html.text, 'lxml')
        music_name = None
        music_url = None
        for script in soup.find_all(name='script'):
            if script.string == None: continue
            if 'new APlayer(' in script.string:
                title = re.findall(r'title: ?\'(.*)\'', str(script.string))[0]
                author = re.findall(r'author: ?\'(.*)\'', str(script.string))[0]
                music_url = re.findall(r'url: ?\'(.*)\'', str(script.string))[0]
                # music_pic = re.findall(r'pic: ?\'(.*)\'', str(script.string))[0]
                if music_url is None:
                    return None

                music_name = '{} - {}'.format(title, author)
                music_url = self._main_url + '/' + music_url
        res = self.get_url_html(music_url)
        if res.ok is True and '404' not in res.url:
            return res.url
        return None
        pass

    def parse_down_url(self, url:str):
        down_htm = self.get_url_html(url)
        soup = BeautifulSoup(down_htm.text, 'lxml')
        res_lst = soup.find_all(name='div', attrs={"class": "alert alert-warning"})
        is_need_replace = False
        for res in res_lst:
            if '本帖含有隐藏内容' in res.text:
                is_need_replace = True
        if is_need_replace:
            replace_url = url.replace('https://www.hifini.com/thread-', 'https://www.hifini.com/post-create-')[:-4] + '-1.htm'
            print(replace_url)
            replace_json = {
                'doctype' : '1',
                'return_html': '1',
                'quotepid': '0',
                'message': 'thanks very much !!!',
            }
            requests.post(replace_url, data=replace_json, cookies=ConfigManager().hifi_cookies())
            down_htm = self.get_url_html(url)

        soup = BeautifulSoup(down_htm.text, 'lxml')

        down_url = ''
        down_passwd = ''

        down_info_lst = soup.find_all(name='div', attrs={"class": "alert alert-success"})
        for down_info in down_info_lst:
            if '链接' in down_info.text and '提取码' in down_info.text:
                print(down_info.text)
                down_url = re.findall(r'链接: (.*) 提取码', down_info.text)[0]
                #'.u_jx_d_OQ{display:inline !important;}'
                spans = down_info.find_all(name='span')
                for span in spans:
                    is_va_passwd = len(re.findall('.' + span['class'][0] + '.*' + '{display:inline !important;}', down_htm.text)) > 0
                    if is_va_passwd:
                        down_passwd = down_passwd + span.text
                print(down_url)
                print(down_passwd)

        return down_url, down_passwd
        pass

if __name__ == '__main__':
    url = 'https://www.hifini.com/thread-41473.htm'
    HifiHelper().parse_down_url(url)
    pass