#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import json
import tornado.ioloop
import tornado.web
import redis

REDIS_POOL = redis.ConnectionPool(host='127.0.0.1', port=16379, password="feiliuzhixia3qianchi")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class GetLatestHandler(tornado.web.RequestHandler):
    def get(self):
        global REDIS_POOL
        r = redis.StrictRedis(connection_pool=REDIS_POOL, charset='utf-8')
        result = [x.decode("utf8") for x in r.smembers("new_proxies")]
        self.write(json.dumps(result))


class PostProxiesHandler(tornado.web.RequestHandler):
    def post(self):
        content_type = self.get_argument("content_type")
        content = self.get_argument("content")
        proxy_list = []
        if content_type:
            content_type = content_type.lower()
            if content_type == "json":
                self.handle_json(content)
                return
            else:
                self.write("unsupport content type")

    def handle_json(self, json_str: str):
        global REDIS_POOL
        r = redis.StrictRedis(connection_pool=REDIS_POOL, charset='utf-8')
        obj = json.loads(json_str)
        if isinstance(obj, list):
            proxy_list = []
            for item in obj:
                proxy_str = "%s %s:%s" % (item["type"], item["ip"], str(item["port"]))
                proxy_list.append(proxy_str.lower())
            r.sadd("new_proxies", *proxy_list)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/latest_proxy.html', GetLatestHandler),
        (r'/post_proxy.html.html', PostProxiesHandler),
    ], debug=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
