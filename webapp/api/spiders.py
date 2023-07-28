from dependency_injector.wiring import Provide, inject
from flask.views import MethodView
from flask_smorest import Blueprint
import marshmallow as ma

from webapp import Container
from webapp.services import ScrapyService

blueprint = Blueprint('spiders', __name__)


class SpiderSchema(ma.Schema):
    name = ma.fields.String(required=True)
    settings = ma.fields.Dict(required=False)
    params = ma.fields.Dict(required=False)


class SpiderStatsSchema(ma.Schema):
    spider = ma.fields.String(required=True)
    start_time = ma.fields.DateTime(required=True)
    finish_time = ma.fields.DateTime(required=True)
    elapsed_time = ma.fields.Float(required=True)
    item_scraped_count = ma.fields.Integer()
    item_dropped_count = ma.fields.Integer()
    request_bytes = ma.fields.Integer()
    response_bytes = ma.fields.Integer()
    http_requests = ma.fields.Integer()
    http_success_requests = ma.fields.Integer()
    http_error_requests = ma.fields.Integer()


@blueprint.route('/api/spiders')
class SpidersApi(MethodView):
    @blueprint.response(200, SpiderSchema(many=True))
    @inject
    def get(self, scrapy_service: ScrapyService = Provide[Container.scrapy_service]):
        return scrapy_service.get_spiders()


@blueprint.route('/api/spider/<name>/stats')
class SpiderApi(MethodView):
    @blueprint.response(200, SpiderStatsSchema)
    @inject
    def get(self, name, scrapy_service: ScrapyService = Provide[Container.scrapy_service]):
        model = scrapy_service.get_spider_stats(name)
        return model


@blueprint.route('/api/spiders/run')
class SpiderRunApi(MethodView):
    @blueprint.arguments(SpiderSchema)
    @blueprint.response(204)
    @inject
    def post(self, spider, scrapy_service: ScrapyService = Provide[Container.scrapy_service]):
        #scrapy_service.run_spider(spider['name'], spider.get('settings'), spider.get('params'))
        pass
