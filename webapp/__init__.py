import os

import flask_smorest
from flask import Flask
from flask_admin import Admin

from webapp.containters import Container
from scrapy.utils.project import get_project_settings

from webapp.models import ItemModel, JobModel, SpiderModel
from webapp.views import ItemModelView, JobModelView


def create_app() -> Flask:
    import webapp.api.items
    import webapp.api.spiders
    import webapp.api.scheduler

    container = Container()
    settings = get_project_settings()
    container.config.from_dict(dict(settings))

    assert container.config.REDIS_HOST() is not None

    app = Flask('webapp', static_url_path='/')
    # create_admin(app, container)

    app.config["API_TITLE"] = "Siteparser API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')

    scheduler = container.scheduler()
    scheduler.start()

    restapi = flask_smorest.Api(app)
    restapi.register_blueprint(webapp.api.items.blueprint)
    restapi.register_blueprint(webapp.api.spiders.blueprint)
    restapi.register_blueprint(webapp.api.scheduler.blueprint)
    return app


def create_admin(app: Flask, container: Container) -> None:
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app,
                  name='Parser',
                  # base_template='default/base.html',
                  template_mode='bootstrap4', url='/')
    admin.add_view(JobModelView(JobModel,
                                container.job_service(),
                                container.spider_list(),
                                name='Jobs', url='jobs'))
    admin.add_view(ItemModelView(ItemModel,
                                 container.items_service(),
                                 container.spider_list(),
                                 name='Items', url='items'))


if __name__ == '__main__':
    create_app().run()
