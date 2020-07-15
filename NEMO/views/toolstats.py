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
from NEMO.models import User, Tool, Project, Account, UsageEvent

def allowed_tools(request):
	""" tools for which the requester is allowed to view usage events"""
# somebody who is allowed to change events can view them for all tools
	if request.user.has_perm('NEMO.change_usageevent'):
		return Tool.objects.all()
# others can just view tools where they are primary responsibles
	else:
		return Tool.objects.filter(primary_owner=request.user)

def get_tool_span_events(request, tool, begin, end):
	""" get all usage events ending after begin and before or at end """
	toolusage = []
	if Tool.objects.get(pk=tool) in allowed_tools(request):
		events = UsageEvent.objects.filter(tool=tool, end__gt=begin, end__lte=end).order_by('start')
		for event in events:
			fullname = event.user.last_name + " " + event.user.first_name
			projectname = event.project.name
			groupname = event.project.account.name
			start = event.start
			end = event.end
			minutes = int((end-start)/timedelta(minutes=1)+0.5)
			event_entry = {'start': start, 'end': end, 'minutes': minutes, 'projectname': projectname, 'groupname': groupname, 'user': fullname}
			toolusage.append(event_entry)
	return toolusage

@staff_member_required(login_url=None)
@require_GET
def toolstats(request):
	""" Presents a page displaying tool usage for a given time span. """
	dictionary = {}
	dictionary['tools'] = allowed_tools(request)
	tool = 0
	try:
		tool = int(request.GET['tool'])
		if Tool.objects.get(pk=tool) in allowed_tools(request):
			start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])
			dictionary['start'] = start
			dictionary['end'] = end
			dictionary['toolusage'] = get_tool_span_events(request, tool, start, end)
			dictionary['toolname'] = Tool.objects.get(pk=tool).name
		else:
			dictionary['toolname'] = Tool.objects.get(pk=tool).name
			tool = 0
	except:
		dictionary['toolname'] = '(undefined tool)'
	dictionary['tool'] = tool
	return render(request, 'toolstats.html', dictionary)


#@staff_member_required(login_url=None)
#@require_GET
#def toolusagexlsx(request):
#	dictionary = {}
#	try:
#		start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])
#		tool = int(request.GET['tool'])
#		fn = "toolusage_" + str(tool) + "_" + start.strftime("%Y%m%d") + "-" + end.strftime("%Y%m%d") + ".xlsx"
#		toolusage = get_tool_span_usage(tool, start, end)
#		response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
#		book = Workbook(response, {'in_memory': True})
#		sheet = book.add_worksheet('tool usage')
#		bold = book.add_format()
#		bold.set_bold()
#		title = [ Tool.name(pk=tool), 'from', start.strftime("%Y-%m-%d"), 'to', end.strftime("%Y-%m-%d") ]
#		sheet.write_row('A1', title, bold)
#		columntitles = ['Start', 'End', 'Duration/min', 'Project', 'Account,Group', 'User']
#		sheet.write_row('A2', columntitles, bold)
#		iter = 1
#		for e in toolusage:
#			if not r['billable_days'] == 0 or not r['total_bill'] == 0:
#				days_cell = xl_rowcol_to_cell(iter,5)
#				adj_cell = xl_rowcol_to_cell(iter,7)
#				if r['user_type'] == 'Internal - Unlimited':
#					usage_eq = 1125
#				elif r['user_type'] == 'Internal - Full'or r['user_type'] == 'Internal - Packaging' or r['user_type'] == 'Internal - SMP':
#					usage_eq = f'=min({xl_rowcol_to_cell(iter,5)}+{xl_rowcol_to_cell(iter,6)},10)*{xl_rowcol_to_cell(iter,7)}+max(-10+{xl_rowcol_to_cell(iter,5)}+{xl_rowcol_to_cell(iter,6)},0)*45'
#				else:
#					usage_eq = f'=({xl_rowcol_to_cell(iter,5)}+{xl_rowcol_to_cell(iter,6)})*{xl_rowcol_to_cell(iter,7)}'
#				total_eq = f'=sum({xl_range(iter, 8, iter, 11)})'
#				row = [r['username'], r['name'], r['email'], r['PI'], r['user_type'], r['billable_days'], "", r['rate'], usage_eq, r['stockroom_bill'], r['staff_charge_bill'], "", total_eq]
#				sheet.write_row(iter,0,row)
#				iter +=1
#		sheet.set_column('H:M', None, money)
#		sheet.set_column('G:G', None, redgreen)
#		sheet.set_column('L:L', None, rgmoney)
#		book.close()
#		return response
#	except:
#		return render(request, 'billing.html', dictionary)
