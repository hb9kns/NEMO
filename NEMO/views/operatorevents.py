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

def allowed_operators(request):
	""" operators for which the requester is allowed to view events"""
# reusing permissions: those allowed to change events can view all operators
	if request.user.has_perm('NEMO.change_account'):
		return User.objects.all()
# others can just view themselves
	else:
		return User.objects.filter(pk=request.user.id)

def get_operator_span_events(request, eventtype, operatorid, begin, end):
	""" get all usage events ending after begin and before or at end
	    (type selects between 'reservation' or 'usage') """
	operatorevents = []
	if User.objects.get(pk=operatorid) in allowed_operators(request):
		if eventtype == 'reservation':
			events = Reservation.objects.filter(user=operatorid, end__gt=begin, end__lte=end, cancelled=False, shortened=False).order_by('start')
		else:
# for usage events, get those where the user is operator
			events = UsageEvent.objects.filter(operator=operatorid, end__gt=begin, end__lte=end).order_by('start')
		for event in events:
			try:
				username = event.user.last_name + " " + event.user.first_name
			except:
				username = "(unknown user)"
			try:
				operatorname = event.operator.last_name + " " + event.operator.first_name
			except:
				operatorname = username
			try:
				toolname = event.tool.name
			except:
				toolname = "(unknown tool)"
			try:
				projectname = event.project.name
			except:
				projectname = "(unknown project)"
			try:
				affiliation = event.user.affiliation.name
			except:
				affiliation = "(unknown affiliation)"
			try:
				remarks = event.title
			except:
				remarks = "(undefined)"
			try:
				start = event.start
				end = event.end
				hours = int((end-start)/timedelta(minutes=1)+0.5)/60
			except:
				start = None
				end = None
				hours = None
			start = timezone.localtime(start)
			end = timezone.localtime(end)
			event_entry = {'start': start, 'end': end, 'hours': hours, 'toolname': toolname, 'projectname': projectname, 'affiliation': affiliation, 'user': username, 'operator': operatorname, 'remarks': remarks}
			operatorevents.append(event_entry)
	return operatorevents

@require_GET
def operatorevents(request):
	""" Presents a page displaying operator events for a given time span. """
	dictionary = {}
	dictionary['operators'] = allowed_operators(request)
	try:
		operatorid = int(request.GET['operatorid'])
# try getting user, for catching nonexistent operatorid values
		operatorname = User.objects.get(pk=operatorid).first_name+" "+User.objects.get(pk=operatorid).last_name
	except:
		operatorid = request.user.id
	operatorname = User.objects.get(pk=operatorid).first_name+" "+User.objects.get(pk=operatorid).last_name
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
		if User.objects.get(pk=operatorid) in allowed_operators(request):
			events = get_operator_span_events(request, eventtype, operatorid, start, end)
	except:
		pass
	try:
		outputtype = request.GET['outputtype']
	except:
		outputtype = 'table'
	if outputtype != 'xlsx':
		dictionary['operatorid'] = operatorid
		dictionary['operatorname'] = operatorname
		dictionary['start'] = start
		dictionary['end'] = end
		dictionary['events'] = events
		dictionary['eventtype'] = eventtype
		if outputtype == 'txt':
			return render(request, 'operatorevents.txt', dictionary, content_type="text/plain")
		else:
# HTML table output
			return render(request, 'operatorevents.html', dictionary)
	else:
# XLSX output
		fn = 'op_' + eventtype + '_' + str(operatorid) + '_' + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
		book = Workbook(response, {'in_memory': True})
		sheet = book.add_worksheet(eventtype+' '+str(operatorid))
		bold = book.add_format()
		bold.set_bold()
		italic = book.add_format()
		italic.set_italic()
		title = [ eventtype + ' events for operator:', operatorname ]
		sheet.write_row('A1', title, bold)
		title = [ start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d") ]
		sheet.write_row('A2', title)
		columntitles = ['Start', 'End', 'Hours', 'Tool', 'Project', 'User', 'Affiliation', 'Title/Remarks']
		sheet.write_row('A4', columntitles, italic)
		rownum = 4
		for e in events:
			row = [ e['start'].strftime("%y-%m-%d,%H:%M"), e['end'].strftime("%y-%m-%d,%H:%M"), e['hours'], e['toolname'], e['projectname'], e['user'], e['affiliation'], e['remarks'] ]
			sheet.write_row(rownum,0,row)
			rownum += 1
		book.close()
		return response
