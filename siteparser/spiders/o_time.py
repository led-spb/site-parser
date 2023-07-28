import scrapy
from datetime import datetime

from siteparser.items import SportEventItem


class OTimeSpider(scrapy.Spider):
    name = 'o-time'
    allowed_domains = ['reg.o-time.ru']
    start_urls = ['https://reg.o-time.ru/calendar']

    sport_names = {
        1: u'Лыжные гонки', 2: u'Бег', 3: u'Ориентирование', 8: u'Велоспорт', 9: u'Триатлон', 11: u'Плавание'
    }

    def __init__(self, sport_types: str = None):
        super().__init__()
        self.sport_types = list(map(int, sport_types.split(','))) if sport_types else []

    def parse(self, response, **kwargs):
        year = datetime.now().year
        for data in response.css('h2,.all'):

            if data.root.tag == 'h2':
                try:
                    year = int(data.root.text_content().split()[-1])
                except ValueError:
                    pass
                continue

            value_date = " ".join(data.css('.alldate font::text').getall()[:2]+[str(year)])
            current_date = datetime.strptime(value_date, '%d %b %Y')

            for event in data.css('.allbutton div'):
                sport_code = int(event.css('.alllogo > img::attr(alt)').get(default=0))
                if sport_code not in self.sport_types:
                    continue

                item = SportEventItem(
                    date=current_date,
                    sport_code=sport_code,
                    sport=self.sport_names.get(sport_code, u'Неизвестно'),
                    title=event.css('.allname').pop().root.text_content().strip(),
                    link=event.css('.allname > a::attr(href)').get(),
                    place=event.css('.allplace').pop().root.text_content()
                )
                yield item
        pass
