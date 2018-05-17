# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from proxy_spider.settings import ROOT_DIR
from proxy_spider.items import *
from pprint import pprint
import os
import json
import redis

REDIS_POOL = redis.ConnectionPool(host='redis.com', port=16379, password='feiliuzhixia3qianchi')


class ProxySpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if isinstance(item, ProxyItem):
            iid = item['type'] + item['ip'] + str(item['port'])
            if iid in self.ids_seen:
                raise DropItem("Duplicate item found: %s" % item)
            else:
                self.ids_seen.add(iid)
        return item


class ProxyPipeline(object):
    def open_spider(self, spider):
        self.proxy_list = []

    def process_item(self, item, spider):
        if isinstance(item, ProxyItem):
            self.proxy_list.append(dict(item))
        return item

    def close_spider(self, spider):
        data_dir = os.path.join(ROOT_DIR, 'proxy_data')

        # 如果不存在数据目录，就先创建
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        # 存json
        json_fp = os.path.join(data_dir, str(spider.name)+".json")
        with open(json_fp, 'w', encoding='utf8') as fp:
            json.dump(self.proxy_list, fp)

        # 存redis
        r = redis.StrictRedis(connection_pool=REDIS_POOL)
        for item in self.proxy_list:
            proxy_str = "%s %s:%s" % (item['type'], item['ip'], item['port'])
            r.sadd("new_proxies", proxy_str)
