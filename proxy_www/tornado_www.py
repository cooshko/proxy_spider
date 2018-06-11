#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import json
import tornado.ioloop
import tornado.web
import redis
import pika

REDIS_POOL = redis.ConnectionPool(host='myserver.com', port=16379, password="feiliuzhixia3qianchi")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class GetLatestHandler(tornado.web.RequestHandler):
    def get(self):
        global REDIS_POOL
        r = redis.StrictRedis(connection_pool=REDIS_POOL, charset='utf-8')
        result = [x.decode("utf8") for x in r.smembers("alive_proxies")]
        self.write(json.dumps(result))


class ReportProxyHandler(tornado.web.RequestHandler):
    def post(self):
        proxy = self.get_argument("proxy_maybe_fail")
        r = redis.StrictRedis(connection_pool=REDIS_POOL, charset='utf-8')
        result = dict(result="")
        if r.sismember("alive_proxies", proxy):
            # 验证proxy是否有效
            self.report_proxy(proxy)
        else:
            result['result'] = "{} is not our member.".format(proxy)
        self.write(json.dumps(result))

    def report_proxy(self, proxy):
        # 推到消息队列中去
        cred = pika.PlainCredentials("http_proxy_user", "feiliuzhixia3qianchi")  # 远程访问的用户名、密码，如果不使用，则会默认调用guest/guest
        conn = pika.BlockingConnection(pika.ConnectionParameters(host="myserver.com",
                                                                 port=5672,
                                                                 credentials=cred,
                                                                 virtual_host='http_proxy_vhost'))  # 连接
        channel = conn.channel()  # channel负责收发消息
        channel.queue_declare(queue="need_validation")  # 声明一个队列，如果队列已经存在则忽略，如果不存在则创建

        channel.basic_publish(exchange="",
                              routing_key="need_validation",  # 相当于要往哪个队列里发消息
                              body=json.dumps(['revalidation', proxy]))  # 具体的消息内容
        # print("Done")
        conn.close()  # 发完数据就可以关闭链接了


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/latest_proxy.html', GetLatestHandler),
        (r'/proxy_maybe_fail.html', ReportProxyHandler),
    ], debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
