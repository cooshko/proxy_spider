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
import pika
# import redis
#
# REDIS_POOL = redis.ConnectionPool(host='redis.com', port=16379, password='feiliuzhixia3qianchi')


class ProxySpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if isinstance(item, ProxyItem):
            if item['proxy'] in self.ids_seen:
                raise DropItem("Duplicate item found: %s" % item)
            else:
                self.ids_seen.add(item['proxy'])
        return item


class ProxyPipeline(object):
    def open_spider(self, spider):
        self.proxy_list = []

    def process_item(self, item, spider):
        if isinstance(item, ProxyItem):
            self.proxy_list.append(item['proxy'].lower())
        return item

    def close_spider(self, spider):
        data_dir = os.path.join(ROOT_DIR, 'proxy_data')

        # 如果不存在数据目录，就先创建
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        # 存文件
        with open(os.path.join(data_dir, str(spider.name)+'.txt'), 'w', encoding='utf-8') as f:
            f.writelines("\n".join(self.proxy_list))

        # 存json
        # json_fp = os.path.join(data_dir, str(spider.name)+".json")
        # with open(json_fp, 'w', encoding='utf8') as fp:
        #     json.dump(self.proxy_list, fp)

        # # 存redis
        # r = redis.StrictRedis(connection_pool=REDIS_POOL)
        # for item in self.proxy_list:
        #     proxy_str = "%s %s:%s" % (item['type'], item['ip'], item['port'])
        #     r.sadd("new_proxies", proxy_str)

        # 推到消息队列中去
        cred = pika.PlainCredentials("http_proxy_user", "feiliuzhixia3qianchi")  # 远程访问的用户名、密码，如果不使用，则会默认调用guest/guest
        conn = pika.BlockingConnection(pika.ConnectionParameters(host="myserver.com",
                                                                 port=5672,
                                                                 credentials=cred,
                                                                 virtual_host='http_proxy_vhost'))  # 连接
        channel = conn.channel()  # channel负责收发消息
        channel.queue_declare(queue="need_validation")  # 声明一个队列，如果队列已经存在则忽略，如果不存在则创建
        for proxy in self.proxy_list:
            channel.basic_publish(exchange="",
                                  routing_key="need_validation",  # 相当于要往哪个队列里发消息
                                  body=json.dumps(['new', str(proxy).lower()]))  # 具体的消息内容
        # print("Done")
        conn.close()  # 发完数据就可以关闭链接了


