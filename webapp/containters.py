from dependency_injector import containers, providers
from redis.client import Redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore

import webapp.services


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=['webapp.api'])

    config = providers.Configuration()

    redis_client = providers.Factory(Redis, host=config.REDIS_HOST, port=config.REDIS_PORT.as_int())

    # Scheduler
    job_store = providers.Factory(
        RedisJobStore,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT.as_int(),
        jobs_key=config.REDIS_JOBS_KEY,
        run_times_key=config.REDIS_RUN_KEYS
    )
    scheduler = providers.Singleton(
        BackgroundScheduler,
        jobstores=providers.Dict(default=job_store)
    )
    executor = providers.Singleton(
        webapp.services.ScrapyExecutor
    )

    # Services
    items_service = providers.Singleton(
        webapp.services.ItemsService,
        redis_api=redis_client,
        redis_key=config.REDIS_ITEMS_KEY
    )
    scrapy_service = providers.Singleton(
        webapp.services.ScrapyService,
        redis_client=redis_client,
        redis_key=config.REDIS_STATS_KEY
    )
    scrapy_run_service = providers.Singleton(
        webapp.services.ScrapyRunService,
        executor=executor
    )
    job_service = providers.Singleton(
        webapp.services.JobService,
        scheduler=scheduler,
        scrapy_service=scrapy_service,
        scrapy_run_service=scrapy_run_service
    )
    spider_list = providers.Callable(
        lambda service: service.get_spiders(),
        scrapy_service
    )
