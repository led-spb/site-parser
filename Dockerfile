FROM python:3.10-alpine

WORKDIR /app
RUN apk update && apk add --no-cache gcc libc-dev linux-headers libffi-dev
ADD ./requirements.txt /app/
RUN pip --no-cache-dir install -r requirements.txt
ADD ./scrapy.cfg ./gunicorn.conf.py /app/
ADD ./webapp /app/webapp
ADD ./siteparser /app/siteparser

ENTRYPOINT ["flask", "--app", "webapp"]
CMD ["run"]
