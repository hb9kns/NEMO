# NEMO/FIRST-Lab, Short Manual for Users

Laboratory and user management for [FIRST-Lab]( https://first.phys.ethz.ch)
is done on an instance of [NEMO]( https://github.com/hb9kns/NEMO ),
which is a web application based on Django/Python and SQL databases.

## Login/Logout

FIRST-Lab users can log in on the [main page][nemo]
provided they have a [D-PHYS account]( https://account.phys.ethz.ch/ )
from the Department of Physics, required not only for accessing NEMO,
but also for transferring data to/from FIRST-Lab equipment.

They are then presented with the main view, allowing access to the booking
calendar, tool handling (using/releasing tools counted for billing),
and providing various possibilities for contacting staff and other users.

For logging out from NEMO, click onto your username (in parentheses) at the top right.

## Calendar for Booking

The [booking Calendar][calendar] consists of two panes. The left pane
lists the available tools or permits to see past usage, the right pane
shows a calendar view into reservations and outage notifications.

### Tool pane

The pull-down menu at the top permits for selection of `Reservations`
(for booking tools or moving reservations), `Usage` (displaying of past
usage), and `Specific user` (information about another user's reservation
and usage).

In case of `Reservations` and `Usage` the list of tools can be expanded 
or compressed with the buttons below the pull-down menu selector, and
only those tools are displayed whose checkboxes are selected in the list.

### Calendar pane

The calendar pane allows for selection of `Day/Week/Month` views with the
buttons at the top right side. With the buttons `</>/Today` at the left,
the displayed time unit can be selected.

### Booking a tool

To book a tool the user is qualified for, first select `Reservations`
in the left pane. Then in the right pane, select the correct calendar
view and click where the booking should start (or end), keep clicked,
drag to the end (or beginning) of the booking slot, and release.  If the
user participates in several projects, one must then be selected for
billing of the booking slot; if only one project is available, it will
be selected automatically.

The booking by default has the user's name as title. This can be changed
by clicking into the body of the booking entry.  The booking can be moved
around by clicking and holding its body, keeping clicked, and dragging it
to the target time; the duration can be changed by clicking and dragging
the small `=` mark at the bottom of the booking entry (appearing when
the cursor is inside of the entry).

Bookings can be cancelled with the `Cancel` button at the bottom of
the detailed view popping up when clicking its body (they remain in the
database, but will neither show up nor interfere with other bookings).

## Tool control

The [Tool control][toolcontrol] also consists of two panes, the left one
being the same as for the calendar, while the right pane shows information
for the tool selected at the left side, with several buttons/tabs.

### Summary

This tab shows the current status of the selected tool, and if the
user is qualified, also a button for starting/ending use of the tool.

### Details

Information about equipment responsibles, location of the tool,
qualified users, resources the equipment may require, and past
information (tasks and comments) can be displayed.

### Report a problem

This can be used to inform the responsibles and other users about
issues with the tool. *Currently this is still handled by e-mail.*

### Post a comment

This can be used to inform all users of the tool about observations
or (depending on the tool -- ask the responsibles!) status of the
equipment. But if something requires a (re)action by the responsibles,
report it as a problem, not just as a comment!

---

[nemo]: https://nemo.first.ethz.ch "NEMO/FIRST-Lab main page"
[calendar]: https://nemo.first.ethz.ch/calendar/ "booking calendar"
[toolcontrol]: https://nemo.first.ethz.ch/tool_control/ "tool control"

*2020-1-14/Y.Bonetti*
