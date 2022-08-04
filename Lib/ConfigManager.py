import threading


class ConfigManager(object):
    # 线程锁
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls):
        if not hasattr(ConfigManager, "_instance"):
            with ConfigManager._instance_lock:
                if not hasattr(ConfigManager, "_instance"):
                    ConfigManager._instance = object.__new__(cls)
        return ConfigManager._instance
        pass

    def hifi_cookies(self):
        return { "enwiki_session": r"bbs_sid=4bh9alktdpajnn93jih89dgb6t; bbs_token=IVQuA0yigYg_2F2zC3WucQckhvwXYC_2BDjd4iWBWwmBeh8V1dRYKD4j8AcHuMVrLHYcrgBTcVwqlA_2BeC53P9Yyi39x19PQIZ7dD" }

    def http_porxy(self):
        return 'http://t30022786:Shmily349713.@proxy.huawei.com:8080'

    def https_porxy(self):
        return 'http://t30022786:Shmily349713.@proxy.huawei.com:8080'

    def requests_proxies(self):
        return None
        proxies = {
            'http': 'http://t30022786:Shmily349713.@proxy.huawei.com:8080',
            'https': 'http://t30022786:Shmily349713.@proxy.huawei.com:8080',
        }
        return proxies