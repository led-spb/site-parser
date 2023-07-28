import datetime
from typing import Iterable, Any, Dict

from apscheduler.job import Job
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from webapp.models import SpiderModel, JobModel
from webapp.services import ScrapyService, ScrapyRunService


class JobService:
    def __init__(self, scheduler: BaseScheduler, scrapy_service: ScrapyService, scrapy_run_service: ScrapyRunService):
        self.scheduler = scheduler
        self.scrapy_service = scrapy_service
        self.scrapy_run_service = scrapy_run_service

    @staticmethod
    def _create_model(job: Job) -> JobModel:
        trigger = None
        if job.trigger and isinstance(job.trigger, CronTrigger):
            m = {f.name: f for f in job.trigger.fields}
            trigger = f'{m["minute"]} {m["hour"]} {m["day"]} {m["month"]} {m["day_of_week"]}'

        model = JobModel(
            id=job.id,
            trigger=trigger,
            next_run=job.next_run_time,
            spider=SpiderModel(name=job.kwargs['name'],
                               params=job.kwargs.get('params'),
                               settings=job.kwargs.get('settings'))
        )
        return model

    def get_jobs(self, detailed: bool = False) -> Iterable[JobModel]:
        for job in self.scheduler.get_jobs():
            yield self.get_job(job.id, detailed)
        pass

    def get_job(self, id: str, detailed: bool = False) -> JobModel:
        job = self.scheduler.get_job(id)
        if job is None:
            raise ValueError('Job is not found')
        model = self._create_model(job)
        if detailed:
            model.statistics = self.scrapy_service.get_spider_stats(model.spider.name, model.next_run.tzinfo)
        return model

    def remove_job(self, id: str) -> None:
        self.scheduler.remove_job(id)

    def create_job(self, spider_name: str, trigger: str,
                   params: Dict[str, Any] = None, settings: Dict[str, Any] = None) -> JobModel:
        arguments = {
                'name': spider_name,
                'settings': settings,
                'params': params
        }
        trigger = CronTrigger.from_crontab(trigger)
        res = self.scheduler.add_job(
            func=self.scrapy_run_service.run_spider,
            kwargs=arguments,
            trigger=trigger
        )
        return self._create_model(res)

    def update_job(self, id: str, spider_name: str, trigger: str,
                   params: Dict[str, Any] = None, settings: Dict[str, Any] = None) -> JobModel:
        arguments = {
                'name': spider_name,
                'settings': settings,
                'params': params
        }
        trigger = CronTrigger.from_crontab(trigger)
        self.scheduler.modify_job(job_id=id, kwargs=arguments)
        res = self.scheduler.reschedule_job(job_id=id, trigger=trigger)
        return self._create_model(res)

    def start_job(self, id: str) -> JobModel:
        self.get_job(id)
        job = self.scheduler.modify_job(id, next_run_time=datetime.datetime.now())
        return self._create_model(job)
