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
        return { "enwiki_session": r"" }

    def http_porxy(self):
        return ''

    def https_porxy(self):
        return ''

    def requests_proxies(self):
        return None
        proxies = {
            '',
            '',
        }
        return proxies
