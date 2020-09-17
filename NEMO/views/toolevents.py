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
	    (type selects between 'reservation' or 'usage') """
	toolevents = []
	if Tool.objects.get(pk=tool) in allowed_tools(request):
		if eventtype == 'reservation':
			events = Reservation.objects.filter(tool=tool, end__gt=begin, end__lte=end, cancelled=False, shortened=False).order_by('start')
		else:
			events = UsageEvent.objects.filter(tool=tool, end__gt=begin, end__lte=end).order_by('start')
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
			except:
				start = None
				end = None
				minutes = None
			start = timezone.localtime(start)
			end = timezone.localtime(end)
			event_entry = {'start': start, 'end': end, 'minutes': minutes, 'projectname': projectname, 'affiliation': affiliation, 'user': fullname, 'remarks': remarks}
			toolevents.append(event_entry)
	return toolevents

@staff_member_required(login_url=None)
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
		title = [ start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d") ]
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

### reporting of total project usage

def get_project_span_tool_event_sums(eventtype, projects, begin, end):
	""" get sums of all project related usage events for each tool,
            ending after begin and before or at end
	    (eventtype selects between 'reservation' or 'usage')
            and return a list of ['tool':.., 'minutes':..] """
	if eventtype == 'reservation':
		events = Reservation.objects.filter(project__in=projects, end__gt=begin, end__lte=end, cancelled=False, shortened=False).order_by('start')
	else:
		events = UsageEvent.objects.filter(project__in=projects, end__gt=begin, end__lte=end).order_by('start')
	tools = [tool.pk for tool in Tool.objects.all().order_by('name')]
	toolsums = {}
	for t in tools:
		toolsums[t] = 0
	for event in events:
		if True:
			start = event.start
			end = event.end
			minutes = int((end-start)/timedelta(minutes=1)+0.5)
			toolsums[event.tool.pk] += minutes
		else:
			pass
	result = []
	for t in tools:
		if toolsums[t] != 0:
			result.append({'tool':Tool.objects.get(pk=t).name,'minutes':toolsums[t]})
	return result

@staff_member_required(login_url=None)
@require_GET
def project_sums(request):
	""" Presents a page displaying the sum of tool events
            belonging to given projects and for a given time span. """
# get project ids (only characters '0-9,' from request)
	try:
		project_ids = re.sub('[^0-9,]', '', request.GET['pjts']).rstrip(',')
		projects = Project.objects.filter(pk__in=set(project_ids.split(",")))
	except:
		projects = Project.objects.filter(active=True)
	dictionary = {}
	dictionary['projects'] = projects
# get eventtype and outputtype
	try:
		eventtype = request.GET['eventtype']
	except:
		eventtype = 'usage'
	try:
		outputtype = request.GET['outputtype']
	except:
		outputtype = 'table'
# by default, start is beginnning of the year, end is today
# generate ISO formats for defaults, to be able to use existing parser function
	try:
		trystart = request.GET['start']
	except:
		trystart = '{0}-01-01'.format(date.today().year)
	try:
		tryend = request.GET['end']
	except:
		tryend = date.today().isoformat()
	(start, end) = parse_start_and_end_date(trystart, tryend)
# get all event sums related to all the projects
	if True:
		totals = get_project_span_tool_event_sums(eventtype, projects, start, end)
	else:
		totals = []
# tabular/textual output
	if outputtype != 'xlsx':
		dictionary['start'] = start
		dictionary['end'] = end
		dictionary['totals'] = totals
		dictionary['eventtype'] = eventtype
		if outputtype == 'txt':
# preformatted text output
			return render(request, 'eventsums.txt', dictionary, content_type="text/plain")
		else:
# HTML table output
			return render(request, 'eventsums.html', dictionary)
	else:
# XLSX output
		indicator = projects.first().name
		if len(projects)>1:
			indicator += '_etc'
		fn = eventtype + '_' + indicator + '_' + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
		book = Workbook(response, {'in_memory': True})
		sheet = book.add_worksheet(eventtype+' '+indicator)
		bold = book.add_format()
		bold.set_bold()
		italic = book.add_format()
		italic.set_italic()
		title = [ eventtype+' sums for all of:' ]
		for p in projects:
			title.append( p.name )
		sheet.write_row('A1', title, bold)
		title = [ 'beginning:', start.strftime("%Y-%m-%d"), 'ending:', end.strftime("%Y-%m-%d") ]
		sheet.write_row('A2', title)
		columntitles = ['Tool', 'Minutes']
		sheet.write_row('A4', columntitles, italic)
		rownum = 4
		for e in totals:
			row = [ e['tool'], e['minutes'] ]
			sheet.write_row(rownum,0,row)
			rownum += 1
		book.close()
		return response

#:# def allowed_tools(request):
#:# 	""" tools for which the requester is allowed to view usage events"""
#:# # reusing permissions: those allowed to change events can view all tools
#:# 	if request.user.has_perm('NEMO.change_usageevent'):
#:# 		return Tool.objects.all()
#:# # others can just view tools where they are primary responsibles
#:# 	else:
#:# 		return Tool.objects.filter(primary_owner=request.user)
