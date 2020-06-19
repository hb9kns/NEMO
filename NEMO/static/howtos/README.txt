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

1. edit markdown files, with suffix `.md`
2. `. /home/wwwnemo/public/NEMO/venv/bin/activate` (source script into shell)
3. `django-admin collectstatic`
4. `deactivate`
5. `chmod -R a+r /home/wwwnemo/public/NEMO/static`
5. `cd /home/wwwnemo/public/NEMO/static/howtos`
6. `poorkyll first.css`

---

*2020-2-18/Y.Bonetti*
