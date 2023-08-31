import datetime
from dataclasses import dataclass, field
from typing import List


@dataclass
class BaseItem:
    spider: str = None
    created: datetime.datetime = None

    id: str = None
    date: datetime.datetime = None
    category: str = None
    title: str = None
    message: str = None
    link: str = None

    template = """<b>{{category}}</b>
{% if date %}{{date}}{%- endif %}
{% if link %}<a href="{{link}}">{{title or message}}</a>{% else %}{{title or message}}{% endif %}
{% if title %}{{message}}{% endif %}
"""


@dataclass
class SportEventItem(BaseItem):
    sport_code: int = None
    sport: str = None
    place: str = None

    template = """<b>{{category}}</b>
<b>{{ date.strftime('%d.%m.%Y') }}: {{sport}}</b> {{place}}
{% if link %}<a href="{{link}}">{{title}}</a>{% else %}{{title}}{% endif %}
"""


@dataclass
class JournalStudent:
    id: int
    surname: str
    firstname: str
    middlename: str
    institution_name: str
    group_name: str


@dataclass
class JournalEstimateItem(BaseItem):
    subject: str = None
    comment: str = None
    estimate: str = None
    estimate_code: str = None
    student: JournalStudent = None

    template = """<b>{{subject}}</b>
<b>Дата</b>: {{date.strftime('%d.%m.%Y')}}
<b>{{title}}</b>: {{estimate}}
{% if comment %}{{comment}}{% endif %}"""


@dataclass
class JournalTaskFileItem:
    name: str
    uuid: str


@dataclass
class JournalTaskItem:
    kind: str
    name: str
    files: List[JournalTaskFileItem] = field(default_factory=lambda: [])


@dataclass
class JournalLessonItem(JournalEstimateItem):
    student: JournalStudent = None
    tasks: List[JournalTaskItem] = field(default_factory=lambda: [])
    template = """<b>{{subject}}</b>
<b>Дата</b>: {{date.strftime('%d.%m.%Y')}}
<b>Тема</b>: {{title}}
{%- for task in tasks or [] %}
<b>{{task.kind}}</b>: {{task.name or ''}}
{%- for file in task.files or [] %}
<a href='https://dnevnik2.petersburgedu.ru/api/filekit/file/download?p_uuid={{file.uuid}}'>{{file.name}}</a>
{%- endfor %}
{%- endfor %}"""


@dataclass
class JournalEventItem(BaseItem):
    event: str = None
    student: JournalStudent = None
    template = """<b>{{ student.firstname or ''}} {{ 'вход' if event == 'input' else 'выход' }}</b>
{{date.strftime('%d.%m.%Y %H:%M')}}"""


@dataclass
class DoctorClinicItem:
    id: str
    name: str


@dataclass
class DoctorSpecItem:
    id: str
    name: str


@dataclass
class DoctorItem:
    id: str
    name: str
    comment: str


@dataclass
class DoctorAppointmentItem(BaseItem):
    clinic: DoctorClinicItem = None
    speciality: DoctorSpecItem = None
    doctor: DoctorItem = None
    address: str = None
    room: str = None

    template = """<b>{{ clinic.name }}</b>
<b>Врач:</b> {{ doctor.name }} {{ doctor.comment or '' }}
<b>Специальность:</b> {{ speciality.name }} {{ address or '' }}

<b>Дата:</b> <a href="https://gorzdrav.spb.ru/service-free-schedule">{{ date.strftime('%d.%m.%Y %H:%M') }}</a>
"""
