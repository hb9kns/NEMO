#!/bin/sh
# install NEMO from working directory into following venv directory:
NEMODIR=/var/local/nemo
NEMODB=nemo.db
PORT=12345

if test "$NEMODIR" = ""
then cat <<EOH
 Please set NEMODIR at beginning of script, e.g
 NEMODIR=/var/local/nemo
EOH
 exit 1
fi

echo :: making venv $NEMODIR
python3 -m venv $NEMODIR
. $NEMODIR/bin/activate

echo :: installing python packages
pip install wheel
# # following may not be necessary if gunicorn is installed on site:
# pip install gunicorn
pip install NEMO

export DJANGO_SETTINGS_MODULE=settings
export PYTHONPATH=$NEMODIR/

cp -f ./*.py $NEMODIR
if test -r $NEMODB
then cp -f $NEMODB $NEMODIR/$NEMODB
fi

mkdir -p $NEMODIR/logs
touch $NEMODIR/logs/django_error.log
cd $NEMODIR
ln -s lib/python3.*/site-packages/NEMO/migrations migrations

echo :: preparing django
# Run migrations to create or update the database
django-admin makemigrations NEMO
django-admin migrate
# Collect static files
django-admin collectstatic --no-input --clear

echo :: running gunicorn test server on localhost:$PORT
cd lib/python3.*/site-packages/
gunicorn --bind 0.0.0.0:$PORT NEMO.wsgi:application
