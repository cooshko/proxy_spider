import pika
import json
import redis
REDIS_POOL = redis.ConnectionPool(host='myserver.com', port=16379, password="feiliuzhixia3qianchi")
r = redis.StrictRedis(connection_pool=REDIS_POOL, charset='utf-8')
all_proxies = r.smembers('alive_proxies')


cred = pika.PlainCredentials("http_proxy_user", "feiliuzhixia3qianchi")  # 远程访问的用户名、密码，如果不使用，则会默认调用guest/guest
conn = pika.BlockingConnection(pika.ConnectionParameters(host="myserver.com",
                                                         port=5672,
                                                         credentials=cred,
                                                         virtual_host='http_proxy_vhost'))  # 连接
channel = conn.channel()  # channel负责收发消息
channel.queue_declare(queue="need_validation")  # 声明一个队列，如果队列已经存在则忽略，如果不存在则创建
for item in all_proxies:
    proxy = item.decode('utf8')
    # print(proxy)
    channel.basic_publish(exchange="",
                          routing_key="need_validation",  # 相当于要往哪个队列里发消息
                          body=json.dumps(['revalidation', proxy]))  # 具体的消息内容
# print("Done")
conn.close()  # 发完数据就可以关闭链接了