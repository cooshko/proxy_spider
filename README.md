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
#####check_proxy_alive - 执行main.py，配置信息在config.py里
#####proxy_spider - 命令行下进入该目录，scrapy crawl xici（或者kuaidaili）， 需在pipeline.py里指定rabbitmq的参数
#####proxy_www - 执行tornado_www.py，参数在文件开头指定，预设监听8888端口，可用的URL：/latest_proxy.html 获取最新的可用的代理；/proxy_maybe_fail.html 如果有代理可能失效，可以POST {proxy: http://xx.xxx...} 到这个URL，系统会安排验证，如确实失效，会剔除出有效代理池