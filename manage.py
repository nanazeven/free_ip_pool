from multiprocessing import Process
import setting
from verify import Verify
from crawler import Crawler
from api import app
import time


class Manage:

    def manage_verify(self, interval=60):
        '''
        每隔interval时间运行一次代理验证程序
        :param interval:
        :return:
        '''
        verify = Verify()
        while True:
            verify.run()
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

        verify_process = Process(target=self.manage_verify)
        verify_process.start()

        api_process = Process(target=self.manage_api)
        api_process.start()
