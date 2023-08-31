import datetime
import io
import logging
import hashlib
import pickle
from dataclasses import asdict
import requests
import redis
from scrapy.exceptions import DropItem
from scrapy.exporters import BaseItemExporter
from jinja2 import Environment
from scrapy.utils.serialize import ScrapyJSONEncoder

from siteparser.items import BaseItem


class FormatItemExporter(BaseItemExporter):
    def __init__(self, defaults=None):
        self.defaults = defaults or {}
        self.jinja = Environment()
        self.templates = {}
        super().__init__(dont_fail=False)

    def export_item(self, item: BaseItem):
        message = self.format_item(item)
        if message is not None:
            return message
        pass

    def format_item(self, item: BaseItem):
        if not hasattr(item, 'template'):
            return None
        template = self.templates.get(type(item))
        if template is None:
            template = self.jinja.from_string(item.template, globals=self.defaults)
            self.templates[type(item)] = template
        return template.render(asdict(item))


class UniquePipeline:
    def __init__(self, crawler) -> None:
        super().__init__()
        settings = crawler.settings
        self.redis_client = redis.Redis(settings.get('REDIS_HOST', 'localhost'), settings.getint('REDIS_PORT', 6379))
        self.redis_key_name = settings.get('REDIS_ITEMS_KEY')
        self.encoder = ScrapyJSONEncoder(sort_keys=True)

    def process_item(self, item: BaseItem, spider):
        item.spider = spider.name
        item.category = item.category or spider.name

        hash = self.item_hash(item)

        if self.redis_client.hexists(self.redis_key_name, hash):
            raise DropItem(f'Duplicated item')

        item.created = datetime.datetime.now()
        serialized = self.serialize_item(item)
        self.redis_client.hset(self.redis_key_name, hash, serialized)
        return item

    def item_hash(self, item: BaseItem):
        # data = str(hash(asdict(item, dict_factory=frozenset))).encode('ascii')
        data = self.encoder.encode(asdict(item)).encode('ascii')
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()

    @staticmethod
    def serialize_item(item: BaseItem):
        stream = io.BytesIO()
        pickle.dump(item, stream)
        stream.seek(0)
        return stream.read()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


class TelegramOutputPipeline:

    def __init__(self, crawler) -> None:
        self.crawler = crawler
        self.telegram_token = crawler.settings.get('TELEGRAM_TOKEN')
        self.telegram_chat_id = crawler.settings.get('TELEGRAM_CHAT_ID')
        self.exporter = None
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.exporter = FormatItemExporter(defaults={'category': spider.name})
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        message = self.exporter.export_item(item)
        if message is not None and self.telegram_token is not None:
            try:
                response = requests.request(
                    url=f'https://api.telegram.org/bot{ self.telegram_token }/sendMessage',
                    method='POST',
                    data={'chat_id': self.telegram_chat_id, 'parse_mode': 'HTML', 'text': message[:4096]}
                )
                logging.debug(response.text)
                response.raise_for_status()
            except BaseException:
                logging.error('Unable send notification')
        return item
