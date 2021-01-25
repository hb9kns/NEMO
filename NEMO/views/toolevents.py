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

def get_project_span_tool_event_sums(projects, begin, end, billables=False):
	""" get sums (in minutes) of all project related events for each tool,
            ending after begin and before or at end
            and return a list of ['tool':.., 'usage':.., 'monthly':.., 'reservation':..]
	    (if billables==True, return tool entries with existing billing
	     reference together, and sum all usage and reservation for
	     tools with same reference)
	"""
# list of tool primary keys and corresponding billing references
	tools = {tool.pk:tool.billing_reference for tool in Tool.objects.all().order_by('name')}
	toolsums = {}
	refsums = {}
	delta_months = abs((end-begin)/timedelta(days=30))
	for t in tools.keys():
# populate toolsums
		toolsums[t] = [0,0]
	billrefs=set([b for b in tools.values() if b])
	billrefs=list(billrefs)
	billrefs.sort()
	for b in billrefs:
# populate refsums for billing references
		refsums[b] = [0,0]
	for event in UsageEvent.objects.filter(project__in=projects, end__gt=begin, end__lte=end).order_by('start'):
		try:
			start = event.start
			end = event.end
			minutes = int((end-start)/timedelta(minutes=1)+0.5)
			toolsums[event.tool.pk][0] += minutes
			refsums[tools[event.tool.pk]][0] += minutes
		except:
			pass
	for event in Reservation.objects.filter(project__in=projects, end__gt=begin, end__lte=end, cancelled=False, shortened=False).order_by('start'):
		try:
			start = event.start
			end = event.end
			minutes = int((end-start)/timedelta(minutes=1)+0.5)
			toolsums[event.tool.pk][1] += minutes
			refsums[tools[event.tool.pk]][1] += minutes
		except:
			pass
	result = []
	if billables:
		for b in billrefs:
			tn=''
			for t in Tool.objects.filter(billing_reference=b):
				tn+=t.name+' // '
		# monthly: average usage in hours (to one decimal) per month
			result.append({'ref':b, 'desc':tn.rstrip(' // '), 'usage':refsums[b][0], 'monthly':int(refsums[b][0]/delta_months/6+0.5)/10, 'reservation':refsums[b][1]})
	else:
# use mock reference number (just running index)
		ref=990001
		for t in tools.keys():
			if toolsums[t][0] != 0 or toolsums[t][1] != 0:
		# monthly: average usage in hours (to one decimal) per month
				result.append({'ref':ref, 'desc':Tool.objects.get(pk=t).name, 'usage':toolsums[t][0], 'monthly':int(toolsums[t][0]/delta_months/6+0.5)/10, 'reservation':toolsums[t][1]})
				ref+=1
	return result

@staff_member_required(login_url=None)
@require_GET
def project_sums(request, billable_tools=True):
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
	dictionary['allprojects'] = Project.objects.all()
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
	days = int(0.5+(end-start)/timedelta(days=1))
	dictionary['days'] = days
# get all event sums related to all the projects as a
# list of {'tool':.,'usage':.,'reservation':.}
	try:
		totals = get_project_span_tool_event_sums(projects, start, end, billables=billable_tools)
	except:
		totals = []
# tabular/textual output
	if outputtype != 'xlsx':
		dictionary['start'] = start
		dictionary['end'] = end
		dictionary['totals'] = totals
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
		fn = 'nemo-' + indicator + '-' + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
		book = Workbook(response, {'in_memory': True})
		sheet = book.add_worksheet(indicator)
		bold = book.add_format()
		bold.set_bold()
		italic = book.add_format()
		italic.set_italic()
		title = [ 'NEMO usage and reservation sums for all of:' ]
		for p in projects:
			title.append( p.name )
		sheet.write_row('A1', title, bold)
		title = [ 'beginning:', start.strftime("%Y-%m-%d"), 'ending:', end.strftime("%Y-%m-%d"), 'corresponding to', days, 'days' ]
		sheet.write_row('A2', title)
		columntitles = ['Reference', 'Description', 'Usage/min', 'Average Monthly Usage/hours', 'Reservation/min']
		sheet.write_row('A4', columntitles, italic)
		rownum = 4
		for e in totals:
			row = [ e['ref'], e['desc'], e['usage'], e['monthly'], e['reservation'] ]
			sheet.write_row(rownum,0,row)
			rownum += 1
		book.close()
		return response

@staff_member_required(login_url=None)
@require_GET
def billing_sums(request):
	""" Calculates table of billable tool usage
	    for all projects and for a given time span. """
# get active project ids
#	projects = Project.objects.filter(active=True)
	projects = Project.objects.all()
	dictionary = {}
	dictionary['projects'] = projects
# by default, start is beginnning of the month, end is today
	def_start = '{0}-{1}-01'.format(date.today().year,date.today().month)
	def_end = date.today().isoformat()
# generate ISO formats for defaults, to be able to use existing parser function
	try:
		trystart = request.GET['start']
	except:
		trystart = def_start
	try:
		tryend = request.GET['end']
	except:
		tryend = def_end
	try:
		(start, end) = parse_start_and_end_date(trystart, tryend)
	except:
		(start, end) = parse_start_and_end_date(def_start, def_end)
	days = int(0.5+(end-start)/timedelta(days=1))
	dictionary['days'] = days
# get all event sums related to all the projects as a
# list of {'tool':.,'usage':.,'reservation':.}
	totals={}
	for p in projects:
		try:
			totals[p.name] = get_project_span_tool_event_sums([p], start, end, billables=True)
			# note as valid project
			good_name = p.name
		except:
			totals[p.name] = []
	if good_name:
		# get sorted billing references from last valid project
		billrefs = [ [t['ref'],t['desc']] for t in totals[good_name] ]
		billrefs.sort()
	fn = 'nemo-billing-' + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
	book = Workbook(response, {'in_memory': True})
	sheet = book.add_worksheet('billing')
	bold = book.add_format()
	bold.set_bold()
	italic = book.add_format()
	italic.set_italic()
	title = [ 'NEMO usage hours for billable tools of all projects' ]
	sheet.write_row('A1', title, bold)
	title = [ 'beginning:', start.strftime("%Y-%m-%d"), 'ending:', end.strftime("%Y-%m-%d"), 'corresponding to', days, 'days' ]
	sheet.write_row('A2', title)
	columntitles = ['Reference', 'Description']+[ p.name for p in projects ]
	sheet.write_row('A4', columntitles, italic)
	columntitles = ['', '']+[ p.billing_reference for p in projects ]
	sheet.write_row('A5', columntitles, italic)
	rownum = 5
	for b in billrefs:
		# prepend billing ref and description
		row = [ b[0], b[1] ]
		for p in projects:
		# two-decimals float of billrefs usage total converted to hours
			row += [ float('{0:.2f}'.format( float(tot['usage'])/60 )) for tot in totals[p.name] if tot['ref'] == b[0] ]
		sheet.write_row(rownum,0,row)
		rownum += 1
	book.close()
	return response
