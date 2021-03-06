import random
import sys
from ruia import AttrField, Item, Request, Spider, TextField
from ruia_ua import middleware
from aiostream.stream import list as alist
sys.path.append("..")

from database.motor_base import MotorBase


class ArchivesItem(Item):
    """
    eg: http://www.ruanyifeng.com/blog/archives.html
    """
    target_item = TextField(css_select='div#beta-inner li.module-list-item')
    href = AttrField(css_select='li.module-list-item>a', attr='href')


class ArticleListItem(Item):
    """
    eg: http://www.ruanyifeng.com/blog/essays/
    """
    target_item = TextField(css_select='div#alpha-inner li.module-list-item')
    title = TextField(css_select='li.module-list-item>a')
    href = AttrField(css_select='li.module-list-item>a', attr='href')


class BlogSpider(Spider):
    """
    针对博客源 http://www.ruanyifeng.com/blog/archives.html 的爬虫
    这里为了模拟ua，引入了一个ruia的第三方扩展
        - ruia-ua: https://github.com/ruia-plugins/ruia-ua
        - pipenv install ruia-ua
        - 此扩展会自动为每一次请求随机添加 User-Agent
    """
    # 设置启动URL
    start_urls = ['http://www.ruanyifeng.com/blog/archives.html']
    # 爬虫模拟请求的配置参数
    request_config = {
        'RETRIES': 3,
        'DELAY': 0,
        'TIMEOUT': 20
    }
    # 请求信号量
    concurrency = 10
    blog_nums = 0

    async def parse(self, res):
        items = await alist(ArchivesItem.get_items(html=res.html))
        self.mongo_db = MotorBase(loop=self.loop).get_db()
        for item in items:
            # 随机休眠
            self.request_config['DELAY'] = random.randint(5, 10)
            yield Request(
                item.href,
                callback=self.parse_item,
                request_config=self.request_config
            )

    async def parse_item(self, res):
        items = await alist(ArticleListItem.get_items(html=res.html))
        for item in items:
            # 已经抓取的链接不再请求
            is_exist = await self.mongo_db.source_docs.find_one({'url': item.href})
            if not is_exist:
                # 随机休眠
                self.request_config['DELAY'] = random.randint(5, 10)
                yield Request(
                    item.href,
                    callback=self.save,
                    metadata={'title': item.title},
                    request_config=self.request_config
                )

    async def save(self, res):
        # 好像有两个url一样 原本的博客总数1725 在入库后变成了1723
        data = {
            'url': res.url,
            'title': res.metadata['title'],
            'html': res.html
        }

        try:
            await self.mongo_db.source_docs.update_one({
                'url': data['url']},
                {'$set': data},
                upsert=True)
        except Exception as e:
            self.logger.exception(e)


if __name__ == '__main__':
    BlogSpider.start(middleware=middleware)
