# proxy_spider

#####  基于python3.5、Scrapy 1.3.3，爬取xici、kuaidaili每日公布的免费代理
#####  *由于这些代理的公布页有几千页，全部抓取并不明智，因此预设只抓取10页（每类代理），只xici已经有约3K代理数据。

##本工具由三个模块组成，分别是
#####check_proxy_alive 守护进程，不停验证proxy有效性
#####proxy_spider  scrapy爬虫程序
#####proxy_www 代理获取网站

##依赖
#####check_proxy_alive - redis、pika、chardet
#####proxy_spider - scrapy、pika
#####proxy_www - tornado、pika、redis

##部署和用法
#####check_proxy_alive - 执行main.py
#####proxy_spider - scrapy crawl xici（或者kuaidaili）
#####proxy_www - 执行tornado_www.py