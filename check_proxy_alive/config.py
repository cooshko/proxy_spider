#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

# 用于验证proxy是否有效的目标网站，不建议使用百度
# MY_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.8.2000 Chrome/30.0.1599.101 Safari/537.36",
#            "Accept": "image/webp,*/*;q=0.8",
#            "Accept-Language": "zh-CN"}
# MY_TARGET = "https://www.jd.com/"
# MY_TARGET = "http://2017.ip138.com/ic.asp"
MY_HEADERS = {"User-Agent": r"curl/7.47.0",
              "Accept": r"*/*", }
MY_TARGET = "http://ip.cn/?"
MY_TARGET_CHARACTER = "来自"

MY_DEBUG = True
MY_TIMEOUT = 2.0

# pika
RABBIT_HOST = 'myserver.com'
RABBIT_PORT = 5672
RABBIT_USER = "http_proxy_user"
RABBIT_PASSWORD = 'feiliuzhixia3qianchi'
RABBIT_VHOST = 'http_proxy_vhost'

# redis
REDIS_HOST = 'myserver.com'
REDIS_PORT = 16379
REDIS_PASSWORD = 'feiliuzhixia3qianchi'