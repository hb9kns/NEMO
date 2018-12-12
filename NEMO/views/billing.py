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
from NEMO.models import User, AreaAccessRecord, Account, Project, StockroomWithdraw, StaffCharge

#@staff_member_required(login_url=None)
#@require_GET
def get_billing_data(start, end):
	billing_result = []
	daily_rate = {1:0,2:135,3:0,4:220,5:0,6:45,7:0,8:0}
	staff_charge_rate = {'Internal Academic':80,'External Academic':130,'Industrial':480,'Undergraduate':80}

	users = User.objects.all().exclude(type=1).exclude(type=3).exclude(type=7).exclude(type=8)
	for user in users:
		billable_days = 0
		try:
			user_access = AreaAccessRecord.objects.filter(customer=user, end__gte=start, end__lt=end, staff_charge=None).order_by('start')
			for index, access_event in enumerate(user_access):
				start_date = timezone.localtime(access_event.start).date()
				end_date = timezone.localtime(access_event.end).date()
				dt = end_date - start_date
				days = dt.days
				if index == 0:
					billable_days += days + 1
				else:
					last_access = user_access[index-1]
					if timezone.localtime(last_access.end).date() == start_date:
						billable_days += days
					else:
						billable_days += days + 1
		except:
			pass
		stockroom_bill = 0
		try:
			stockroom_withdraws = StockroomWithdraw.objects.filter(customer=user, date__range=(start, end))
			for purchase in stockroom_withdraws:
				stockroom_bill += purchase.stock.cost*purchase.quantity
		except:
			pass
		staff_charge_bill = 0
		try:
			staff_charge = StaffCharge.objects.filter(customer=user, end__gte=start, end__lt=end, validated=True)
			for charge in staff_charge:
				chargetime = charge.end-charge.start
				staff_charge_bill += chargetime.total_seconds()/3600*staff_charge_rate[user.type.name]
		except:
			pass
		user_billing = {'username': user.username, 'last_name': user.last_name, 'first_name': user.first_name, 'email': user.email, 'type': user.type.name, 'billable_days': billable_days, 'stockroom_bill': stockroom_bill, 'staff_charge_bill': round(staff_charge_bill,2)}
		billing_result.append(user_billing)

	return billing_result

@staff_member_required(login_url=None)
@require_GET
def billing(request):
	""" Presents a page that displays billing. """
	dictionary = {}
	try:
		start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])
		dictionary['start'] = start
		dictionary['end'] = end
		dictionary['billing_result'] = get_billing_data(start, end)
	except:
		pass
	return render(request, 'billing.html', dictionary)


@staff_member_required(login_url=None)
@require_GET
def billingcsv(request):
	try:
		start, end = parse_start_and_end_date(request.GET['start'], request.GET['end'])
		fn = "billing_" + start.strftime("%Y%m%d") + "_" + end.strftime("%Y%m%d") + ".csv"
		billing_result = get_billing_data(start, end)
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
		fields = ['username', 'last_name', 'first_name', 'email', 'type', 'billable_days', 'stockroom_bill', 'staff_charge_bill']
		writer = csv.DictWriter(response, fields)
		writer.writeheader()
		for r in billing_result:
			writer.writerow(r)
	except:
		pass
	return response
