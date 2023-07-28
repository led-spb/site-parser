from datetime import datetime, timedelta
import scrapy
from scrapy.http import JsonRequest
from siteparser.items import JournalEventItem, JournalEstimateItem, JournalTaskItem, JournalLessonItem, \
    JournalTaskFileItem, JournalStudent


class JournalSpider(scrapy.Spider):
    name = 'journal'
    allowed_domains = ['dnevnik2.petersburgedu.ru']

    def __init__(self, student=None, token=None):
        super().__init__()
        self.student = student
        self.token = token
        self.headers = {'X-JWT-Token': self.token,
                        'X-Requested-With': 'XMLHttpRequest', 'DNT': '1'}

    def start_requests(self):
        if self.headers.get('X-JWT-Token') is None:
            self.logger.error('Crawler not started. Please configure "token" parameters')
            return

        yield JsonRequest(url='https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list',
                          headers=self.headers,
                          callback=self.parse_students, dont_filter=True)
        pass

    def parse_students(self, response):
        items = response.json()
        for item in items.get('data', {}).get('items', []):
            edu = item.get('educations')[0]
            if self.student is not None and self.student != edu.get('education_id'):
                continue

            student = JournalStudent(
                id=edu.get('education_id'),
                surname=item.get('surname'),
                firstname=item.get('firstname'),
                middlename=item.get('middlename'),
                institution_name=edu.get('institution_name'),
                group_name=edu.get('group_name')
            )
            yield from self.start_student_requests(student)
        pass

    def start_student_requests(self, student: JournalStudent):
        yield JsonRequest(url=f'https://dnevnik2.petersburgedu.ru/api/journal/estimate/table?'
                              f'p_limit=5&'
                              f'p_educations%5B%5D={student.id}',
                          headers=self.headers,
                          callback=self.parse_estimates,
                          cb_kwargs={'student': student},
                          dont_filter=True)
        yield JsonRequest(url=f'https://dnevnik2.petersburgedu.ru/api/journal/acs/list?'
                              f'p_limit=5'
                              f'&p_education={student.id}',
                          headers=self.headers,
                          callback=self.parse_events,
                          cb_kwargs={'student': student},
                          dont_filter=True)
        yield JsonRequest(url=f'https://dnevnik2.petersburgedu.ru/api/journal/lesson/list-by-education?'
                              f'p_educations%5B%5D={student.id}&'
                              f'&p_datetime_from={datetime.now() - timedelta(days=14):%d.%m.%Y}'
                              f'&p_datetime_to={datetime.now():%d.%m.%Y}',
                          headers=self.headers,
                          callback=self.parse_tasks,
                          cb_kwargs={'student': student},
                          dont_filter=True)

    def parse_estimates(self, response, student: JournalStudent):
        items = response.json()
        for item in items.get('data', {}).get('items', []):
            yield JournalEstimateItem(
                id=item.get('id'),
                category=self.name,
                subject=item.get('subject_name'),
                date=datetime.strptime(item.get('date'), '%d.%m.%Y'),
                title=item.get('estimate_type_name'),
                estimate=item.get('estimate_value_name'),
                estimate_code=item.get('estimate_value_code'),
                comment=item.get('estimate_comment'),
                student=student
            )
        pass

    def parse_events(self, response, student: JournalStudent):
        items = response.json()
        for item in items.get('data', {}).get('items', []):
            yield JournalEventItem(
                id=item.get('identity', {}).get('id'),
                date=datetime.strptime(item.get('datetime'), '%d.%m.%Y %H:%M:%S'),
                category=self.name,
                event=item.get('direction'),
                student=student
            )
        pass

    def parse_tasks(self, response, student: JournalStudent):
        items = response.json()
        for item in items.get('data', {}).get('items', []):
            if len(item.get('tasks', [])) == 0:
                continue
            tasks = [JournalTaskItem(kind=t.get('task_kind_name'),
                                     name=t.get('task_name'),
                                     files=[
                                         JournalTaskFileItem(name=f.get('file_name'), uuid=f.get('uuid'))
                                         for f in t.get('files')
                                     ]
                                     ) for t in item.get('tasks')]
            yield JournalLessonItem(
                id=item.get('identity', {}).get('id'),
                category=self.name,
                subject=item.get('subject_name'),
                date=datetime.strptime(item.get('datetime_from'), '%d.%m.%Y %H:%M:%S'),
                title=item.get('content_name'),
                tasks=tasks,
                student=student
            )
        pass

    def parse(self, response, **kwargs):
        pass
