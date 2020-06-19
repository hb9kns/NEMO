# NEMO/FIRST-Lab, Short Manual for Equipment Responsibles

Equipment responsibles have some additional permissions in [NEMO][nemo]:
after login, the toolbar at the top will display an additional
`Administration` pull-down menu reserved for FIRST-Lab staff (FTT members).
*Please keep in mind all activity is logged by the system; if in doubt, ask*
the [NEMO responsible][nemoresp] before doing anything you don't understand.

## Special bookings

There are additional projects available to equipment responsibles:

- `_MAINTENANCE` is to be used for work on equipment; if it is out of order,
  please schedule an outage as well, which makes it clearly visible to users
- `_TRAINING` for, well, trainings...

Equipment responsibles will see an extra button "Schedule an outage"
in the calendar pane, to mark a tool as being unavailable.
These entries can be moved and modified like bookings, and
in addition, they can be modified under "Detailed Administration"
explained further down.

## Administration

<!--
### Alerts (inactive)

Alerts are messages displayed at NEMO's main page after login.
In general, they are issued by FTT members, but there might be
cases where it makes sense for equipment responsibles to alert
all users logging in to NEMO.
The `Alert` page should be self-explanatory.

*Due to date/time entry issues, this is not yet working.*
FIRST-Lab team members can use the `Alert` section in the
"Detailed Administration" pull-down.
-->

### Email

The `Email` page allows to send a message to all users,
responsibles, or to those who are
qualified for a tool, work on a specific project, or bill to a specific
account (yet unused in NEMO/FIRST-Lab).

Please note: Mentors belong to the project "_MENTOR" which
can be selected to send a message to all of them.

### Maintenance (inactive)

The `Maintenance` page permits to display maintenance state of all tools.
This is not yet used.

### Tool Qualifications

The `Tool Qualifications` page allows to add or remove users *in batch*
to/from the list of one or several tools (equipment).
**This is quite powerful, therefore please be careful when using it!**
Responsibles are allowed to change data for any equipment, but should
only do it for their own or in agreement with the other responsibles,
similar to good practice on the `flresp` file share.

To change qualifications, first select the appropriate equipment (tool)
by typing its name into the `Search for tool` field at the right, then
clicking onto the (correct!) tool in the list displayed.

Next, start typing the name of the first user to be added or removed
from the list for this tool (equipment) into the `Search for user`
field at the left, and click onto the correct user name in the list.
The user name will then appear as a button below the search field,
and you can start typing the next user's name. By clicking on a user's
button, you can remove it, if you added it by mistake.

After selecting all the required user names, you can click either the
`Qualify users` at the left to add those users to the list of the selected
tool (equipment), or the `Disqualify users` at the right to remove them.

Please note: it is technically well possible for equipment responsibles
to add (qualify) themselves for any equipment ...

### User directory

This page displays a list of all active users and their affiliations (group).

In addition, equipment responsibles are marked in _green_ and
listed a second time in an additional table at the end of the page.

### Reservation Abuse

This page allows to display reservations cancelled by users, to check
whether somebody is repeatedly blocking equipment for others without
using it.

The cancellation horizon allows to ignore all bookings cancelled *earlier*
than this many hours before their start. (E.g if this is set to 3 hours,
then no booking should be reported which has been cancelled any time
earlier than 3 hours before the start time.)

The selection parameters are still work in progress:

- The "Cancellation penalty" field is not correctly displaying its value.
(However, there is no need to modify it, therefore simply ignore it.)
- There is a glitch in the code populating the dates: please click into
the "Starting" and "Ending" fields and manually choose dates, before
generating the report; otherwise, you will get an empty one.

### Detailed Administration

This selection switches view to an internal Django page, the system
running NEMO. Not all pages are available to equipment responsibles.
It can be left by clicking on `VIEW SITE` at the top right;
one may also completely log out from NEMO by clicking on `LOG OUT` there.

#### Scheduled outages Add/Change

This permits to change scheduled outages set in the Calendar view,
e.g if start or end points should be set to a specific time not
easily attainable in the Calendar view.

It is also possible to add new entries; however, this is more tedious
and error-prone than through the Calendar and therefore not recommended.

In this view, you can also manually enter begin and end times, which may
be more practical than pulling the corresponding entrie across calendar
panes. To make use of this, create an outage anywhere in the calendar,
then switch to the detailed administration and edit/enter the correct
dates/times.

#### Tools Change

This allows to fully modify any tool (equipment);
therefore, be **even more careful when using this view** as you could
change or remove much more data (although recoverable with some work)
than with the `Tool Qualification` page alone.

*Equipment responsibles should use this view only after additional
instruction by FIRST-Lab staff, and it is currently not yet needed.*

---

[nemo]: https://nemo.first.ethz.ch "NEMO/FIRST-Lab main site"
[nemoresp]: mailto:yargo.bonetti@first.ethz.ch "Yargo Bonetti / 37541"

*2020-02-14/Y.Bonetti*
