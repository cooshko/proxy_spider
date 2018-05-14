# -*- coding: utf-8 -*-
import scrapy
from proxy_spider.items import XiciItem
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
            ip_list_table = response.css("table#ip_list")
            ip_rows = ip_list_table.css("tr")

            # 提取每行代理信息
            for row in ip_rows:
                td_list = row.css("td")
                if td_list:
                    pi = XiciItem(
                        ip=td_list[1].xpath("string(.)").extract_first().strip(),
                        port=int(td_list[2].xpath("string(.)").extract_first().strip()),
                        geography=td_list[3].xpath("string(.)").extract_first().strip(),
                        anonymous=td_list[4].xpath("string(.)").extract_first().strip(),
                        type=td_list[5].xpath("string(.)").extract_first().strip(),
                        # fromurl=response.url
                    )
                    yield pi

            # 导航链接
            pagination_a = response.css("div.pagination a")
            for a in pagination_a:
                next_page = response.urljoin(a.css("::attr(href)").extract_first())
                page_num = int(str(next_page).split(r'/')[-1])
                if page_num < self.settings.get("DEPTH", 10):
                    # with open("visited_url.log", "a", encoding='utf8') as fp:
                    #     fp.write(next_page+"\n")
                    yield scrapy.Request(url=next_page)
