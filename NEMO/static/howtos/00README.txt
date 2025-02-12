# HowTos, Markdown files

## To Edit and Publish

The static files for NEMO/FIRST are hosted on the same server, therefore
we can create the HTML from the Markdown files in the target directory,
which automatically makes sure permissions are set correctly.
If we would generate them in this folder here, we would have to make
sure the permissions are set correctly in the published (target) folder,
which sometimes has failed.

`poorkyll` is a shell script running a simple Markdown
convertert on all `*.md` files in the current directory.
The scripts are located in folder `./bin/` and require
Perl and the usual shell stuff.

First edit markdown files with suffix `.md` then:

	cd /home/wwwnemo/public/NEMO
	. venv/bin/activate
	export PYTHONPATH="/home/wwwnemo/public/NEMO:$PYTHONPATH"
	export DJANGO_SETTINGS_MODULE=settings
	django-admin collectstatic
	deactivate
	chmod -R a+r /home/wwwnemo/public/NEMO/static
	cd /home/wwwnemo/public/NEMO/static/howtos
	PATH=bin:$PATH poorkyll first.css

---

*2020-8-10/Y.Bonetti*
