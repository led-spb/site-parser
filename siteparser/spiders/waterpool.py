import scrapy
import re
from siteparser.items import BaseItem


class WaterpoolSpider(scrapy.Spider):
    name = 'waterpool'
    allowed_domains = ['directory.spb.ru']
    start_urls = ["https://directory.spb.ru/cp/"]

    def __init__(self):
        super().__init__()

    def parse(self, response, **kwargs):
        for value in response.css('.elementor-column .elementor-element.elementor-widget-uael-advanced-heading'):
            message = re.sub(r'(\s){2,}', ' ', value.root.text_content().strip())
            yield BaseItem(category=self.name, title=u'Информация', message=message, link=response.request.url)
        pass
