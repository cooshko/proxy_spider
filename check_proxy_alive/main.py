#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import json
import os
import sys
import time
import requests
from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import Lock, Queue, cpu_count, Process
from multiprocessing.queues import Empty
import chardet
import redis
import pika
import re
sys.path.insert(0, os.path.dirname(__file__))
import config


class ProxyDetector(object):
    # 进程锁
    MY_LOCK = Lock()
    MY_PATH = os.path.dirname(__file__)
    Q = Queue()
    REDIS_POOL = redis.ConnectionPool(host=config.REDIS_HOST,
                                      port=config.REDIS_PORT,
                                      password=config.REDIS_PASSWORD)

    def __init__(self):
        self.MY_DEBUG = getattr(config, "MY_DEBUG", True)
        self.MY_TARGET = getattr(config, "MY_TARGET", r"http://ip.cn/?")
        self.MY_TIMEOUT = getattr(config, "MY_TIMEOUT", 2.0)
        self.MY_PROCESSES_NUMBER = cpu_count()
        self.pool = ThreadPool(self.MY_PROCESSES_NUMBER)
        self.MY_HEADERS = getattr(config, "MY_HEADERS", {"User-Agent": r"curl/7.47.0", "Accept": r"*/*", })
        self.MY_TARGET_CHARACTER = getattr(config, "MY_TARGET_CHARACTER", "")
        self.alive_proxys = []

    def handle_alive_proxy(self, proxy):
        """
        对有效的代理进行处理
        :param proxy:
        :return:
        """
        r = redis.StrictRedis(connection_pool=ProxyDetector.REDIS_POOL)
        r.sadd('alive_proxies', proxy)

    def handle_revalidation_fail(self, proxy):
        """
        对重验证失效的代理进行处理
        :param proxy:
        :return:
        """
        self.MY_LOCK.acquire()
        r = redis.StrictRedis(connection_pool=ProxyDetector.REDIS_POOL)
        r.srem('alive_proxies', proxy)
        self.MY_LOCK.release()

    def content_has_character(self, raw_content: bytes):
        detect_result = chardet.detect(raw_content)
        encoding = 'gb18030' if detect_result['encoding'] in ['gbk', 'gb2312'] else 'utf8'
        content = str(raw_content, encoding=encoding)
        return self.MY_TARGET_CHARACTER in content

    def check_alive(self, validation_type, proxy):
        """
        验证proxy是否有效
        :param validation_type: new, revalidation
        :param proxy: 字符串，http://x.x.x.x:y
        :return:
        """
        # 全局变量：验证网站、是否调试、超时时间
        proxy = proxy.lower()
        proxies = dict()
        proxies["http"] = proxies["https"] = proxy.replace('https', 'http')
        if self.MY_DEBUG:
            print(validation_type, proxy)
        # 为保证质量，一个proxy验证三次（loop_count），必须至少成功两次（success_count），才算有效
        success_count = 0
        loop_count = 0

        # 平均响应时间
        response_times = []

        while loop_count < 3:
            try:
                loop_count += 1

                # 已经两次失败情况下，没必要进入第三次loop
                if loop_count == 3 and success_count == 0:
                    if validation_type == 'revalidation':
                        self.handle_revalidation_fail(proxy)
                        return False

                start_time = time.time()  # 用于计算响应时间
                resp = requests.get(url=self.MY_TARGET, proxies=proxies, timeout=self.MY_TIMEOUT, headers=self.MY_HEADERS)
                response_times.append(time.time() - start_time)  # 计算本次响应时间并添加到响应时间列表中

                if resp.status_code == 200:
                    # 当返回HTTP状态码为200时，检查响应的内容是否为空
                    # 不为空则success_count自增1
                    raw_content = resp.content.strip()
                    if len(raw_content) > 0:
                        if self.content_has_character(raw_content):
                            # 返回的网页内容含有指定的内容
                            success_count += 1
                        else:
                            # 没有指定内容的话，视为无效代理
                            break

                    if success_count == 2:
                        # 如已成功两次，即可退出循环
                        break
                resp.close()
            except:
                continue

        if success_count >= 2:
            response_avg_seconds = sum(response_times) / len(response_times)
            self.MY_LOCK.acquire()
            if self.MY_DEBUG:
                print(proxy, "....OK!! %.2fs  PID:" % response_avg_seconds, str(os.getpid()))
            if validation_type == 'new':
                self.handle_alive_proxy(proxy)
            self.MY_LOCK.release()
            return proxy
        else:
            if validation_type == 'revalidation':
                # self.MY_LOCK.acquire()
                # print("removing", proxy)
                # self.MY_LOCK.release()
                self.handle_revalidation_fail(proxy)

    def before_job(self):
        if self.MY_DEBUG:
            #     print("ready to go, %d processes" % self.MY_PROCESSES_NUMBER)
            print("waiting for message...")
        result_path = os.path.join(ProxyDetector.MY_PATH, "result.txt")
        if os.path.exists(result_path):
            os.remove(result_path)

    def start(self):
        self.before_job()
        while True:
            try:
                cred = pika.PlainCredentials(config.RABBIT_USER, config.RABBIT_PASSWORD)
                conn = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBIT_HOST,
                                                                         port=config.RABBIT_PORT,
                                                                         credentials=cred,
                                                                         virtual_host=config.RABBIT_VHOST))
                channel = conn.channel()
                channel.queue_declare(queue="need_validation")

                channel.basic_consume(queue="need_validation",  # 从指定队列读取消息
                                      no_ack=True,  # 不用确认该消息，ack功能用于防止消息丢失
                                      consumer_callback=self.mq_consumer)  # 收到的数据，使用回调函数去处理，这里使用上方定义的callback函数
                channel.start_consuming()  # 开始不停的获取消息，注意，它是阻塞的
            except:
                time.sleep(3)

    def mq_consumer(self, ch, method, properties, body):
        item = json.loads(body.decode('utf8'))
        item_type = item[0]
        item_proxy = item[1]
        # self.check_alive(item_type, item_proxy)
        self.pool.apply_async(self.check_alive, (item_type, item_proxy))


def main():
    obj = ProxyDetector()
    obj.start()


if __name__ == '__main__':
    p_list = []
    for i in range(cpu_count()):
        p = Process(target=main)
        p_list.append(p)
        p.start()

    for p in p_list:
        p.join()
