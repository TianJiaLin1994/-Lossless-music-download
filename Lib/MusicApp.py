import os
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from lanzou.api import LanZouCloud
from functools import partial
from Lib.HifiHelper import HifiHelper

from selenium import webdriver



class SearchResultListBox(tk.Frame):
    def __init__(self, *args):
        super(SearchResultListBox, self).__init__(*args)
        self._item_count = 0
        self._item_list = []
        self._play_list = {}

        self._chrome_options = webdriver.ChromeOptions()
        self._chrome_options.add_argument('--headless')
        self._chrome_options.add_argument('--no-sandbox')
        self._thread_pool = ThreadPoolExecutor(max_workers=4)

        self._browser = webdriver.Chrome(executable_path=r"D:/python_soft/web_driver/chromedriver.exe", options=self._chrome_options)
        pass

    def init(self):
        self._play_label = tk.Label(self, text='正在播放歌曲 ： 暂未播放歌曲')
        self._play_label.place(x=0,y=0, width=200, height=20)
        self._stop_button = tk.Button(self, text="停止", command=self._stop_play_click)
        self._stop_button.place(x=200,y=0, width=100, height=20)
        self._down_label = tk.Label(self, text='正在下载歌曲 ： . . . . . . ')
        self._down_label.place(x=300, y=0, width=400, height=20)
        self._down_progress_label = tk.Label(self, text='进度 ： * ')
        self._down_progress_label.place(x=700, y=0, width=100, height=20)
        pass

    def _stop_play_click(self):
        self._browser.refresh()
        pass

    def play_music(self, name, url):
        if name in self._play_label['text']:
            return
        print('play :' + url)
        self._play_label['text']= '正在试听歌曲 ： {}'.format(name)
        # self._stop_play_click()
        self._browser.get(url)
        pass

    def insert(self, url, name):
        y = 30 * (self._item_count + 1)

        label = tk.Label(self, text=name)
        label.place(x=0,y=y, width=500, height=20)


        down_button = tk.Button(self, text="下载", command=partial(self._down_button_click, name, url))
        down_button.place(x=510,y=y, width=100, height=20)

        play_button = tk.Button(self, text="试听", command=partial(self._play_button_click, name, url))
        play_button.place(x=610, y=y, width=100, height=20)

        self._item_list.append([label, down_button, play_button])

        self._item_count += 1
        pass

    def place(self, x, y, width, height):
        super(SearchResultListBox, self).place(x=x,y=y, width=width, height=height)
        pass

    def clean(self):
        for [label, down_button, play_button] in self._item_list:
            label.destroy()
            down_button.destroy()
            play_button.destroy()
        self._item_count = 0
        pass

    def _down_lanzou_progress(self, file_name, total_size, now_size):
        self._down_progress_label['text'] = '进度 : {}/{}'.format(int(now_size / 1024 / 1024), int(total_size / 1024 / 1024))
        pass
    def _down_lanzou_final(self, file_path:str):
        suffix_name = file_path[file_path.rfind('.') + 1:]
        path = file_path[:file_path.rfind('\\')]
        file_name = file_path[file_path.rfind('\\') + 1:]

        import zipfile
        release_file_dir = path + '\\music'
        is_zip = zipfile.is_zipfile(file_path)
        if is_zip:
            zip_file_contents = zipfile.ZipFile(file_path, 'r')
            for file in zip_file_contents.namelist():
                filename = file.encode('cp437').decode('gbk')  # 先使用cp437编码，然后再使用gbk解码
                if '.mp3' in filename or os.path.exists(release_file_dir + '\\' + filename):
                    continue
                zip_file_contents.extract(file, release_file_dir)  # 解压缩ZIP文件
                os.chdir(release_file_dir)  # 切换到目标目录
                os.rename(file, filename)  # 重命名文件
        self._down_progress_label['text'] = '进度 : 完成'
        os.remove(file_path)
        pass
    def _download_by_url(self, url):
        down_url, down_passwd = HifiHelper().parse_down_url(url)
        LanZouCloud().down_file_by_url(down_url, pwd=down_passwd, save_path='D:\\code\\Hifini_music\\download', callback=self._down_lanzou_progress, downloaded_handler=self._down_lanzou_final)
        pass
    def _down_button_click(self, name, url):
        self._down_label['text'] = '下载歌曲 ： {}'.format(name)
        self._thread_pool.submit(self._download_by_url, url)
        pass

    def _play_audition_url(self, url):
        pass

    def _play_button_click(self, name, url):
        # 加入播放列表
        print(url)
        self._browser.get(url)
        play_button = self._browser.find_element_by_xpath('//*[@id="player4"]/div[1]/div')
        if play_button is None:
            self._play_label['text'] = '该歌曲无法试听 ： {}'.format(name)
            return
        self._play_label['text'] = '正在试听歌曲 ： {}'.format(name)
        play_button.click()
        return
        pass

class MusicApp(object):
    def __init__(self):

        pass

    def init(self, title_name:str, width:int = 800, height:int = 600):
        self._main_window = tk.Tk()
        self._main_window.title(title_name)
        self._main_window.geometry('{}x{}'.format(width, height))
        self.set_center_window(width, height)

        # 搜索输入框
        self._search_entry = tk.Entry(self._main_window)
        self._search_entry.place(x=20,y=20, width=400, height=30)
        # 搜索按钮
        self._search_button = tk.Button(self._main_window, text="搜索", command=self._click_search_button)
        self._search_button.place(x=600,y=20, width=60, height=30)
        # 搜索结果显示
        self._search_result_frame = SearchResultListBox(self._main_window)
        self._search_result_frame.place(x=0,y=60, width=width, height=400)
        self._search_result_frame.init()
        pass

    def run(self):
        self._main_window.mainloop()
        pass

    def set_center_window(self, width, height):
        ws = self._main_window.winfo_screenwidth()
        hs = self._main_window.winfo_screenheight()
        x = int((ws / 2) - (width / 2))
        y = int((hs / 2) - (height / 2))
        self._main_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        pass

    def _make_search_result_item(self, url, name):
        item = tk.Frame()
        test_label = tk.Label(item, text='test_item')
        test_label.pack()
        down_button = tk.Button()
        down_button.pack()
        return down_button

    def _click_search_button(self):
        self._search_result_frame.clean()
        music_name = self._search_entry.get()
        search_table = HifiHelper().search(music_name)
        if len(search_table) == 0:
            print('没有搜索到')
        for url, name in search_table.items():
            self._search_result_frame.insert(url, name)
            #print('url : {}, name : {}'.format(url, name))
