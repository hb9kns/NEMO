#!/bin/sh
# install NEMO from working directory into following venv directory:
NEMODIR=/var/local/nemo
NEMODB=nemo.db
# gunicorn listener
GLISTN=127.0.1.1:12345
# used for testing whether installation already took place
DONE=$NEMODIR/static

if test "$NEMODIR" = ""
then cat <<EOH
 Please set NEMODIR at beginning of script, e.g
 NEMODIR=/var/local/nemo
EOH
 exit 1
fi

echo :: making venv $NEMODIR
python -m venv $NEMODIR
. $NEMODIR/bin/activate
export DJANGO_SETTINGS_MODULE=settings
export PYTHONPATH=$NEMODIR/

if test -d $DONE
then echo :: already installed, skipping
else


 echo ::::: make sure everything is running on python3.6 at minimum :::::
 sleep 1
 echo :: installing python packages
 pip install wheel
#  # following may not be necessary if gunicorn is installed on site:
#  pip install gunicorn
 pip install NEMO

 cp -f ./*.py $NEMODIR
 cp -f /etc/ssl/certs/quovadis_global_ica_g2.crt $NEMODIR/quovadis.crt
 if test -r $NEMODB
 then cp -f $NEMODB $NEMODIR/$NEMODB
 fi

 mkdir -p $NEMODIR/logs
 touch $NEMODIR/logs/django_error.log
 cd $NEMODIR
 ln -s lib/python3.*/site-packages/NEMO/migrations migrations

 echo :: preparing django
#  Run migrations to create or update the database
 django-admin makemigrations NEMO
 django-admin migrate
#  Collect static files
 django-admin collectstatic --no-input --clear

fi

echo :: running gunicorn test server on $GLISTN
cd $NEMODIR/lib/python3.*/site-packages/
gunicorn --bind $GLISTN NEMO.wsgi:application
