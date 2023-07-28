#!/bin/sh

cd $(dirname $0)
frontend/build

docker build --rm -t site-parser:latest .