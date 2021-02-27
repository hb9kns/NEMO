import re
from xlsxwriter.workbook import Workbook
from xlsxwriter.utility import xl_rowcol_to_cell, xl_range

from datetime import timedelta, date
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from NEMO.utilities import parse_start_and_end_date
from NEMO.models import User, Tool, Project, Account, UsageEvent, Reservation

def allowed_tools(request):
	""" tools for which the requester is allowed to view usage events"""
# reusing permissions: those allowed to change events can view all tools
	if request.user.has_perm('NEMO.change_usageevent'):
		return Tool.objects.all()
# others can just view tools where they are primary responsibles
	else:
		return Tool.objects.filter(primary_owner=request.user)

def get_tool_span_events(request, eventtype, tool, begin, end):
	""" get all usage events ending after begin and before or at end
	    (type selects between 'reservation' or 'usage')
	    and add line containing sum of all event durations at end """
	toolevents = []
	if Tool.objects.get(pk=tool) in allowed_tools(request):
		if eventtype == 'reservation':
			events = Reservation.objects.filter(tool=tool, end__gt=begin, end__lte=end, cancelled=False, shortened=False).order_by('start')
		else:
			events = UsageEvent.objects.filter(tool=tool, end__gt=begin, end__lte=end).order_by('start')
		toolsum = 0
		for event in events:
			try:
				fullname = event.user.last_name + " " + event.user.first_name
			except:
				fullname = "(unknown user)"
			try:
				projectname = event.project.name
			except:
				projectname = "(unknown project)"
			try:
				affiliation = event.user.affiliation.name
			except:
				affiliation = "(unknown affiliation)"
			if eventtype == 'reservation':
				try:
					remarks = event.title
				except:
					remarks = "(unknown title)"
			else:
				remarks = ""
			try:
				start = event.start
				end = event.end
				minutes = int((end-start)/timedelta(minutes=1)+0.5)
				toolsum += minutes
			except:
				start = None
				end = None
				minutes = None
			start = timezone.localtime(start)
			end = timezone.localtime(end)
			event_entry = {'start': start, 'end': end, 'minutes': minutes, 'projectname': projectname, 'affiliation': affiliation, 'user': fullname, 'remarks': remarks}
			toolevents.append(event_entry)
# append total (note: start and end will be undefined here!)
		toolevents.append( { 'minutes': toolsum } )
	return toolevents

@permission_required('NEMO.change_tool', raise_exception=True)
@require_GET
def toolevents(request):
	""" Presents a page displaying tool events for a given time span. """
	dictionary = {}
	dictionary['tools'] = allowed_tools(request)
	try:
		tool = int(request.GET['tool'])
		toolname = Tool.objects.get(pk=tool).name
	except:
		tool = 0
		toolname = '(undefined tool)'
	try:
		start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])
	except:
# by default, start is beginnning of the year, end is today
		start = date.today().replace(month=1,day=1)
		end = date.today()
	try:
		eventtype = request.GET['eventtype']
	except:
		eventtype = 'usage'
	events = []
	try:
		if Tool.objects.get(pk=tool) in allowed_tools(request):
			events = get_tool_span_events(request, eventtype, tool, start, end)
	except:
		pass
	try:
		outputtype = request.GET['outputtype']
	except:
		outputtype = 'table'
	if outputtype != 'xlsx':
		dictionary['tool'] = tool
		dictionary['toolname'] = toolname
		dictionary['start'] = start
		dictionary['end'] = end
		dictionary['events'] = events
		dictionary['eventtype'] = eventtype
		if outputtype == 'txt':
			return render(request, 'toolevents.txt', dictionary, content_type="text/plain")
		else:
# HTML table output
			return render(request, 'toolevents.html', dictionary)
	else:
# XLSX output
# get last entry containing sum
		toolsum = events[-1]['minutes']
# .. and remove it from table
		events = events[0:-1]
		fn = eventtype + '_' + str(tool) + '_' + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
		book = Workbook(response, {'in_memory': True})
		sheet = book.add_worksheet(eventtype+' '+str(tool))
		bold = book.add_format()
		bold.set_bold()
		italic = book.add_format()
		italic.set_italic()
		title = [ eventtype, toolname ]
		sheet.write_row('A1', title, bold)
		title = [ start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), toolsum ]
		sheet.write_row('A2', title)
		columntitles = ['Start', 'End', 'Minutes', 'Project', 'User', 'Affiliation', 'Title/Remarks']
		sheet.write_row('A4', columntitles, italic)
		rownum = 4
		for e in events:
			row = [ e['start'].strftime("%y-%m-%d,%H:%M"), e['end'].strftime("%y-%m-%d,%H:%M"), e['minutes'], e['projectname'], e['user'], e['affiliation'], e['remarks'] ]
			sheet.write_row(rownum,0,row)
			rownum += 1
		book.close()
		return response
