import redis
import re
import setting
import random


class RedisClient:

    def __init__(self):
        self.db = redis.StrictRedis(host=setting.REDIS_HOST, port=setting.REDIS_POST, password=setting.REDIS_PASSWORD,
                                    db=0)

    def add(self, redis_key, proxy, score=setting.INIT_SCORE):

        if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', proxy):
            if not self.db.zscore(redis_key, proxy):
                return self.db.zadd(redis_key, {proxy: score})
        return None

    def randow(self, redis_key):
        '''
        获取有效代理，首先获取分数最高的代理，如果不存在。则按照排名获取
        :return: 随机代理
        '''

        res = self.db.zrangebyscore(redis_key, setting.MAX_SCORE, setting.MAX_SCORE)
        if len(res):
            proxy = random.choice(res)
        else:
            res = self.db.zrevrange(redis_key, 0, 100)
            if len(res):
                proxy = random.choice(res)
            else:
                proxy = None
        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf-8')
        return proxy

    def decrease(self, redis_key, proxy):
        '''
        代理分数-1 如果代理分数小于分数最小值MIN_SCORE 删除
        :param proxy: 代理
        :return: 修改后的代理分数
        '''
        score = self.db.zscore(redis_key, proxy)
        if score and score > setting.MIN_SCORE:
            return self.db.zincrby(redis_key, -1, proxy)
        else:
            self.db.zrem(redis_key, proxy)

    def exists(self, redis_key, proxy):
        '''
        是够存在
        :param proxy:
        :return: bloo
        '''
        return self.db.zscore(redis_key, proxy) == None

    def max(self, redis_key, proxy):
        '''
        将代理赋值最大分数add数据库
        :param proxy:
        :return:
        '''
        return self.db.zadd(redis_key, {proxy: setting.MAX_SCORE})

    def count(self, redis_key):
        '''
        获取可用代理数量
        :return: count
        '''

        return len(self.db.zrangebyscore(redis_key, setting.MAX_SCORE, setting.MAX_SCORE))

    def all(self, redis_key):
        '''
        获取全部代理
        :return:
        '''
        return self.db.zremrangebyscore(redis_key, setting.MIN_SCORE, setting.MAX_SCORE)

    def batch(self, redis_key, start, end):
        '''
        根据索引获取数据
        :param start:
        :param end:
        :return:
        '''
        return self.db.zrevrange(redis_key, start, end)

    def is_over_maxinum(self, redis_key):
        '''
        判断是否达到最大限制，上限为50000
        :return:
        '''
        if self.count(redis_key) >= setting.POOL_SIZE_MAX:
            return True

        return False
