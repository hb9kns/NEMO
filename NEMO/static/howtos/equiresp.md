# NEMO/FIRST-Lab, Short Manual for Equipment Responsibles

Equipment responsibles have some additional permissions in [NEMO][nemo]:
after login, the toolbar at the top will display an additional
`Administration` pull-down menu reserved for FIRST-Lab staff (FTT members).
*Please keep in mind all activity is logged by the system; if in doubt, ask*
the [NEMO responsible][nemoresp] before doing anything you don't understand.

## Alerts

Alerts are messages displayed at NEMO's main page after login.
In general, they are issued by FTT members, but there might be
cases where it makes sense for equipment responsibles to alert
all users logging in to NEMO.
The `Alert` page should be self-explanatory.

## Email (inactive)

The `Email` page allows to send a message to all users, to those who are
qualified for a tool, work on a specific project, or bill to a specific
account (currently unused in NEMO/FIRST-Lab). *However, the required forms
have not yet been set up, and therefore cannot be used at this moment.*

## Maintenance (inactive)

The `Maintenance` page permits to display maintenance state of all tools.
This is not yet used.

## Tool Qualifications

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

## Detailed Administration

This selection switches view to an internal Django page, the system
running NEMO. The only selection available to equipment responsibles is
the `Tools/Change` page, which allows to fully modify any tool (equipment);
therefore, be **even more careful when using this view** as you could
change or remove much more data (although recoverable with some work)
than with the `Tool Qualification` page alone.

*Equipment responsibles should use this view only after additional
instruction by FIRST-Lab staff, and it is currently not yet needed.*

You can leave this internal view by clicking on `VIEW SITE` at the
top right; you may also completely log out from NEMO by clicking
on `LOG OUT` there.

---

[nemo]: https://nemo.first.ethz.ch "NEMO/FIRST-Lab main site"
[nemoresp]: mailto:yargo.bonetti@first.ethz.ch "Yargo Bonetti / 37541"

*2020-1-13/Y.Bonetti*
