from copy import deepcopy
from datetime import timedelta
from http import HTTPStatus
from itertools import chain

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import logger, require_GET, require_POST

from NEMO.forms import nice_errors, CommentForm
from NEMO.models import Comment, Configuration, ConfigurationHistory, Project, Reservation, StaffCharge, Task, TaskCategory, TaskStatus, Tool, UsageEvent, User
from NEMO.utilities import quiet_int, extract_times
from NEMO.views.policy import check_policy_to_enable_tool, check_policy_to_disable_tool, check_policy_to_note_pending_usage
from NEMO.views.customization import get_customization
from NEMO.widgets.dynamic_form import DynamicForm
from NEMO.widgets.tool_tree import ToolTree

@login_required
@require_GET
def tool_control(request, tool_id=None):
	""" Presents the tool control view to the user, allowing them to being/end using a tool or see who else is using it. """
	if request.user.active_project_count() == 0:
		return render(request, 'no_project.html')
	# The tool-choice sidebar is not available for mobile devices, so redirect the user to choose a tool to view.
	if request.device == 'mobile' and tool_id is None:
		return redirect('choose_tool', next_page='tool_control')
	tools = Tool.objects.filter(visible=True).order_by('category', 'name')
	dictionary = {
		'tools': tools,
		'selected_tool': tool_id,
	}
	# The tool-choice sidebar only needs to be rendered for desktop devices, not mobile devices.
	if request.device == 'desktop':
		dictionary['rendered_tool_tree_html'] = ToolTree().render(None, {'tools': tools, 'checktools': {'none'} })
	return render(request, 'tool_control/tool_control.html', dictionary)


@login_required
@require_GET
def tool_status(request, tool_id):
	""" Gets the current status of the tool (that is, whether it is currently in use or not). """
	tool = get_object_or_404(Tool, id=tool_id, visible=True)
	exclude=get_customization('exclude_from_usage')
	projects_to_exclude = []
	if exclude:
		projects_to_exclude = [int(s) for s in exclude.split() if s.isdigit()]
	dictionary = {
		'tool': tool,
		'task_categories': TaskCategory.objects.filter(stage=TaskCategory.Stage.INITIAL_ASSESSMENT),
		'rendered_configuration_html': tool.configuration_widget(request.user),
		'mobile': request.device == 'mobile',
		'task_statuses': TaskStatus.objects.exclude(name="default"),
		'post_usage_questions': DynamicForm(tool.post_usage_questions).render(),
		'active_projects_filtered': request.user.active_projects().exclude(id__in=projects_to_exclude)
	}

	try:
		current_reservations = Reservation.objects.filter(start__lt=timezone.now(), end__gt=timezone.now(), cancelled=False, missed=False, shortened=False, user=request.user, tool=tool)
		if current_reservations:
# ::::::::::::::::::::: dirty hack for now to cope with virtual tools:
# ::::::::::::::::::::: simply use the first of several current reservations!
			current_reservation = current_reservations[0]
			if request.user == current_reservation.user:
				dictionary['time_left'] = current_reservation.end
	except Reservation.DoesNotExist:
		pass

	if tool.pending_usage():
	# will be checked only if pending usage is allowed for tool
	# and if all three entries are not None and pending_user is not empty
		dictionary['pending_usage'] = True
		dictionary['pending_user'] = tool.pending_user
		dictionary['pending_operator'] = tool.pending_operator
		dictionary['pending_project'] = tool.pending_project
	else:
		dictionary['pending_usage'] = False

	try:
		next_4hrs = Reservation.objects.filter(start__gt=timezone.now(), start__lte=timezone.now()+timedelta(hours=4), cancelled=False, missed=False, shortened=False, tool=tool).order_by('start')
		if next_4hrs:
			next_res = next_4hrs[0]
			dictionary['next_res'] = next_res
	except Reservation.DoesNotExist:
		pass
	# Staff need the user list to be able to qualify users for the tool.
	if request.user.is_staff:
		dictionary['users'] = User.objects.filter(is_active=True)

	return render(request, 'tool_control/tool_status.html', dictionary)


@staff_member_required(login_url=None)
@require_GET
def use_tool_for_other(request):
	dictionary = {
		'users': User.objects.filter(is_active=True).exclude(id=request.user.id)
	}
	return render(request, 'tool_control/use_tool_for_other.html', dictionary)


