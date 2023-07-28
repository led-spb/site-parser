#!/bin/bash

cd $(dirname $0)

CRAWL_NAME=$1
if [ -z ${CRAWL_NAME:+x} ]; then
   echo "Usage: $(basename $0) crawl_name"
   exit 1
fi

# Common env
source .env
# Individual env
if [ -f ".${CRAWL_NAME}.env" ]; then
   source ".${CRAWL_NAME}.env"
fi

venv/bin/scrapy crawl $@