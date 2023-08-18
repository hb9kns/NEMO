#!/bin/sh
target=../../../static/howtos/
CSS=first.css
BINDIR=./bin ./bin/poorkyll $CSS
cp -f $CSS *.html $target
