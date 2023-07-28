import itertools
from functools import reduce
from typing import List, Callable

from flask_admin.actions import action
from flask_admin.model import BaseModelView
from flask_admin.model.filters import BaseFilter
from markupsafe import Markup
from wtforms import Form

from webapp.models import ItemModel, SpiderModel
from webapp.services import ItemsService


class AttributeInListFilter(BaseFilter):

    def __init__(self, column, name, options=None, data_type=None, key_name=None):
        super().__init__(name, options, data_type, key_name)
        self.column = column

    def apply(self, query, value):
        pass

    def operation(self):
        return 'is'


class ItemModelView(BaseModelView):
    can_create = False
    can_edit = False
    details_modal = True
    can_view_details = True

    column_filters = (AttributeInListFilter('spider', 'spider'),)
    column_default_sort = [('created', True)]

    list_template = 'items/list.html'
    details_modal_template = 'default/modal_details.html'

    def _preformatted(view, context, model, name):
        return Markup(model.formatted.replace('\n', '<br>')) if model.formatted else None

    column_formatters = {
        'formatted': _preformatted,
        'created': lambda v, c, m, p: m.created.strftime('%d.%m.%Y %H:%M'),
    }

    def __init__(self, model, items_service: ItemsService, spider_list: List[SpiderModel], name=None, category=None,
                 endpoint=None, url=None, static_folder=None,
                 menu_class_name=None, menu_icon_type=None, menu_icon_value=None):
        self.items_service = items_service
        self.spider_list = [x.name for x in spider_list]
        self.column_filters[0].options = [(x.name, x.name) for x in spider_list]
        super().__init__(model, name, category, endpoint, url, static_folder, menu_class_name, menu_icon_type,
                         menu_icon_value)

    @action('remove', 'Remove items', 'Are you sure remove selected items?')
    def remove_items(self, ids):
        for item_id in ids:
            self.items_service.remove_item(item_id)
        pass

    def get_pk_value(self, model: ItemModel):
        return model.key

    def scaffold_list_columns(self):
        return ['spider', 'created', 'formatted']

    def scaffold_sortable_columns(self):
        return ['created']

    def scaffold_form(self):
        class ItemForm(Form):
            ...
        return ItemForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def get_list(self, page, sort_field, sort_desc, search, filters: List, page_size=None):
        _, filter_key, filter_value = filters[0] if len(filters) > 0 else (None, None, None)
        total_it, items_it = itertools.tee(
            filter(
                lambda item: filter_key is None or getattr(item, filter_key) == filter_value,
                self.items_service.get_items(sort_by=sort_field, reverse=sort_desc)
            ), 2
        )

        items = list(itertools.islice(items_it, page*page_size, (page+1)*page_size))
        total = reduce(lambda acc, x: acc+1, total_it, 0)
        return total, items

    def get_one(self, id):
        return self.items_service.get_by_key(id)

    def create_model(self, form):
        pass

    def update_model(self, form, model):
        pass

    def delete_model(self, model):
        self.items_service.remove_item(model.key)

    def _create_ajax_loader(self, name, options):
        pass
