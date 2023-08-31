from datetime import datetime
import scrapy
from scrapy.http import JsonRequest
from siteparser.items import DoctorAppointmentItem, DoctorClinicItem, DoctorSpecItem, DoctorItem


class DoctorSpider(scrapy.Spider):
    name = 'doctor'
    base_url = 'https://gorzdrav.spb.ru/_api/api/v2'
    allowed_domains = ['gorzdrav.spb.ru']

    def __init__(self, district=None, clinics=None, specs=None, doctors=None):
        super().__init__()
        self.district = int(district)
        self.clinics = list(map(int, clinics.split(','))) if clinics else None
        self.specs = list(specs.split(',')) if specs else None
        self.doctors = list(doctors.split(',')) if doctors else None

        self.headers = {
            'Referer': 'https://gorzdrav.spb.ru/service-free-schedule',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': 1
        }

    def start_requests(self):
        if self.clinics is None or self.district is None:
            return

        yield JsonRequest(url=f'{self.base_url}/shared/district/{self.district}/lpus',
                          callback=self.parse_clinics,
                          cb_kwargs={},
                          dont_filter=True,
                          headers=self.headers)
        pass

    def parse_clinics(self, response):
        self.headers['token'] = response.headers.get('token')
        for clinic in response.json().get('result', []):
            if clinic.get('id') in self.clinics:
                clinic_item = DoctorClinicItem(
                    id=clinic.get('id'),
                    name=clinic.get('lpuFullName')
                )
                yield from self.start_specs_requests(clinic_item)
        pass

    def start_specs_requests(self, clinic: DoctorClinicItem):
        yield JsonRequest(url=f'{self.base_url}/schedule/lpu/{ clinic.id }/specialties',
                          callback=self.parse_specs,
                          cb_kwargs={'clinic': clinic},
                          dont_filter=True,
                          headers=self.headers)
        pass

    def parse_specs(self, response, clinic: DoctorClinicItem):
        self.headers['token'] = response.headers.get('token')
        for spec in response.json().get('result', []):
            if self.specs is None or spec.get('id') in self.specs:
                spec_item = DoctorSpecItem(
                    id=spec.get('id'),
                    name=spec.get('name')
                )
                yield from self.start_doctors_requests(clinic, spec_item)
        return

    def start_doctors_requests(self, clinic: DoctorClinicItem, spec: DoctorSpecItem):
        yield JsonRequest(url=f'{self.base_url}/schedule/lpu/{ clinic.id }/speciality/{spec.id}/doctors',
                          callback=self.parse_doctors,
                          cb_kwargs={'clinic': clinic, 'spec': spec},
                          dont_filter=True,
                          headers=self.headers)
        pass

    def parse_doctors(self, response, clinic: DoctorClinicItem, spec: DoctorSpecItem):
        self.headers['token'] = response.headers.get('token')
        for doc in response.json().get('result', []):
            if self.doctors is None or doc.get('id') in self.doctors:
                doc_item = DoctorItem(
                    id=doc.get('id'),
                    name=doc.get('name'),
                    comment=doc.get('comment')
                )
                yield from self.start_appoint_requests(clinic, spec, doc_item)
        pass

    def start_appoint_requests(self, clinic: DoctorClinicItem, spec: DoctorSpecItem, doc: DoctorItem):
        yield JsonRequest(url=f'{self.base_url}/schedule/lpu/{clinic.id}/doctor/{doc.id}/appointments',
                          callback=self.parse_appoint,
                          cb_kwargs={'clinic': clinic, 'spec': spec, 'doc': doc},
                          dont_filter=True,
                          headers=self.headers)
        pass

    def parse_appoint(self, response, clinic: DoctorClinicItem, spec: DoctorSpecItem, doc: DoctorItem):
        self.headers['token'] = response.headers.get('token')
        for app in response.json().get('result', []):
            item = DoctorAppointmentItem(
                clinic=clinic,
                speciality=spec,
                doctor=doc,
                date=datetime.fromisoformat(app.get('visitStart')),
                address=app.get('address'),
                room=app.get('room')
            )
            self.logger.info(item)
            yield item
        pass

    def parse(self, response, **kwargs):
        pass
