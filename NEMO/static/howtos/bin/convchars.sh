#!/bin/sh
# convert some special characters to HTML
sed -e 's/°/\&deg;/g
 s/ -- / \&mdash; /g
 s/§/\&sect;/g' | tr -c '
 -~	' :
# finish with translation of all other special chars (except whitespace) to :
