from db import RedisClient
from setting import REDIS_KEY_HTTPS, REDIS_KEY_HTTP
from log import logger
# import logging
from urllib.parse import urljoin
import requests
import re
import time
from lxml import etree
from datetime import datetime


class CrawlerMetaclass(type):
    def __new__(cls, name, bases, attrs):
        '''
        将Crawler类中定义各个免费代理网站的爬虫方法进行汇总到__crawl_func__内
        :param name: 使用此元类的类名，Crawler
        :param bases: 父类
        :param attrs: 类Crawler的所有方法
        :return:
        '''
        count = 0
        attrs['__functions__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__functions__'].append(k)
                count += 1
        attrs['__function_count__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(metaclass=CrawlerMetaclass):
    def __init__(self):
        self.db = RedisClient()
        pass

    def run(self):
        # if self.db.is_over_maxinum(REDIS_KEY_HTTP) :
        #     return
        for callback_index in range(self.__function_count__):
            callback = self.__functions__[callback_index]
            try:
                for res in eval('self.{}()'.format(callback)):
                    if res['type'].upper() == 'HTTP':
                        print(res['proxy'])
                        # self.db.add(REDIS_KEY_HTTP, res['proxy'])
                    else:
                        print(res['proxy'])
                        # self.db.add(REDIS_KEY_HTTPS, res['proxy'])
            except Exception as e:
                logger.warning("{}爬虫方法报错：{}".format(callback, e))


    def xila(self):
        start_url = 'http://www.xiladaili.com/https/{}/'
        for i in range(1,3):
            html_ = get_html(start_url.format(i))
            if not html_:
                return
            doc = etree.HTML(html_)
            tr_list = doc.xpath("//tbody/tr")
            for tr in tr_list:
                ip = tr.xpath("./td[1]/text()")[0]
                yield {'prexy': ip, 'type': "HTTPS"}

    def crawl_dali66(self):
        start_url = "http://www.66ip.cn/nmtq.php?getnum=300&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=1&api=66ip"
        cookie = "__jsluid=98d51c4d405eb14ff88f78342f37b2e1; __jsl_clearance=1560506584.714|0|Y4wXo9n8%2FQ6752WTWKBw9u58GPg%3D"
        html = get_html(start_url, encoding='GBK', Cookie=cookie)
        if html:
            ip_list = re.findall(r'.*?(\d+\.\d+\.\d+\.\d+:\d+).*?', html)
            for proxy in ip_list:
                yield {'proxy': proxy, 'type': "HTTPS"}

    def crawl_kuaidaili(self):
        page_count = 5
        start_url = "https://www.kuaidaili.com/free/inha/{}/"
        for i in range(1, page_count + 1):
            url = start_url.format(i)
            html = get_html(url)
            if html:
                ip_list = re.findall(r'<td data-title="IP">(.*?)</td>', html)
                port_list = re.findall(r'<td data-title="PORT">(.*?)</td>', html)
                type_list = re.findall(r'<td data-title="类型">(.*?)</td>', html)
                for ip, port, type_ in zip(ip_list, port_list, type_list):
                    yield {'proxy': ip + ':' + port, 'type': type_}
                time.sleep(1)

    def crawl_xicidaili(self):
        page_count = 3
        start_url = "https://www.xicidaili.com/nn/{}/"
        for i in range(1, page_count + 1):
            html = get_html(start_url.format(i))
            if html:
                tr_list = re.findall(r'<tr class.*?>(.*?)</tr>', html, re.S)
                if tr_list:
                    for tr in tr_list:
                        ip = re.search(r'<td>(\d+\.\d+\.\d+\.\d+)</td>', tr).group(1)
                        port = re.search(r'<td>(\d+)</td>', tr).group(1)
                        type_ = re.search(r'<td>([HTPS]+)</td>', tr).group(1)
                        yield {'proxy': ip + ':' + port, 'type': type_}

    def crawl_goubanjia(self):
        start_url = "http://www.goubanjia.com/"
        key = 'ABCDEFGHIZ'
        html = get_html(start_url)
        if html:
            doc = etree.HTML(html)
            td_list = doc.xpath("//tbody/tr")
            for td in td_list:
                ip = td.xpath(
                    "./td[@class='ip']/*[not(@style) or @style='display: inline-block;' or @style='display:inline-block;']/text()")[
                     :-1]
                ip = "".join(ip)
                temp_port = td.xpath("./td[@class='ip']/span[contains(@class,'port')]/@class")[0].split(' ')[1]
                type_ = td.xpath('./td[3]/a/text()')[0]
                port = []
                for i in temp_port:
                    port.append(str(key.find(i)))
                port = int(''.join(port)) >> 3
                yield {'proxy': ip + ':' + str(port), 'type': type_}

    def crawl_yundaili(self):
        page_count = 3
        start_url = "http://www.ip3366.net/free/?stype=1&page={}"
        for i in range(1, page_count + 1):
            html = get_html(start_url.format(i), encoding='gb2312')
            if html:
                html = etree.HTML(html)
                tr_list = html.xpath("//table//tr")[1:]
                for tr in tr_list:
                    ip = tr.xpath("./td[1]/text()")[0]
                    port = tr.xpath("./td[2]/text()")[0]
                    type_ = tr.xpath("./td[4]/text()")[0]
                    yield {'proxy': ip + ':' + port, 'type': type_}

    def crawl_qydaili(self):
        page_count = 3
        start_url = "http://www.qydaili.com/free/?action=china&page={}"
        for i in range(1, page_count + 1):
            html = get_html(start_url.format(i))
            if html:
                doc = etree.HTML(html)
                ip_list = doc.xpath("//tbody//td[@data-title='IP']/text()")
                port_list = doc.xpath("//tbody//td[@data-title='PORT']/text()")
                type_list = doc.xpath("//tbody//td[@data-title='类型']/text()")
                for ip, port, type_ in zip(ip_list, port_list, type_list):
                    yield {'proxy': ip + ':' + port, 'type': type_}

    def crawl_ihuandaili(self):
        now = datetime.now().strftime('%Y/%m/%d/%H')
        start_url = "https://ip.ihuan.me/today/{}.html".format(now)
        proxy = self.db.randow(REDIS_KEY_HTTPS)
        proxies = {}
        if proxy:
            proxies = {'https': 'http://' + proxy}
        html = get_html(start_url, proxies=proxies)
        if html:
            ip_list = re.findall(r'.*?(\d+\.\d+\.\d+\.\d+:\d+)@([HTPS]+).*?', html)
            for ip_tuple in ip_list:
                yield {'proxy': ip_tuple[0], 'type': ip_tuple[1]}

    def crawl_iphai(self):
        start_url = "http://www.iphai.com/free/ng"
        html = get_html(start_url)
        if html:
            doc = etree.HTML(html)
            tr_list = doc.xpath("//table/tr")[1:]
            for tr in tr_list:
                ip = tr.xpath("./td[1]/text()")[0].replace('\n', '').strip()
                port = tr.xpath("./td[2]/text()")[0].replace('\n', '').strip()
                type_ = tr.xpath("./td[4]/text()")[0].replace('\n', '').strip()
                if type_ == "":
                    type_ = "HTTP"
                yield {"proxy": ip + ":" + port, "type": type_}

    def crawl_xsdaili(self):
        start_url = "http://www.xsdaili.com/"
        html = get_html(start_url)
        if html:
            doc = etree.HTML(html)
            div = doc.xpath("//div[contains(@class,'ips')]")[0]
            sub_url = div.xpath("./div[@class='title']/a/@href")[0]
            sub_html = get_html(urljoin(start_url, sub_url))
            if sub_html:
                sub_doc = etree.HTML(sub_html)
                proxy_list = re.findall(r'.*?(\d+\.\d+\.\d+\.\d+:\d+)@([HTPS]+).*?', sub_html)
                for proxy in proxy_list:
                    yield {'proxy': proxy[0], 'type': proxy[1]}

    def crawl_crossdaili(self):
        start_url = "https://lab.crossincode.com/proxy/"
        html = get_html(start_url)
        if html:
            doc = etree.HTML(html)
            tr_list = doc.xpath("//table/tr")[1:]
            for tr in tr_list:
                ip = tr.xpath("./td[1]/text()")[0]
                port = tr.xpath("./td[2]/text()")[0]
                type_ = tr.xpath("./td[4]/text()")[0]
                yield {"proxy": ip + ":" + port, "type": type_}


def get_html(url, encoding="utf-8", proxies=None, **kwargs):
    base_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
    }
    headers = dict(base_headers, **kwargs)
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
        if resp.status_code == 200:
            return resp.content.decode(encoding)
            # return resp.text
        else:
            logger.warning("网页下载失败：{}".format(url))
    except Exception as e:
        logger.warning("网页下载报错：{}".format(url))
        return None


# if __name__ == '__main__':
#     c = Crawler()
#     res = []
#     # c.run()
#     # c.crawl_dali66()
#     for i in c.xila():
#         print(i)
#         res.append(i)
#     print(len(res))
