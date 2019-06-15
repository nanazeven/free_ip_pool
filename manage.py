from multiprocessing import Process, Pool
import setting
from verify import Verify
from crawler import Crawler
from db import RedisClient
from api import app
import time


class Manage:
    def manage_http_verify(self, part, interval=60):
        '''
        每隔interval时间运行一次代理验证程序
        :param id:
        :param interval:
        :return:
        '''
        verify = Verify()
        while True:
            verify.run_verify_http(part)
            time.sleep(interval)

    def manage_https_verify(self, interval=60):
        verify = Verify()
        while True:
            verify.run_verify_https()
            time.sleep(interval)

    def manage_crawler(self, interval=5 * 60):
        '''
        每隔interval运行过一次代理爬虫
        :param interval:
        :return:
        '''
        crawler = Crawler()
        while True:
            crawler.run()
            time.sleep(interval)

    def manage_api(self):
        '''
        开启api服务
        :return:
        '''
        app.run(setting.API_HOST, setting.API_PORT)

    def start(self):
        crawl_process = Process(target=self.manage_crawler)
        crawl_process.start()

        verify_https_process = Process(target=self.manage_https_verify)
        verify_https_process.start()

        api_process = Process(target=self.manage_api)
        api_process.start()

        p = Pool(4)
        for i in range(4):
            p.apply_async(self.manage_http_verify, args=(i,))
        p.close()
        p.join()

