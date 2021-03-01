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
# make set of list of billing refs and back to list, to make them unique
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
	sheet.write_row('A2', ['','','','begin','end','note','prefix','price','attach'], italic)
	title = [ '','','SAPdata', start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), '','','1','','','  =', days, ' days' ]
	sheet.write_row('A3', title)
	columntitles = ['Reference', 'Description', 'Project']+[ p.name for p in projects ]
	sheet.write_row('A4', columntitles, italic)
	columntitles = ['', '', '']+[ p.billing_reference for p in projects ]
	sheet.write_row('A5', columntitles, italic)
	rownum = 5
	for b in billrefs:
		# prepend billing ref, description and empty cell
		row = [ b[0], b[1], '' ]
		for p in projects:
		# two-decimals float of billrefs usage total converted to hours
			row += [ float('{0:.2f}'.format( float(tot['usage'])/60 )) for tot in totals[p.name] if tot['ref'] == b[0] ]
		sheet.write_row(rownum,0,row)
		rownum += 1
# add end marker for further processing
	sheet.write_row(rownum,0, ['','^-^','End'])
	book.close()
	return response

### reporting of project usage events

def get_project_span_usage_events(projects, begin, end, billables=True):
	""" get usage events of all selected projects for all billable tools,
            ending after begin and before or at end,
	    returning a list of start/end/tools/project/user/affiliation
	    (if billables==True, return tool entries with existing billing
	     reference together)
	"""
# list of tool primary keys and corresponding billing references
	tools = {tool.pk:tool.billing_reference for tool in Tool.objects.all().order_by('name')}
# make set of list of billing refs and back to list, to make them unique
	billrefs=set([b for b in tools.values() if b])
	billrefs=list(billrefs)
	# billrefs.sort()
	result = []
	for event in UsageEvent.objects.filter(project__in=projects, end__gt=begin, end__lte=end).order_by('start'):
		try:
			eufull = event.user.last_name + " " + event.user.first_name
		except:
			eufull = "(unknown user)"
		try:
			epjt = event.project.name
		except:
			epjt = "(unknown project)"
		try:
			uaffil = event.user.affiliation.name
		except:
			uaffil = "(unknown affiliation)"
		try:
			estart = event.start
			eend = event.end
			eminutes = int( (eend-estart)/timedelta(minutes=1)+0.5 )
		except:
			estart = None
			eend = None
			eminutes = None
		estart = timezone.localtime(estart)
		eend = timezone.localtime(eend)
		etool = event.tool.name
		if tools[event.tool.pk]:
			etref = tools[event.tool.pk]
		else:
			etref = None
		result.append( {'start':estart, 'end':eend, 'minutes':eminutes, 'user':eufull, 'projectdesc':epjt, 'tooldesc':etool, 'toolref':etref, 'affiliation':uaffil} )
	return result

@staff_member_required(login_url=None)
@require_GET
def projectevents(request, billable_tools=True):
	""" Presents a page displaying all tool usage events
            belonging to given projects and for a given time span. """
# get project ids (only characters '0-9,' from request)
	try:
		project_ids = re.sub('[^0-9,]', '', request.GET['pjts']).rstrip(',')
		projects = Project.objects.filter(pk__in=set(project_ids.split(",")))
	except:
		projects = None
	dictionary = {}
	dictionary['pjts'] = projects
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
# get all tool events related to all the projects as a
# list of {'start':.,'end':...}
	try:
		pjtevents = get_project_span_usage_events(projects, start, end, billables=billable_tools)
	except:
		pjtevents = []
	dictionary['events'] = pjtevents
# tabular/textual output
	if outputtype != 'xlsx':
		dictionary['start'] = start
		dictionary['end'] = end
		if outputtype == 'txt':
# preformatted text output
			return render(request, 'projectevents.txt', dictionary, content_type="text/plain")
		else:
# HTML table output
			return render(request, 'projectevents.html', dictionary)
	else:
# XLSX output
		indicator = projects.first().name
		if len(projects)>1:
			indicator += '_etc'
		fn = 'nemoevents-' + indicator + '-' + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
		book = Workbook(response, {'in_memory': True})
		sheet = book.add_worksheet(indicator)
		bold = book.add_format()
		bold.set_bold()
		italic = book.add_format()
		italic.set_italic()
		title = [ 'NEMO usage events for all of:' ]
		for p in projects:
			title.append( p.name )
		sheet.write_row('A1', title, bold)
		title = [ 'beginning:', start.strftime("%Y-%m-%d"), 'ending:', end.strftime("%Y-%m-%d"), 'corresponding to', days, 'days' ]
		sheet.write_row('A2', title)
		columntitles = ['Start', 'End', 'Minutes', 'Tool', 'Ref', 'Project', 'User', 'Affiliation']
		sheet.write_row('A4', columntitles, italic)
		rownum = 4
		for e in pjtevents:
			row = [ e['start'].strftime("%y-%m-%d,%H:%M"), e['end'].strftime("%y-%m-%d,%H:%M"), e['minutes'], e['tooldesc'], e['toolref'], e['projectdesc'], e['user'], e['affiliation'] ]
			sheet.write_row(rownum,0,row)
			rownum += 1
		book.close()
		return response
