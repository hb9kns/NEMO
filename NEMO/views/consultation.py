from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from django.template import Template, Context
from django.views.decorators.http import require_http_methods
from django.core.files.storage import get_storage_class

from NEMO.utilities import parse_parameter_string
from NEMO.views.constants import FEEDBACK_MAXIMUM_LENGTH
from NEMO.views.customization import get_customization, get_media_file_contents


@login_required
@require_http_methods(['GET', 'POST'])
def consultation(request):
	recipient = get_customization('feedback_email_address')
	email_contents = get_media_file_contents('consultation_email.html')
	email_response_contents = get_media_file_contents('consultation_email_response.html')
	if not recipient or not email_contents or not email_response_contents:
		return render(request, 'feedback.html', {'customization_required': True})

	if request.method == 'GET':
		return render(request, 'consultation.html')
	contents = parse_parameter_string(request.POST, 'consultation', FEEDBACK_MAXIMUM_LENGTH)
	if contents == '':
		return render(request, 'consultation.html')
	dictionary = {
		'contents': contents,
		'user': request.user,
	}

	email = Template(email_contents).render(Context(dictionary))
	send_mail('Consultation Request from ' + str(request.user), '', request.user.email, [recipient], html_message=email)

	response_email = EmailMessage()
	email_body = Template(email_response_contents).render(Context(dictionary))
	storage = get_storage_class()()
	response_email.subject = 'Design Consultation Request Follow Up'
	response_email.from_email = recipient
	response_email.to = [request.user.email]
	response_email.body = email_body
	response_email.content_subtype = "html"
	response_email.attach_file(storage.path('design_consultation_template.pptx'))
	response_email.send()


	dictionary = {
		'title': 'Design Consultation Request',
		'heading': 'Request Sent!',
		'content': 'Your design consultation request has been sent to the PRISM Cleanroom staff. We will follow up with you as soon as we can.',
	}
	return render(request, 'acknowledgement.html', dictionary)
