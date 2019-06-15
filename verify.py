from db import RedisClient
import setting
import asyncio
import aiohttp
import time
from log import logger

class Verify:

    def __init__(self):
        self.db = RedisClient()

    async def verify_proxy(self, redis_key, proxy):
        '''
        验证一个代理IP
        :param proxy:
        :return:
        '''
        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf-8')
        re_proxy = 'http://' + proxy

        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                async with session.get(setting.TEST_URL, proxy=re_proxy, timeout=6,
                                       allow_redirects=False) as resp:
                    if resp.status in [200, 302]:
                        logger.info("{}池：{}： ok 100点".format(redis_key, proxy))
                        # print(proxy, redis_key, "ok 100点")
                        self.db.max(redis_key, proxy)
                    else:
                        logger.info("{}池：{}： fail -1点".format(redis_key,proxy))
                        # print(proxy, redis_key, "fail -1点")
                        self.db.decrease(redis_key, proxy)
            except (aiohttp.ClientError, aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                # print(proxy, redis_key, "error -1点", e)
                logger.info("{}池：{}： error -1点".format(redis_key, proxy))
                self.db.decrease(redis_key, proxy)

    # async def run_by_redis(self, redis_key):
    #     count = self.db.count(redis_key)
    #     print(redis_key, '当前剩余', count, '个代理')
    #     for i in range(0, count, setting.TEST_SIZE):
    #         start = i
    #         end = min(i + setting.TEST_SIZE, count) - 1
    #         print('正在测试{}第'.format(redis_key), start + 1, '-', end + 1, '个代理')
    #         proxies = self.db.batch(redis_key, start, end)
    #         for proxy in proxies:
    #             await self.verify_proxy(redis_key, proxy)
    #
    # def run(self):
    #     print("开始验证代理")
    #     try:
    #         tasks = [
    #             self.run_by_redis(setting.REDIS_KEY_HTTP),
    #             self.run_by_redis(setting.REDIS_KEY_HTTPS)
    #         ]
    #         loop = asyncio.get_event_loop()
    #         loop.run_until_complete(asyncio.wait(tasks))
    #         time.sleep(5)
    #     except Exception as e:
    #         print('验证程序运行错误: ', e)

    def run_verify_http(self, part):
        stime = time.time()

        count = self.db.count(setting.REDIS_KEY_HTTP)
        start = part * (count // 4)
        stop = start + (count // 4)
        if part == 3:
            stop = count
        try:
            print("{}开始验证{}-{}".format(setting.REDIS_KEY_HTTP, start, stop))

            for i in range(start, stop, setting.HTTP_VERIFY_SIZE):
                proxies = self.db.batch(setting.REDIS_KEY_HTTP, i, i + setting.HTTP_VERIFY_SIZE)
                loop = asyncio.get_event_loop()
                tasks = [self.verify_proxy(setting.REDIS_KEY_HTTP, proxy) for proxy in proxies]
                loop.run_until_complete(asyncio.wait(tasks))

            print("{}验证完成{}-{}耗时：{}".format(setting.REDIS_KEY_HTTP, start, stop, time.time() - stime))
        except Exception as e:
            print('{}验证报错{}-{}：{}'.format(setting.REDIS_KEY_HTTP, start, stop, e))

    def run_verify_https(self):
        stime = time.time()
        try:
            print("{}开始验证".format(setting.REDIS_KEY_HTTPS))

            count = self.db.count(setting.REDIS_KEY_HTTPS)
            for i in range(0, count, setting.HTTP_VERIFY_SIZE):
                proxies = self.db.batch(setting.REDIS_KEY_HTTPS, i, i + setting.HTTP_VERIFY_SIZE)
                loop = asyncio.get_event_loop()
                tasks = [self.verify_proxy(setting.REDIS_KEY_HTTPS, proxy) for proxy in proxies]
                loop.run_until_complete(asyncio.wait(tasks))

            print("{}验证完成,耗时：{}".format(setting.REDIS_KEY_HTTPS, time.time() - stime))
        except Exception as e:
            print('{}验证报错：{}'.format(setting.REDIS_KEY_HTTPS, e))
