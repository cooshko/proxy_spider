# -*- coding: utf-8 -*-
import scrapy
import redis


class CheckProxySpider(scrapy.Spider):
    name = "check_proxy"
    REDIS_POOL = redis.ConnectionPool(host='redis.com', port=16379, password="feiliuzhixia3qianchi")
    custom_settings = {
        "RETRY_ENABLED": False,
    }

    def start_requests(self):
        target_url = r'http://2017.ip138.com/ic.asp'
        headers = {"User-Agent": r"curl/7.47.0", "Accept": r"*/*", }
        r = redis.StrictRedis(connection_pool=self.REDIS_POOL)
        proxy_list = r.smembers("new_proxies")
        for item in proxy_list:
            scheme, ipport = item.decode("utf8").split()
            proxy = "%s://%s" % (scheme, ipport)
            meta = {"using_proxy": item.decode("utf8"), "proxy": proxy, "download_timeout": 1}
            yield scrapy.Request(target_url, callback=self.parse, headers=headers, meta=meta, dont_filter=True)

    def parse(self, response):
        if response.status == 200:
            fname = response.meta["using_proxy"].replace(":", "")+".html"
            with open(fname, 'wb') as f:
                f.write(response.body)