@login_required
@require_POST
def tool_configuration(request):
	""" Sets the current configuration of a tool. """
	try:
		configuration = Configuration.objects.get(id=request.POST['configuration_id'])
	except:
		return HttpResponseNotFound('Configuration not found.')
	if configuration.tool.in_use():
		return HttpResponseBadRequest('Cannot change a configuration while a tool is in use.')
	if not configuration.user_is_maintainer(request.user):
		return HttpResponseBadRequest('You are not authorized to change this configuration.')
	try:
		slot = int(request.POST['slot'])
		choice = int(request.POST['choice'])
	except:
		return HttpResponseBadRequest('Invalid configuration parameters.')
	try:
		configuration.replace_current_setting(slot, choice)
	except IndexError:
		return HttpResponseBadRequest('Invalid configuration choice.')
	configuration.save()
	history = ConfigurationHistory()
	history.configuration = configuration
	history.slot = slot
	history.user = request.user
	history.setting = configuration.get_current_setting(slot)
	history.save()
	return HttpResponse()


@login_required
@require_POST
def create_comment(request):
	form = CommentForm(request.POST)
	if not form.is_valid():
		return HttpResponseBadRequest(nice_errors(form).as_ul())
	comment = form.save(commit=False)
	comment.content = comment.content.strip()
	comment.author = request.user
	comment.expiration_date = None if form.cleaned_data['expiration'] == 0 else timezone.now() + timedelta(days=form.cleaned_data['expiration'])
	comment.save()
	return redirect('tool_control')


@login_required
@require_POST
def hide_comment(request, comment_id):
	comment = get_object_or_404(Comment, id=comment_id)
	if comment.author_id != request.user.id and not request.user.is_staff:
		return HttpResponseBadRequest("You may only hide a comment if you are its author or a staff member.")
	comment.visible = False
	comment.hidden_by = request.user
	comment.hide_date = timezone.now()
	comment.save()
	return redirect('tool_control')


def determine_tool_status(tool):
	# Make the tool operational when all problems are resolved that require a shutdown.
	if tool.task_set.filter(force_shutdown=True, cancelled=False, resolved=False).count() == 0:
		tool.operational = True
	else:
		tool.operational = False
	tool.save()


@login_required
@require_POST
def enable_tool(request, tool_id, user_id, project_id, staff_charge, operator_id=None):
	""" Enable a tool for a user, or note pending usage for later. The user must be qualified to do so based on the lab usage policy. """

	if not settings.ALLOW_CONDITIONAL_URLS:
		return HttpResponseBadRequest('Tool control is only available on campus. We\'re working to change that! Thanks for your patience.')

	tool = get_object_or_404(Tool, id=tool_id)
	# operator_id used by disable_tool() in case of re-enabling for pending usage
	if operator_id:
		operator = get_object_or_404(User, id=operator_id)
	else:
		operator = request.user
	user = get_object_or_404(User, id=user_id)
	project = get_object_or_404(Project, id=project_id)
	staff_charge = staff_charge == 'true'
	if tool.get_current_usage_event():
		response = check_policy_to_note_pending_usage(tool, operator, user, project)
		if response.status_code != HTTPStatus.OK:
			return response
		return note_pending_usage(request, tool_id, user_id, project_id)
	else:
		response = check_policy_to_enable_tool(tool, operator, user, project, staff_charge)
	if response.status_code != HTTPStatus.OK:
		return response

	# All policy checks passed so enable the tool for the user.
	if tool.interlock and not tool.interlock.unlock():
		error_message = f"The interlock command for the {tool} failed. The error message returned: {tool.interlock.most_recent_reply}"
		logger.error(error_message)
		return HttpResponseServerError(error_message)

	# remove noted pending usage
	tool.clear_pending_usage()

	# Create a new usage event to track how long the user uses the tool.
	new_usage_event = UsageEvent()
	new_usage_event.operator = operator
	new_usage_event.user = user
	new_usage_event.project = project
	new_usage_event.tool = tool
	new_usage_event.save()

	if staff_charge:
		new_staff_charge = StaffCharge()
		new_staff_charge.staff_member = request.user
		new_staff_charge.customer = user
		new_staff_charge.project = project
		new_staff_charge.save()

	return response


