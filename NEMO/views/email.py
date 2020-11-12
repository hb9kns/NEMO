from logging import getLogger
from smtplib import SMTPException

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import Template, Context
from django.views.decorators.http import require_GET, require_POST

from NEMO.forms import EmailBroadcastForm
from NEMO.models import Tool, Account, Project, User, PhysicalAccessLevel
from NEMO.views.customization import get_media_file_contents


logger = getLogger(__name__)


@login_required
@require_GET
def get_email_form(request):
	recipient = request.GET.get('recipient', '')
	try:
		validate_email(recipient)
	except:
		return HttpResponseBadRequest('Recipient not valid.')
	return render(request, 'email/email_form.html', {'recipient': recipient})


@login_required
@require_GET
def get_email_form_for_user(request, user_id):
	recipient = get_object_or_404(User, id=user_id)
	return render(request, 'email/email_form.html', {'name': recipient.get_full_name(), 'recipient': recipient.email})


@login_required
@require_POST
def send_email(request):
	try:
		recipient = request.POST['recipient']
		validate_email(recipient)
		recipient_list = [recipient]
	except:
		return HttpResponseBadRequest('The intended recipient was not a valid email address. The email was not sent.')
	sender = request.user.email
	subject = request.POST.get('subject')
	body = request.POST.get('body')
	if request.POST.get('copy_me'):
		recipient_list.append(sender)
	try:
		email = EmailMultiAlternatives(subject, from_email=sender, bcc=recipient_list)
		email.attach_alternative(body, 'text/html')
		email.send()
	except SMTPException as error:
		error_message = 'NEMO was unable to send the email through the email server. The error message that NEMO received is: ' + str(error)
		logger.exception(error_message)
		dictionary = {
			'title': 'Email not sent',
			'heading': 'There was a problem sending your email',
			'content': error_message,
		}
		return render(request, 'acknowledgement.html', dictionary)
	dictionary = {
		'title': 'Email sent',
		'heading': 'Your email was sent',
	}
	return render(request, 'acknowledgement.html', dictionary)


@require_GET
def email_broadcast(request, audience=''):
	dictionary = {}
	if request.user.is_staff:
		if audience == 'tool':
			dictionary['search_base'] = Tool.objects.filter(visible=True)
		elif audience == 'project':
			dictionary['search_base'] = Project.objects.filter(active=True, account__active=True)
		elif audience == 'account':
			dictionary['search_base'] = Account.objects.filter(active=True)
		elif audience == 'physicalaccess':
			dictionary['search_base'] = PhysicalAccessLevel.objects.all()
		elif audience == 'all' or audience == 'equiresp' or audience == 'pjtresp' :
			dictionary['search_base'] = 'all'
			dictionary['all'] = True
		dictionary['audience'] = audience
	else:
		dictionary['audience'] = 'tool'
		dictionary['search_base'] = Tool.objects.filter(visible=True, primary_owner=request.user)
	return render(request, 'email/email_broadcast.html', dictionary)


@login_required
@require_GET
def compose_email(request):
	audience = request.GET.get('audience')
	selection = request.GET.get('selection')
	try:
		if audience == 'tool':
			users = User.objects.filter(qualifications__id=selection).distinct()
		elif request.user.is_staff:
			if audience == 'project':
				users = User.objects.filter(projects__id=selection).distinct()
			elif audience == 'account':
				users = User.objects.filter(affiliation=selection).distinct()
			elif audience == 'physicalaccess':
				users = User.objects.filter(physical_access_levels=selection).distinct()
			elif audience == 'equiresp':
				users = User.objects.filter(groups__name=settings.EQUIRESP_GROUP_NAME).distinct()
			elif audience == 'pjtresp':
				pjtmgrs = Account.objects.values_list('manager', flat=True)
				users = User.objects.filter(pk__in=pjtmgrs).distinct()
			elif audience == 'all':
				users = User.objects.all()
			else:
				dictionary = {'error': 'You specified an invalid audience'}
				return render(request, 'email/email_broadcast.html', dictionary)
		else:
			dictionary = {'error': 'You may not broadcast email to this audience'}
			return render(request, 'email/email_broadcast.html', dictionary)
	except:
		dictionary = {'error': 'You specified an invalid audience parameter'}
		return render(request, 'email/email_broadcast.html', dictionary)

	generic_email_sample = get_media_file_contents('generic_email.html')
	dictionary = {
		'audience': audience,
		'selection': selection,
		'users': users,
	}
	if generic_email_sample:
		generic_email_context = {
			'title': 'TITLE',
			'greeting': 'Greeting',
			'contents': 'Contents',
		}
		dictionary['generic_email_sample'] = Template(generic_email_sample).render(Context(generic_email_context))
	return render(request, 'email/compose_email.html', dictionary)

