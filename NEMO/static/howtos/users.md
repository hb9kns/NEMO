# NEMO/FIRST-Lab, Short Manual

(for users and [equipment responsibles]( #equiresp ))

Laboratory and user management for [FIRST-Lab]( https://first.phys.ethz.ch)
is done on an instance of [NEMO,][nemorepo]
an open-source web application based on Django/Python and SQL databases.

## Login/Logout

FIRST-Lab users can log in on [NEMO's main page][nemo]
provided they have a [D-PHYS account]( https://account.phys.ethz.ch/ )
from the Department of Physics (required not only for accessing NEMO,
but also for transferring data to/from FIRST-Lab equipment).

They are then presented with the landing page, allowing access to the reservation
calendar, tool handling (using/releasing tools counted for billing),
and providing various possibilities for contacting staff and other users.

For logging out from NEMO, click onto your username (in parentheses) at the top right.
In case this is not present (on some mobile devices or specific browsers),
please go to the landing page (e.g by clicking onto "NEMO" in the
top left corner of any page), and then the "Logout" link at the bottom
of the page (with a red-white NO-ENTRY symbol).

## Calendar for Reservations

The [reservation Calendar][calendar] consists of two panes. The left pane
lists the available tools or permits to see past usage, the right pane
shows a calendar view into reservations, usage and outage notifications.
The left pane also provides a link for displaying one's own reservations.

### Tool pane

The pull-down menu at the top permits for selection of `Reservations`
(for reserving tools or moving reservations), `Usage` (displaying of past
usage), and `Specific user` (information about another user's reservation
and usage).

In case of `Reservations` and `Usage` the list of tools can be expanded 
or compressed with the buttons below the pull-down menu selector.
*Only those tools are displayed whose checkboxes are set* in the list,
*plus* the one which is selected (yellow background) for reservation.
**Please make sure to select the correct tool for making reservations:**
it must have a yellow background in the tool pane!

Tools marked "[staff only]" can only be viewed/accessed by staff.

### Calendar pane

The calendar pane allows for selection of `Day/Week/Month` views with the
buttons at the top right side. With the buttons `</>/Today` at the left,
the displayed time unit can be selected.

**If the background of this pane is red, you have selected a shutdown tool.**
Please make sure to select the correct tool!
Equipment responsibles may reserve a shutdown tool, though,
to permit planning of maintenance works.

Please also keep in mind that some tools are always marked as shut down,
in particular the `_no-tool_` -- therefore you
should make sure to select another tool before making reservations.

### Reserving a tool

To reserve a tool the user is qualified for, first select `Reservations`
in the left pane, and click onto the *name* of the tool so that it gets
a yellow background (checkmark is not sufficient: this only *displays* the
tool's reservations). In the right pane, select the correct calendar
view and click where the reservation should start (or end), keep clicked,
drag to the end (or beginning) of the reservation slot, and release.  If the
user participates in several projects, one must then be selected for
billing of the reservation slot; if only one project is available, it will
be selected automatically.

The reservation by default has the user's name as title. This can be changed
by clicking into the body of the reservation entry. The reservation can be moved
around by clicking and holding its body, keeping clicked, and dragging it
to the target time; the duration can be changed by clicking and dragging
the small `=` mark at the bottom of the reservation entry (appearing when
the cursor is inside of the entry).

Reservations can be cancelled with the `Cancel` button at the bottom of
the detailed view popping up when clicking its body (they remain in the
database, but will neither show up nor interfere with other reservations).

There are some special "tools" for use by the team (announcement, planning
etc). Specifically, the `_no-tool_` is preselected in some views.
It has a reservation limit of 1 minute, therefore any reservation attempt
by normal users for this tool will fail with a warning.
It is normally also marked as "shutdown" (with red flame symbol), so that
it cannot be reserved anyway. (In certain situations it might still be
possible for equipment responsibles to reserve it, though.)

Please remember to always click the name of the tool to be reserved
before making a reservation in the calendar pane!

## Tool control

The [Tool control][toolcontrol] also consists of two panes, the left one
being the same as for the calendar, while the right pane shows information
for the tool selected at the left side, with several buttons/tabs.

### Summary

This tab shows the current status of the selected tool, and if the
user is qualified, also a button for starting/ending use of the tool.
If another user is using the tool, you may be able to kick them off
on the following Details tab, depending on the tool's configuration.

If a tool is in use, you may see a section "to announce pending usage",
if the tool is configured to allow this. In this case, you can still
select the project you want the usage billed on and the click on the
"Note pending usage" button, which puts you in the queue for this tool.
When the former user stops using the tool, you will immediately start
using it, i.e taking over the tool. If a tool is controlled remotely by
NEMO, this will also prevent it from being switched off between usages.

### Details

Information about equipment responsibles, location of the tool,
qualified users, resources the equipment may require, and past
information (tasks and comments) can be displayed.

If you have a reservation currently open and want to use the tool,
but another person already is occupying the tool, you may kick them
off by a link provided a the top of this page. Then you can start
your own use on the Summary tab.

This page also shows the physical access level required for making
a reservation. If you lose access to a certain area (e.g by not
coming to FIRST during 6 months), you will get a warning about
lack of permission when trying to make a reservation.

### Report a problem

This can be used to inform the responsibles and other users about issues
with the tool. A message will also be sent by e-mail.

### Post a comment

This can be used to inform all users of the tool about observations
or (depending on the tool -- ask the responsibles!) status of the
equipment. But if something requires a (re)action by the responsibles,
report it as a problem, not just as a comment, and send them a message!

## Status dashboard

[This page][dashboard] shows the status of all equipment, filtered by
tools in use (i.e where somebody is currently billed for using it),
idle or unavailable ones, or just those where the user is qualified for.

The tool names are links into the corresponding "Tool control" page.
This allows to e.g select "my tools" for easy filtered access to reservation
and tool control.

On the Area occupancy page, you can see a weekly plot of cleanroom
occupation as reported by the electronic login system.
This is a moving average in bins of 10 min each.
It may give you an idea when the lab on average has low/high load.

## Notes

### Team members

At the end of the tool list (enjoy the pun!), team member names are
added. They might be used for announcing absence or other availability
issues for the FIRST-Lab team. However, you cannot reserve or use them...

### Deep links (bookmarks) for specific tools

You can create/save deeplinks for specific tools (equipment) and certain
views, listed on the "Tool control" menu in the "Details and History" tab.
(To save, right click or directly copy, depending on the browser and
operating system.)

### Server time at page generation

The server time is displayed at the top right corner.  This is not
updating, but reflects the time when the page displayed was generated
on the server.

---

<a id="equiresp"></a>
## Equipment Responsibles

Equipment responsibles have some additional permissions in [NEMO][nemo]:
there is (small) pull-down menu "Equi.resp" in the toolbar at the top.
Currently it contains two entries:

- Email broadcast for tools,
  allowing to send e-mail for all tools you are responsible for
- Tool qualifications,
  allowing to (dis)qualify users to/from tools you are responsible for

*Please keep in mind all activity is logged by the system; if in doubt, ask*
the [NEMO responsible][nemoresp] before doing anything you don't understand.

### Reservations and special projects

Equipment responsibles can reserve any tool, even if they are not
qualified for them in NEMO, the reason being that they might have to
reserve another (adjacent) tool for blocking lab space.
However, unless they are qualified, they cannot *use* the tool.

They can also select tools which are shut down, and therefore should
make sure not to have selected the `_no-tool_` which is used as a dummy;
otherwise, reservations may silently disappear.

There are additional projects available to equipment responsibles:

- `_MAINTENANCE` is to be used for work on equipment; if it is out of order,
  please schedule an outage as well, which makes it clearly visible to users
- `_TRAINING` for, well, trainings...
- `_MENTORING` must not be used except for reserving a tool while mentoring;
  however, you cannot *use* a tool on this project; please use `_TRAINING`
  for this case

Equipment responsibles will see an extra button "Schedule an outage"
in the calendar pane, to mark a tool as being unavailable.
These entries can be moved and modified like bookings, and
in addition, they can be modified under "Detailed Administration"
explained further down.

### Email

The `Email` page allows you to send a message to all users for tools
you are responsible for.

To resolve an issue (e.g to mark a tool as available after a shut-down),
select the "Resolve" radio button, note the corrective actions, and
select a Resolution category (if applicable), then click on "Save task".
(A shortcut for this can also be accessed through the Tool control menu,
by clicking on the wrench symbol in case of open issues, which will
display links on "update or resolve this task".)

### Tool Qualifications

The `Tool Qualifications` page allows to add or remove users *in batch*
to/from the list of one or several tools (equipment) you are responsible for.
**This is quite powerful, therefore please be careful when using it!**

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

Most tools are configured in such a way that qualifying a user will
automatically also grant them access to the required physical area.
Therefore please double-check user names before adding them!

---

[nemoresp]: mailto:yargo.bonetti@first.ethz.ch "Yargo Bonetti / 37541"
[nemorepo]: https://github.com/hb9kns/NEMO "NEMO Github repository"
[nemo]: https://nemo.first.ethz.ch "NEMO/FIRST-Lab main page"
[calendar]: https://nemo.first.ethz.ch/calendar/ "reservation calendar"
[toolcontrol]: https://nemo.first.ethz.ch/tool_control/ "tool control"
[dashboard]: https://nemo.first.ethz.ch/status_dashboard/ "status dashboard"

*2020-12-09/Y.Bonetti*