@login_required
@require_POST
def disable_tool(request, tool_id):

	if not settings.ALLOW_CONDITIONAL_URLS:
		return HttpResponseBadRequest('Tool control is only available on campus.')

	tool = get_object_or_404(Tool, id=tool_id)
	if tool.get_current_usage_event() is None:
		return HttpResponse()
	current_usage_event = tool.get_current_usage_event()
	downtime = timedelta(minutes=quiet_int(request.POST.get('downtime')))
	response = check_policy_to_disable_tool(tool, request.user, downtime)
	if response.status_code != HTTPStatus.OK:
		return response
	try:
		current_reservation = Reservation.objects.get(start__lt=timezone.now(), end__gt=timezone.now(), cancelled=False, missed=False, shortened=False, user=current_usage_event.user, tool=tool)
		# Staff are exempt from mandatory reservation shortening when tool usage is complete.
		if request.user.is_staff is False:
			# Shorten the user's reservation to the current time because they're done using the tool.
			new_reservation = deepcopy(current_reservation)
			new_reservation.id = None
			new_reservation.pk = None
			new_reservation.end = timezone.now() + downtime
			new_reservation.save()
			current_reservation.shortened = True
			current_reservation.descendant = new_reservation
			current_reservation.save()
	except Reservation.DoesNotExist:
		pass

	# All policy checks passed so disable the tool for the user,
	# unless another usage is pending.
	# (We don't want to switch the tool off in this case!)
	if not tool.pending_usage():
		if tool.interlock and not tool.interlock.lock():
			error_message = f"The interlock command for the {tool} failed. The error message returned: {tool.interlock.most_recent_reply}"
			logger.error(error_message)
			return HttpResponseServerError(error_message)

	# End the current usage event for the tool
	current_usage_event.end = timezone.now() + downtime

	# Collect post-usage questions
	dynamic_form = DynamicForm(tool.post_usage_questions)
	current_usage_event.run_data = dynamic_form.extract(request)
	dynamic_form.charge_for_consumable(current_usage_event.user, current_usage_event.operator, current_usage_event.project, current_usage_event.run_data)

	current_usage_event.save()
	if request.user.charging_staff_time():
		existing_staff_charge = request.user.get_staff_charge()
		if existing_staff_charge.customer == current_usage_event.user and existing_staff_charge.project == current_usage_event.project:
			response = render(request, 'staff_charges/reminder.html', {'tool': tool})

	if tool.pending_usage():
		response = enable_tool(request, tool_id, tool.pending_user.id, tool.pending_project.id, staff_charge=False, operator_id=tool.pending_operator.id)

	return response


@login_required
@require_POST
def note_pending_usage(request, tool_id, user_id, project_id):
	""" Note pending usage of a tool. No staff charges. """
	if not settings.ALLOW_CONDITIONAL_URLS:
		return HttpResponseBadRequest('Tool control is only available on campus. We\'re working to change that! Thanks for your patience.')
	tool = get_object_or_404(Tool, id=tool_id)
	tool.pending_operator = request.user
	tool.pending_user = get_object_or_404(User, id=user_id)
	tool.pending_project = get_object_or_404(Project, id=project_id)
	tool.save()
	return HttpResponse()

@login_required
@require_GET
def cancel_pending_usage(request, tool_id):
	tool = get_object_or_404(Tool, id=tool_id)
# TODO: filter user against pending_user and pending_operator!
	tool.clear_pending_usage()
	return redirect('tool_control', tool_id)

@login_required
@require_GET
def past_comments_and_tasks(request):
	try:
		start, end = extract_times(request.GET)
	except:
		return HttpResponseBadRequest('Please enter a start and end date.')
	tool_id = request.GET.get('tool_id')
	try:
		tasks = Task.objects.filter(tool_id=tool_id, creation_time__gt=start, creation_time__lt=end)
		comments = Comment.objects.filter(tool_id=tool_id, creation_date__gt=start, creation_date__lt=end)
	except:
		return HttpResponseBadRequest('Task and comment lookup failed.')
	past = list(chain(tasks, comments))
	past.sort(key=lambda x: getattr(x, 'creation_time', None) or getattr(x, 'creation_date', None))
	past.reverse()
	dictionary = {
		'past': past,
	}
	return render(request, 'tool_control/past_tasks_and_comments.html', dictionary)


@login_required
@require_GET
def ten_most_recent_past_comments_and_tasks(request, tool_id):
	tasks = Task.objects.filter(tool_id=tool_id).order_by('-creation_time')[:10]
	comments = Comment.objects.filter(tool_id=tool_id).order_by('-creation_date')[:10]
	past = list(chain(tasks, comments))
	past.sort(key=lambda x: getattr(x, 'creation_time', None) or getattr(x, 'creation_date', None))
	past.reverse()
	past = past[0:10]
	dictionary = {
		'past': past,
	}
	return render(request, 'tool_control/past_tasks_and_comments.html', dictionary)
