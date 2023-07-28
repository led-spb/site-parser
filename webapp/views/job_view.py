import dataclasses
import datetime
import itertools
from functools import reduce
from gettext import gettext
from typing import List
import wtforms
import humanize
from flask import request, redirect, flash
from flask_admin import expose
from flask_admin.form import BaseForm, JSONField
from flask_admin.helpers import get_redirect_target
from flask_admin.model import BaseModelView
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.model.template import EndpointLinkRowAction

from webapp.models import JobModel, SpiderModel
from webapp.services import JobService


@dataclasses.dataclass
class JobDto:
    id: str
    spider: str
    trigger: str
    params: str
    settings: str


class JobModelView(BaseModelView):
    edit_modal = True
    create_modal = True
    details_modal = True
    can_view_details = True

    column_formatters = {
        'next_run': lambda v, c, m, p: m.next_run.strftime('%d.%m.%Y %H:%M'),
        'statistics.request_bytes': lambda v, c, m, p: humanize.naturalsize(m.statistics.request_bytes),
        'statistics.response_bytes': lambda v, c, m, p: humanize.naturalsize(m.statistics.response_bytes),
        'statistics.start_time': lambda v, c, m, p: m.statistics.start_time.strftime('%d.%m.%Y %H:%M:%S'),
        'statistics.finish_time': lambda v, c, m, p: m.statistics.finish_time.strftime('%d.%m.%Y %H:%M:%S'),
        'statistics.elapsed_time': lambda v, c, m, p: humanize.naturaldelta(datetime.timedelta(seconds=m.statistics.elapsed_time))
    }

    column_labels = {
        'spider.name': 'Spider',
        'statistics.start_time': 'Start time',
        'statistics.finish_time': 'Finish time',
        'statistics.elapsed_time': 'Elapsed',
        'statistics.item_scraped_count': 'Scrapped items',
        'statistics.item_dropped_count': 'Dropped dropped',
        'statistics.http_requests': 'Requests',
        'statistics.http_success_requests': 'Success',
        'statistics.http_error_requests': 'Error',
        'statistics.request_bytes': 'Sent bytes',
        'statistics.response_bytes': 'Received bytes',
    }
    column_details_list = [
        'spider.name',
        'trigger',
        'next_run',
        'statistics.start_time',
        'statistics.finish_time',
        'statistics.elapsed_time',
        'statistics.item_scraped_count',
        'statistics.item_dropped_count',
        'statistics.http_requests',
        'statistics.http_success_requests',
        'statistics.http_error_requests',
        'statistics.request_bytes',
        'statistics.response_bytes',
    ]

    column_extra_row_actions = [
        EndpointLinkRowAction('fa fa-play glyphicon glyphicon-play', '.start_job')
    ]

    list_template = 'jobs/list.html'
    details_modal_template = 'default/modal_details.html'

    def __init__(self, model, job_service: JobService, spider_list: List[SpiderModel], name=None, category=None,
                 endpoint=None, url=None, static_folder=None,
                 menu_class_name=None, menu_icon_type=None, menu_icon_value=None):
        self.job_service = job_service
        self.spider_list = spider_list

        super().__init__(model, name, category, endpoint, url, static_folder, menu_class_name, menu_icon_type,
                         menu_icon_value)

    @expose("/start", methods=['GET'])
    def start_job(self):
        id = get_mdict_item_or_list(request.args, 'id')
        model = self.get_one(id)
        self.job_service.start_job(id)

        flash(gettext('Job was successfully started.'), 'success')
        return_url = get_redirect_target() or self.get_url('.index_view')
        return redirect(return_url)

    def get_pk_value(self, model: JobModel):
        return model.id

    def scaffold_list_columns(self):
        return ['spider.name', 'trigger', 'next_run']

    def scaffold_sortable_columns(self):
        pass

    def scaffold_form(self):
        class JobForm(BaseForm):
            id = wtforms.fields.HiddenField()
            spider = wtforms.fields.SelectField(choices=[(x.name, x.name) for x in self.spider_list])
            trigger = wtforms.fields.StringField()
            params = JSONField()
            settings = JSONField()
        return JobForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        total_it, job_it = itertools.tee(self.job_service.get_jobs(), 2)
        total = reduce(lambda acc, x: acc + 1, total_it, 0)
        return total, list(job_it)

    def edit_form(self, obj=None):
        obj = JobDto(id=obj.id, spider=obj.spider.name, trigger=obj.trigger, params=obj.spider.params,
                     settings=obj.spider.settings)
        return super().edit_form(obj)

    def get_one(self, id) -> JobModel:
        return self.job_service.get_job(id, detailed=True)

    def create_model(self, form):
        return True

    def update_model(self, form: BaseForm, model: JobModel):
        data = form.data

        self.job_service.update_job(
            model.id,
            spider_name=data.get('spider'),
            trigger=data.get('trigger'),
            params=data.get('params') if data.get('params', '') != '' else None,
            settings=data.get('settings') if data.get('settings', '') != '' else None
        )
        return True

    def delete_model(self, model):
        self.job_service.remove_job(model.id)
        return True

    def _create_ajax_loader(self, name, options):
        pass
