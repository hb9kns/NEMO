from datetime import timedelta, datetime
from django.template import Template, Context
from django.utils import timezone
import kronos
from NEMO.models import Tool, Reservation, UsageEvent, AreaAccessRecord, StaffCharge
from NEMO.views.customization import get_customization, get_media_file_contents
from NEMO.views.calendar import send_missed_reservation_notification
from NEMO.utilities import format_datetime
from django.core.mail import send_mail


@ kronos.register('')
def usage_reminder():
	projects_to_exclude = []
	busy_users = AreaAccessRecord.objects.filter(end=None, staff_charge=None).exclude(project__id__in=projects_to_exclude)
	busy_tools = UsageEvent.objects.filter(end=None).exclude(project__id__in=projects_to_exclude)
	aggregate = {}
	for access_record in busy_users:
		key = str(access_record.customer)
		aggregate[key] = {
			'email': access_record.customer.email,
			'first_name': access_record.customer.first_name,
			'resources_in_use': [str(access_record.area)],
		}
	for usage_event in busy_tools:
		key = str(usage_event.operator)
		if key in aggregate:
			aggregate[key]['resources_in_use'].append(usage_event.tool.name)
		else:
			aggregate[key] = {
				'email': usage_event.operator.email,
				'first_name': usage_event.operator.first_name,
				'resources_in_use': [usage_event.tool.name],
			}
	user_office_email = get_customization('user_office_email_address')
	message = get_media_file_contents('usage_reminder_email.html')
	if message:
		subject = "NanoFab usage"
		for user in aggregate.values():
			rendered_message = Template(message).render(Context({'user': user}))
			send_mail(subject, '', user_office_email, [user['email']], html_message=rendered_message)

	message = get_media_file_contents('staff_charge_reminder_email.html')
	if message:
		busy_staff = StaffCharge.objects.filter(end=None)
		for staff_charge in busy_staff:
			subject = "Active staff charge since " + format_datetime(staff_charge.start)
			rendered_message = Template(message).render(Context({'staff_charge': staff_charge}))
			staff_charge.staff_member.email_user(subject, rendered_message, user_office_email)


@ kronos.register('')
def res_reminder():
	# Exit early if the reservation reminder email template has not been customized for the organization yet.
	good_message = get_media_file_contents('reservation_reminder_email.html')
	problem_message = get_media_file_contents('reservation_warning_email.html')
	if not good_message or not problem_message:
		return
	#HttpResponseNotFound('The reservation reminder email template has not been customized for your organization yet. Please visit the NEMO customizable_key_values page to upload a template, then reservation reminder email notifications can be sent.')

	# Find all reservations in the next day
	#preparation_time = 120  These were sending an email for each reservation 2 hrs in advance. I'm not using them
	#tolerance = 5
	earliest_start = timezone.now()
	latest_start = timezone.now() + timedelta(hours=24)
	upcoming_reservations = Reservation.objects.filter(cancelled=False, start__gt=earliest_start, start__lt=latest_start)
	# Email a reminder to each user with an upcoming reservation.
	goodAggregate = {}
	problemAggregate = {}
	for reservation in upcoming_reservations:
		key = str(reservation.user)
		if reservation.tool.operational and not reservation.tool.problematic() and reservation.tool.all_resources_available():
			if key in goodAggregate:
				goodAggregate[key]['Tools'].append(reservation.tool.name)
			else:
				goodAggregate[key] = {
					'email': reservation.user.email,
					'first_name': reservation.user.first_name,
					'Tools': [reservation.tool.name],
				}
		else:
			if key in problemAggregate:
				problemAggregate[key]['Tools'].append(reservation.tool.name)
			else:
				problemAggregate[key] = {
					'email': reservation.user.email,
					'first_name': reservation.user.first_name,
					'Tools': [reservation.tool.name],
				}
	user_office_email = get_customization('user_office_email_address')
	if good_message:
		subject = "Upcoming Reservations"
		for user in goodAggregate.values():
			rendered_message = Template(good_message).render(Context({'user': user}))
			send_mail(subject, '', user_office_email, [user['email']], html_message=rendered_message)

	if problem_message:
		subject = "Problem With Your Upcoming Reservation"
		for user in problemAggregate.values():
			rendered_message = Template(problem_message).render(Context({'user': user}))
			send_mail(subject, '', user_office_email, [user['email']], html_message=rendered_message)

@ kronos.register('')
def cancel_missed_res():
	# Exit early if the missed reservation email template has not been customized for the organization yet.
	if not get_media_file_contents('missed_reservation_email.html'):
		return
			#HttpResponseNotFound('The missed reservation email template has not been customized for your organization yet. Please visit the NEMO customizable_key_values page to upload a template, then missed email notifications can be sent.')

	tools = Tool.objects.filter(visible=True, operational=True, missed_reservation_threshold__isnull=False)
	missed_reservations = []
	for tool in tools:
		# If a tool is in use then there's no need to look for unused reservation time.
		if tool.in_use() or tool.required_resource_is_unavailable():
			continue
		# Calculate the timestamp of how long a user can be late for a reservation.
		threshold = (timezone.now() - timedelta(minutes=tool.missed_reservation_threshold))
		threshold = datetime.replace(threshold, second=0, microsecond=0)  # Round down to the nearest minute.
		# Find the reservations that began exactly at the threshold.
		reservation = Reservation.objects.filter(cancelled=False, missed=False, shortened=False, tool=tool, user__is_staff=False, start=threshold, end__gt=timezone.now())
		for r in reservation:
			# Staff may abandon reservations.
			if r.user.is_staff:
				continue
			# If there was no tool enable or disable event since the threshold timestamp then we assume the reservation has been missed.
			if not (UsageEvent.objects.filter(tool=tool, start__gte=threshold).exists() or UsageEvent.objects.filter(
					tool=tool, end__gte=threshold).exists()):
				# Mark the reservation as missed and notify the user & NanoFab staff.
				r.missed = True
				r.save()
				missed_reservations.append(r)
	for r in missed_reservations:
		send_missed_reservation_notification(r)
