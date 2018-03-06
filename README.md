# weibo_users_distributed
之前Scrapy新浪微博用户爬虫的改进

使用`scrapy-redis`实现分布式爬取，结果保存MongoDB

通过分析[https://m.weibo.cn/](https://m.weibo.cn/)请求编写用户爬虫

方法是先选取一个用户获取他的关注与粉丝

然后再分别获取他关注人和粉丝的关注与粉丝，以此类推

爬取时遇到了报403，所以禁用了cookies，且设置了延迟
```
COOKIES_ENABLED=False
DOWNLOAD_DELAY=1
```
还有一个随机更换User-Agent的中间件。

我用一台安装了Redis的阿里云服务器作为master管理爬取队列

个人电脑和一台虚拟机作为slave分别爬取内容存储到各自的MongoDB中。

以下的pipeline会把爬取结果存储一份到远程Redis：
```
'scrapy_redis.pipelines.RedisPipeline': 301,
```
一定程度上会影响爬取效率，使用时可以去掉以达到更高效。

我放着运行了2个小时左右，两台slave的MongoDB分别有4700+和2100+个用户信息

其中有一台是加上之前爬取的2500多条的。
