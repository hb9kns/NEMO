import csv

from datetime import timedelta, date
from time import sleep
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from NEMO.utilities import parse_start_and_end_date, month_list, get_month_timeframe
from NEMO.models import User, AreaAccessRecord, Account, Project

@staff_member_required(login_url=None)
@require_GET
def get_billing_data(request):
	billing_result = []
	#start, end = get_month_timeframe('09/01/2018')
	try:
		start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])

		users = User.objects.all()
		#response = HttpResponse(content_type='text/csv')
		#response['Content-Disposition'] = 'attachment; filename = "billing.csv"'
		#writer = csv.writer(response)
		#writer.writerow(['User Name', 'Last Name', 'First Name', 'email', 'User Type', 'Billable Days'])
		for user in users:
			billable_days = 0
			user_access = AreaAccessRecord.objects.filter(customer = user, start__gte=start, start__lte=end, staff_charge=None).order_by('start')
			for index, access_event in enumerate(user_access):
				start_date = access_event.start.toordinal()
				end_date = access_event.end.toordinal()
				if index == 0:
					billable_days += end_date - start_date + 1
				else:
					last_access = user_access[index-1]
					if last_access.end.toordinal() == start_date:
						billable_days += end_date - start_date
					else:
						billable_days += end_date - start_date + 1
			user_billing = {'username': user.username, 'last_name': user.last_name, 'first_name': user.first_name, 'email': user.email, 'type': user.type, 'billable_days': billable_days}
			billing_result.append(user_billing)
	except:
		pass
	return billing_result

@staff_member_required(login_url=None)
@require_GET
def billing(request):
	""" Presents a page that displays billing. """
	#billing_result = []
	dictionary = {}
	#start, end = get_month_timeframe('09/01/2018')
	#try:
	#	start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])

	#	users = User.objects.all()
		#response = HttpResponse(content_type='text/csv')
		#response['Content-Disposition'] = 'attachment; filename = "billing.csv"'
		#writer = csv.writer(response)
		#writer.writerow(['User Name', 'Last Name', 'First Name', 'email', 'User Type', 'Billable Days'])
	# 	for user in users:
	# 		billable_days = 0
	# 		user_access = AreaAccessRecord.objects.filter(customer = user, start__gte=start, start__lte=end, staff_charge=None).order_by('start')
	# 		for index, access_event in enumerate(user_access):
	# 			start_date = access_event.start.toordinal()
	# 			end_date = access_event.end.toordinal()
	# 			if index == 0:
	# 				billable_days += end_date - start_date + 1
	# 			else:
	# 				last_access = user_access[index-1]
	# 				if last_access.end.toordinal() == start_date:
	# 					billable_days += end_date - start_date
	# 				else:
	# 					billable_days += end_date - start_date + 1
	# 		user_billing = {'username': user.username, 'last_name': user.last_name, 'first_name': user.first_name, 'email': user.email, 'type': user.type, 'billable_days': billable_days}
	# 		billing_result.append(user_billing)
	# except:
	# 	pass

		#writer.writerow(user_billing)
		#return response


	dictionary['billing_result'] = get_billing_data(request)
	return render(request, 'billing.html', dictionary)


@staff_member_required(login_url=None)
@require_GET
def billingcsv(request):
	billing_result = get_billing_data(request)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename = "billing.csv"'
	fields = ['username', 'last_name', 'first_name', 'email', 'type', 'billable_days']
	writer = csv.DictWriter(response, fields)
	writer.writeheader()
	for r in billing_result:
		writer.writerow(r)
	return response
