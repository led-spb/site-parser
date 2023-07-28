from typing import Dict, Any

from dependency_injector.wiring import Provide, inject
from flask.views import MethodView
from flask_smorest import Blueprint
import marshmallow as ma

from webapp import Container
from .spiders import SpiderSchema, SpiderStatsSchema
from ..services import JobService

blueprint = Blueprint('schedule', __name__)


class JobSchema(ma.Schema):
    id = ma.fields.String(required=False)
    trigger = ma.fields.String()
    spider = ma.fields.Nested(SpiderSchema())
    next_run = ma.fields.DateTime()
    statistics = ma.fields.Nested(SpiderStatsSchema())


class JobControlSchema(ma.Schema):
    action = ma.fields.String(required=True)


@blueprint.route('/api/scheduler/jobs')
class SchedulerApi(MethodView):
    @blueprint.response(200, JobSchema(many=True))
    @inject
    def get(self, job_service: JobService = Provide[Container.job_service]):
        return job_service.get_jobs(detailed=True)

    @blueprint.response(200, JobSchema)
    @blueprint.arguments(JobSchema, required=True)
    @inject
    def post(self, job, job_service: JobService = Provide[Container.job_service]):
        model = job_service.create_job(
            spider_name=job['spider']['name'],
            trigger=job['trigger'],
            settings=job['spider'].get('settings'),
            params=job['spider'].get('params')
        )
        return model


@blueprint.route('/api/scheduler/job/<job_id>')
class SchedulerJobApi(MethodView):
    @blueprint.response(204)
    @inject
    def delete(self, job_id :str, job_service: JobService = Provide[Container.job_service]):
        job_service.remove_job(job_id)

    @blueprint.response(200, JobSchema)
    @inject
    def get(self, job_id: str, job_service: JobService = Provide[Container.job_service]):
        return job_service.get_job(job_id, True)

    @blueprint.arguments(JobSchema)
    @blueprint.response(200, JobSchema)
    @inject
    def put(self, job_spec: Dict[str, Any], job_id: str, job_service: JobService = Provide[Container.job_service]):
        model = job_service.update_job(
            id=job_id,
            spider_name=job_spec['spider']['name'],
            trigger=job_spec['trigger'],
            params=job_spec['spider'].get('params'),
            settings=job_spec['spider'].get('settings')
        )
        return model

    @blueprint.arguments(JobControlSchema, required=True)
    @blueprint.response(200, JobSchema)
    @inject
    def post(self, control: Dict[str, Any], job_id: str, job_service: JobService = Provide[Container.job_service]):
        if control.get('action') == 'start':
            job_service.start_job(job_id)
        return job_service.get_job(job_id)
