# -*- coding: utf-8 -*-
import scrapy
from proxy_spider.items import KuaidailiItem
from pprint import pprint


class KuaidailiSpider(scrapy.Spider):
    name = "kuaidaili"
    allowed_domains = ["www.kuaidaili.com"]
    start_urls = [
        'http://www.kuaidaili.com/free/inha/1/',
        'https://www.kuaidaili.com/free/intr/1/',
    ]

    def parse(self, response):
        if response.status == 200:
            if response.body.strip() == '-10':
                # 遇到反爬虫，再刷新一下
                yield scrapy.Request(url=response.url, dont_filter=True)
            else:
                # 返回正常的页面
                trs = response.css("div#list > table tbody tr")
                for row in trs:
                    td_list = row.css("td")
                    if td_list:
                        pi = KuaidailiItem(
                            ip=td_list[0].xpath("string(.)").extract_first().strip(),
                            port=int(td_list[1].xpath("string(.)").extract_first().strip()),
                            anonymous=td_list[2].xpath("string(.)").extract_first().strip(),
                            type=td_list[3].xpath("string(.)").extract_first().strip(),
                            geography=td_list[4].xpath("string(.)").extract_first().strip(),
                        )
                        yield pi

                # 导航链接
                pagination_a = response.css("div#listnav a")
                for a in pagination_a:
                    next_page = response.urljoin(a.css("::attr(href)").extract_first())
                    page_num = int(str(next_page).strip(r'/').split(r'/')[-1])
                    if page_num < self.settings.get("DEPTH", 10):
                        # with open("visited_url.log", "a", encoding='utf8') as fp:
                        #     fp.write(next_page + "\n")
                        yield scrapy.Request(url=next_page)

