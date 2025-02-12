#!/bin/sh
# (2015,2019 YCB)
# change bindir according to your needs!
bindir=${BINDIR:-$HOME/bin}
if test "$1" = ""
then sfl=''
 echo ": no stylesheet used"
else if test -f "$1"
 then sfl="<link rel=\"stylesheet\" type=\"text/css\" href=\"$1\" />"
  echo ": using stylesheet $1"
 else cat <<EOU
 stylesheet '$1' missing!
 usage: $0 [<style>] [i]
  will generate files with .html suffix from all files with .md suffix,
  converting Markdown to HTML, and add a link to the stylesheet <style>,
  or include <style> in output if trailing "i" is present,
  or use no stylesheet if arguments are missing
 ( scripts mrkdwn.pl and convchars.sh must be present and executable
 in directory '$bindir' )
EOU
 exit
 fi
 case $2 in
 [iI]*) sfl="<style> `cat \"$1\"` </style>"
  echo ": including style in output"
  ;;
 ?*) echo ":: ignoring trailing argument $2" ;;
 esac
fi

for mf in *.md
do hf="${mf%md}html"
 echo ": $mf/html :"
 echo '<html><head><title>' >"$hf"
 grep '^#' "$mf" | head -n 1 | sed -e 's/#* */  /' | tee -a "$hf"
 echo '</title>' >>"$hf"
 echo "$sfl</head>" >>"$hf"
 echo '<body>' >>"$hf"
 $bindir/convchars.sh <$mf | $bindir/mrkdwn.pl >>"$hf"
 echo '</body></html>' >>"$hf"
 chmod a+r "$hf"
done
