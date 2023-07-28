from dependency_injector.wiring import Provide, inject
from flask.views import MethodView
from flask_smorest import Blueprint
import marshmallow as ma

from webapp import Container
from webapp.services import ItemsService

blueprint = Blueprint('items', __name__)


class ItemsFilterSchema(ma.Schema):
    spider = ma.fields.String(required=False)


class ItemSchema(ma.Schema):
    key = ma.fields.String(required=True)
    spider = ma.fields.String(required=True)
    created = ma.fields.DateTime()
    formatted = ma.fields.String()
    attributes = ma.fields.Dict()


@blueprint.route('/api/items')
class ItemsApi(MethodView):
    @blueprint.response(200, ItemSchema(many=True))
    @blueprint.arguments(ItemsFilterSchema, location='query', required=False)
    @inject
    def get(self, filter_spec, items_service: ItemsService = Provide[Container.items_service]):
        items_it = filter(self.make_filter(filter_spec), items_service.get_items(reverse=True))
        return list(items_it)

    @staticmethod
    def make_filter(filter_spec):
        spider = filter_spec.get('spider')

        def filter_func(item):
            return spider is None or item.spider == spider
        return filter_func


@blueprint.route('/api/items/<key>')
class ItemsByKeyApi(MethodView):
    @blueprint.response(204)
    @inject
    def delete(self, key, items_service: ItemsService = Provide[Container.items_service]):
        items_service.remove_item(key)