@login_required
@require_POST
def send_broadcast_email(request):
	if not get_media_file_contents('generic_email.html'):
		return HttpResponseBadRequest('Generic email template not defined. Visit the NEMO customizable_key_values page to upload a template.')
	form = EmailBroadcastForm(request.POST)
	if not form.is_valid():
		return render(request, 'email/compose_email.html', {'form': form})
	dictionary = {
		'title': form.cleaned_data['title'],
		'greeting': form.cleaned_data['greeting'],
		'contents': form.cleaned_data['contents'],
	}
	content = get_media_file_contents('generic_email.html')
	content = Template(content).render(Context(dictionary))
	users = None
	audience = form.cleaned_data['audience']
	selection = form.cleaned_data['selection']
	active_choice = form.cleaned_data['only_active_users']
	try:
		if audience == 'tool':
			users = User.objects.filter(qualifications__id=selection)
		elif audience == 'project':
			users = User.objects.filter(projects__id=selection)
		elif audience == 'account':
			users = User.objects.filter(projects__account__id=selection)
		elif audience == 'physicalaccess':
			users = User.objects.filter(physical_access_levels__id=selection)
		elif audience == 'equiresp':
			users = User.objects.filter(groups__name=settings.EQUIRESP_GROUP_NAME)
		elif audience == 'pjtresp':
			pjtmgrs = Account.objects.values_list('manager', flat=True)
			users = User.objects.filter(pk__in=pjtmgrs)
		elif audience == 'all':
			users = User.objects.all()
		if active_choice:
			users = users.filter(is_active=True)
	except:
		dictionary = {'error': 'Your email was not sent. There was a problem finding the users to send the email to.'}
		return render(request, 'email/compose_email.html', dictionary)
	if not users:
		dictionary = {'error': 'The audience you specified is empty. You must send the email to at least one person.'}
		return render(request, 'email/compose_email.html', dictionary)
	if audience == 'tool':
		t = Tool.objects.filter(id=selection)
		subject = t[0].name + ': ' + form.cleaned_data['subject']
	elif audience == 'equiresp':
		subject = '[equiresp]: ' + form.cleaned_data['subject']
	elif audience == 'pjtresp':
		subject = '[FIRST-Lab]: ' + form.cleaned_data['subject']
	elif audience == 'physicalaccess':
		p = PhysicalAccessLevel.objects.filter(id=selection)
		subject = p[0].name + ': ' + form.cleaned_data['subject']
	elif audience == 'project':
		p = Project.objects.filter(id=selection)
		subject = p[0].name + ': ' + form.cleaned_data['subject']
	else:
		subject = form.cleaned_data['subject']
	users = [x.email for x in users]
	if form.cleaned_data['copy_me']:
		users += [request.user.email]
	if form.cleaned_data['carbon_copy']:
		cc_recipient=form.cleaned_data['carbon_copy']
		try:
			validate_email(cc_recipient)
		except:
			return HttpResponseBadRequest('Cc:-Recipient not valid.')
		users += [cc_recipient]
	try:
		email = EmailMultiAlternatives(subject, from_email=request.user.email, bcc=set(users))
		email.attach_alternative(content, 'text/html')
		email.send()
	except SMTPException as e:
		dictionary = {
			'title': 'Email not sent',
			'heading': 'There was a problem sending your email',
			'content': 'NEMO was unable to send the email through the email server. The error message that NEMO received is: ' + str(e),
		}
		return render(request, 'acknowledgement.html', dictionary)
	dictionary = {
		'title': 'Email sent',
		'heading': 'Your email was sent',
	}
	return render(request, 'acknowledgement.html', dictionary)
