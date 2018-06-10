#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import requests
import re
import logging
import multiprocessing
proxy_reg = r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+'
test_target = r'http://ip.cn/?'
test_keyword = '来自'
headers = {
    'User-Agent': r'curl/7.19.7 (x86_64-redhat-linux-gnu) libcurl/7.19.7 NSS/3.27.1 zlib/1.2.3 libidn/1.18 libssh2/1.4.2'
}
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def log(msg: str):
    logger.info(msg)


def check_proxy(proxy: str):
    """
    验证代理是否有效
    :param proxy:
    :return:
    """
    # print("taking", proxy)
    if re.match(proxy_reg, proxy):
        # 符合格式
        scheme, ip_port = proxy.split('://')
        proxies ={
            'http': r'http://{}'.format(ip_port),
            'https': r'http://{}'.format(ip_port),
        }
        count = 0
        while count < 10:
            count += 1
            log("proxy {} try {:d} times.".format(proxy, count))
            try:
                resp = requests.get(test_target, proxies=proxies, headers=headers, timeout=2)
                log(resp.text)
                return test_keyword in resp.text
            except:
                pass
    else:
        return False


def handle_proxy(proxy: str):
    if not check_proxy(proxy):
        log("{} seems unavailable".format(proxy))


if __name__ == '__main__':
    proxies = ['https://171.37.55.70:9797', 'https://118.212.137.135:31288']
    p_list = []
    for proxy in proxies:
        p = multiprocessing.Process(target=handle_proxy, args=(proxy,))
        p.start()
        p_list.append(p)

    for p in p_list:
        p.join()
