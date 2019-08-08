#!/bin/sh
# copy localized files
for nn in Dockerfile settings.py startNEMO.sh
do /bin/cp -f ../our-nemo/$nn .
done
# build docker image
docker build --tag nemof -f Dockerfile .
