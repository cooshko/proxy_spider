# -*- coding: utf-8 -*-
import scrapy
from proxy_spider.items import ProxyItem
import os
from pprint import pprint

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


class XiciSpider(scrapy.Spider):
    name = "xici"
    allowed_domains = ["www.xicidaili.com"]
    start_urls = [
        'http://www.xicidaili.com/nn/1',
        'http://www.xicidaili.com/nt/1',
        'http://www.xicidaili.com/wn/1',
        'http://www.xicidaili.com/wt/1'
    ]

    def parse(self, response):
        if response.status == 200:
            # 正常返回页面

            # 导航链接
            pagination_a = response.css("div.pagination a")
            for a in pagination_a:
                next_page = response.urljoin(a.css("::attr(href)").extract_first())
                page_num = int(str(next_page).split(r'/')[-1])
                if page_num < self.settings.get("DEPTH", 10):
                    yield scrapy.Request(url=next_page)

            # 当前页面内的代理列表
            for sel in response.xpath('//table[@id="ip_list"]/tr[position()>1]'):
                ip = sel.css('td:nth-child(2)::text').extract_first()
                port = sel.css('td:nth-child(3)::text').extract_first()
                scheme = sel.css('td:nth-child(6)::text').extract_first().lower()
                proxy = '%s://%s:%s' % (scheme, ip, port)
                yield ProxyItem(proxy=proxy)
    #             url = 'http://2018.ip138.com/ic.asp'
    #             meta = {
    #                 'proxy': proxy,
    #                 'dont_retry': True,
    #                 '_proxy_scheme': scheme,
    #                 '_proxy_ip': ip,
    #                 'download_timeout': 2,
    #             }
    #
    #             yield scrapy.Request(url=url, callback=self.check_available,
    #                                  meta=meta, dont_filter=True)
    #
    # def check_available(self, response):
    #     if response.status == 200:
    #         if "来自" in response.text:
    #             yield ProxyItem(proxy=response.meta['proxy'])
