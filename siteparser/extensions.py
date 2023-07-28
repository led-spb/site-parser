import pickle

import redis
from scrapy import Spider
from scrapy.statscollectors import MemoryStatsCollector


class RedisStatsCollector(MemoryStatsCollector):
    def __init__(self, crawler):
        super().__init__(crawler)
        settings = crawler.settings
        self.redis_client = redis.Redis(settings.get('REDIS_HOST', 'localhost'), settings.getint('REDIS_PORT', 6379))
        self.redis_key_name = settings.get('REDIS_STATS_KEY')
        # self.encoder = ScrapyJSONEncoder().encode
        self.encoder = pickle.dumps

    def _persist_stats(self, stats, spider: Spider):
        self.redis_client.hset(
            name=self.redis_key_name, key=spider.name,  value=self.encoder(stats)
        )
