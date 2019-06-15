from db import RedisClient
import setting
import asyncio
import aiohttp
import time
import sys


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
                        print(proxy, redis_key, "ok 100点")
                        self.db.max(redis_key, proxy)
                    else:
                        print(proxy, redis_key, "fail -1点")
                        self.db.decrease(redis_key, proxy)
            except (aiohttp.ClientError, aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                print(proxy, redis_key, "error -1点", e)
                self.db.decrease(redis_key, proxy)

    async def run_by_redis(self, redis_key):
        count = self.db.count(redis_key)
        print(redis_key, '当前剩余', count, '个代理')
        for i in range(0, count, setting.TEST_SIZE):
            start = i
            end = min(i + setting.TEST_SIZE, count) - 1
            print('正在测试{}第'.format(redis_key), start + 1, '-', end + 1, '个代理')
            proxies = self.db.batch(redis_key, start, end)
            for proxy in proxies:
                await self.verify_proxy(redis_key, proxy)

    def run(self):
        print("开始验证代理")
        try:
            tasks = [
                self.run_by_redis(setting.REDIS_KEY_HTTP),
                self.run_by_redis(setting.REDIS_KEY_HTTPS)
            ]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            sys.stdout.flush()
            time.sleep(5)
        except Exception as e:
            print('验证程序运行错误: ', e)

    # def run_test(self):
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self.test())
    #
    # async def test(self):
    #     redis_key = setting.REDIS_KEY_HTTPS
    #     proxy = "223.85.196.75:9999"
    #     re_proxy = "http://223.85.196.75:9999"
    #     conn = aiohttp.TCPConnector(ssl=False)
    #     async with aiohttp.ClientSession(connector=conn) as session:
    #         try:
    #             async with session.get(setting.TEST_URL, proxy=re_proxy, timeout=6,
    #                                    allow_redirects=False) as resp:
    #                 if resp.status in [200, 302]:
    #                     print(proxy, redis_key, "ok 100点")
    #                     self.db.max(redis_key, proxy)
    #                 else:
    #                     print(proxy, redis_key, "fail -1点")
    #                     self.db.decrease(redis_key, proxy)
    #         except (aiohttp.ClientError, aiohttp.ClientConnectorError, asyncio.TimeoutError):
    #             print(proxy, redis_key, "error -1点")
    #             self.db.decrease(redis_key, proxy)


