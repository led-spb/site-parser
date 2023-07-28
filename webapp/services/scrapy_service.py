import datetime
import inspect
import pickle
from multiprocessing import Process
from typing import Iterable, Any, Dict, Union

from redis.client import Redis
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings

from ..models import SpiderModel, SpiderStatsModel


class ScrapyExecutor:
    def __call__(self, name, settings, params):
        project_settings = get_project_settings()
        project_settings.update(settings, 'cmdline')
        if project_settings.getbool('DONT_RUN_SPIDER', False):
            return
        crawler = CrawlerProcess(project_settings)
        crawler.crawl(name, **params)
        crawler.start()
        pass


class ScrapyRunService:
    def __init__(self, executor: ScrapyExecutor) -> None:
        self.executor = executor

    def run_spider(self, name: str, settings: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Process:
        process = Process(
            target=self.executor,
            kwargs={'name': name, 'params': params, 'settings': settings})
        process.start()
        return process


class ScrapyService:
    def __init__(self, redis_client: Redis, redis_key: str) -> None:
        self.settings = get_project_settings()
        # self.executor = ScrapyExecutor()
        self.redis = redis_client
        self.redis_key = redis_key
        self.decoder = pickle.loads

    def get_spiders(self) -> Iterable[SpiderModel]:
        result = []
        loader = SpiderLoader(self.settings)
        for name in loader.list():
            spider_cls = loader.load(name)
            args_spec = inspect.getfullargspec(spider_cls.__init__)

            result.append(
                SpiderModel(
                    name=name,
                    params={arg: 'any' for arg in filter(lambda x: x != 'self', args_spec.args)}
                )
            )
        return result

    def get_spider_stats(self, spider: str, tz: datetime.tzinfo = datetime.timezone.utc) -> Union[SpiderStatsModel, None]:
        value = self.redis.hget(self.redis_key, spider)
        if value is None:
            return None

        stats = self.decoder(value)

        http_errors = 0
        http_success = 0
        for key, value in stats.items():
            if not key.startswith('downloader/response_status_count/'):
                continue
            http_code = int(key.split('/')[2])
            if 400 < http_code >= 200:
                http_errors = http_errors + value
            else:
                http_success = http_success + value

        return SpiderStatsModel(
            spider=spider,
            start_time=tz.fromutc(stats['start_time']),
            finish_time=tz.fromutc(stats['finish_time']),
            elapsed_time=stats.get('elapsed_time_seconds'),
            item_scraped_count=stats.get('item_scraped_count', 0),
            item_dropped_count=stats.get('item_dropped_count', 0),
            request_bytes=stats.get('downloader/request_bytes', 0),
            response_bytes=stats.get('downloader/response_bytes', 0),
            http_requests=stats.get('downloader/request_count'),
            http_success_requests=http_success,
            http_error_requests=http_errors
        )

    """def run_spider(self, name: str, settings: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Process:
        process = Process(
            target=self.executor,
            kwargs={'name': name, 'params': params, 'settings': settings})
        process.start()
        return process"""
