import pickle
from dataclasses import asdict
from typing import Iterable

from redis.client import Redis

from siteparser.items import BaseItem
from siteparser.pipelines import FormatItemExporter
from webapp.models import ItemModel


class ItemsService:
    def __init__(self, redis_api: Redis, redis_key: str) -> None:
        self.redis_api = redis_api
        self.redis_items_key = redis_key
        self.item_exporter = FormatItemExporter()
        pass

    def get_items_count(self) -> int:
        return self.redis_api.hlen(self.redis_items_key)

    def get_items(self, sort_by='created', reverse=False) -> Iterable[ItemModel]:
        data = self.redis_api.hgetall(self.redis_items_key)
        items = []
        for key, value in data.items():
            scrapy_item = pickle.loads(value)
            if not isinstance(scrapy_item, BaseItem):
                continue
            items.append(self._create_item_model(key.decode('utf-8'), scrapy_item))

        return sorted(items, key=lambda x: getattr(x, sort_by or 'created'), reverse=reverse)

    def _create_item_model(self, key: str, scrapy_item: BaseItem) -> ItemModel:
        return ItemModel(
                    key=key,
                    spider=scrapy_item.spider,
                    created=scrapy_item.created,
                    attributes=asdict(scrapy_item),
                    formatted=self.item_exporter.export_item(scrapy_item)
                )

    def get_by_key(self, key: str) -> ItemModel:
        value = self.redis_api.hget(self.redis_items_key, key)
        scrapy_item = pickle.loads(value)
        if not isinstance(scrapy_item, BaseItem):
            raise ValueError('Item with key not found')
        return self._create_item_model(key, scrapy_item)

    def remove_item(self, key: str) -> None:
        self.redis_api.hdel(self.redis_items_key, key)
