# NEMO/FIRST-Lab, Short Manual for Users

Laboratory and user management for [FIRST-Lab]( https://first.phys.ethz.ch)
is done on an instance of NEMO,
a web application based on Django/Python and SQL databases.

## Login/Logout

FIRST-Lab users can log in on [NEMO's main page][nemo]
provided they have a [D-PHYS account]( https://account.phys.ethz.ch/ )
from the Department of Physics, required not only for accessing NEMO,
but also for transferring data to/from FIRST-Lab equipment.

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
shows a calendar view into reservations and outage notifications.

### Tool pane

The pull-down menu at the top permits for selection of `Reservations`
(for reserving tools or moving reservations), `Usage` (displaying of past
usage), and `Specific user` (information about another user's reservation
and usage).

In case of `Reservations` and `Usage` the list of tools can be expanded 
or compressed with the buttons below the pull-down menu selector.
*Only those tools are displayed whose checkboxes are set* in the list,
*plus* the one which is selected (coloured background) for reservation.

### Calendar pane

The calendar pane allows for selection of `Day/Week/Month` views with the
buttons at the top right side. With the buttons `</>/Today` at the left,
the displayed time unit can be selected.

### Reserving a tool

To reserve a tool the user is qualified for, first select `Reservations`
in the left pane, and click onto the *name* of the tool so that it gets
a grey background (checkmark is not sufficient: this only *displays* the
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

## Tool control

The [Tool control][toolcontrol] also consists of two panes, the left one
being the same as for the calendar, while the right pane shows information
for the tool selected at the left side, with several buttons/tabs.

### Summary

This tab shows the current status of the selected tool, and if the
user is qualified, also a button for starting/ending use of the tool.
If another user is using the tool, you may be able to kick them off
on the following Details tab.

### Details

Information about equipment responsibles, location of the tool,
qualified users, resources the equipment may require, and past
information (tasks and comments) can be displayed.

If you have a reservation currently open and want to use the tool,
but another person already is occupying the tool, you may kick them
off by a link provided a the top of this page. Then you can start
your own use on the Summary tab.

### Report a problem

This can be used to inform the responsibles and other users about issues
with the tool. If possible, also send a message to the responsible(s).

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

---

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

[nemorepo]: https://github.com/hb9kns/NEMO "NEMO Github repository"
[nemo]: https://nemo.first.ethz.ch "NEMO/FIRST-Lab main page"
[calendar]: https://nemo.first.ethz.ch/calendar/ "reservation calendar"
[toolcontrol]: https://nemo.first.ethz.ch/tool_control/ "tool control"
[dashboard]: https://nemo.first.ethz.ch/status_dashboard/ "status dashboard"

*2020-06-11/Y.Bonetti*
