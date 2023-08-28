from xlsxwriter.workbook import Workbook
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

from django.shortcuts import render

from NEMO.models import User, Tool, Project, Account, PhysicalAccessLevel
from NEMO.models import ActivityHistory, MembershipHistory
from NEMO.views.customization import get_customization

@login_required
def directory(request):
	users = User.objects.filter(is_active=True).exclude(type__in=settings.USERTYPES_DIRECTORY_SUPPRESS).order_by('last_name')
	active_groups = Account.objects.filter(active=True)
	people = []
	try:
		affiliation = int(request.GET['affiliation'])
	except:
	 affiliation = None
	if affiliation:
		try:
			showgroup = Account.objects.get(id=affiliation)
		except:
			showgroup = None
	else:
		showgroup = None
	for user in users:
		staffperms = user.is_staff
		introday = user.date_joined.date()
		projects = [pjt.name for pjt in Project.objects.filter(user=user,active=True) if pjt.name[0:1] not in settings.PROJECTNAME_BEGIN_SUPPRESS]
		permgroups = [pg.name for pg in Group.objects.filter(user=user)]
		try:
			owning_all = Tool.objects.filter(primary_owner=user.id)
			owning = [tool for tool in owning_all if not tool.name.startswith(settings.TOOLNAME_BEGIN_SUPPRESS)]
		except:
			owning = []
		try:
			backup_all = Tool.objects.filter(backup_owners__in=[user.id])
			backup = [tool for tool in backup_all if not tool.name.startswith(settings.TOOLNAME_BEGIN_SUPPRESS)]
		except:
			backup = ["(none)"]
		user_info = {'user':user, 'special':staffperms, 'intro':introday, 'primary_owning':owning, 'backup_owning':backup, 'projects':projects, 'permgroups':permgroups }
		people.append(user_info)
	dictionary = { 'people': people, 'staffdisplay': request.user.is_staff, 'active_groups': active_groups, 'showgroup': showgroup }
	return render(request, 'directory.html', dictionary)

@login_required
def toolresponsibles(request, namesuffix='' ):
	''' generate list of tools sorted by locations, filtered
	for names ending with namesuffix and excluding suppressed tools
	'''
	tools = Tool.objects.filter(visible=True, name__iendswith=namesuffix).exclude(name__startswith=settings.TOOLNAME_BEGIN_SUPPRESS)
# create sorted list of unique tool locations
	locations = list( { t.location for t in tools } )
	locations.sort()
	locationlist = []
	for l in locations:
# loop over locations and tools for each location
		toollist = []
		for t in [ t for t in tools if t.location == l ]:
			powner = t.primary_owner.first_name[0]+'.'+t.primary_owner.last_name+( '' if t.primary_owner.is_active else ' (inactive)' )
			pid = t.primary_owner.id
# get id list of all backup owners for that tool
			bus = User.objects.filter(id__in=t.backup_owners.values_list('id', flat=True)).all()
# and also their initials plus name
			bowners = [ b.first_name[0]+'.'+b.last_name for b in bus ]
			toollist.append( { 'name':t.name, 'primary':powner, 'primary_id':pid, 'backup':bowners } )
		locationlist.append( { 'loc':l, 'tools':toollist } )
	dictionary = { 'toolname_suffix': namesuffix, 'locationlist': locationlist }
	return render(request, 'toolresponsibles.html', dictionary)

@staff_member_required(login_url=None)
@permission_required('NEMO.change_user', raise_exception=True)
def userlist(request):
	""" return user list in XLSX format """
	fn = 'usersNEMO-'+date.today().strftime("%y%m%d")+'.xlsx'
	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename = "%s"' % fn
	book = Workbook(response, {'in_memory': True})
	sheet = book.add_worksheet('user list')
	bold = book.add_format()
	bold.set_bold()
	italic = book.add_format()
	italic.set_italic()
	title = [ 'NEMO user list', date.today().strftime("%Y-%m-%d") ]
	sheet.write_row('A1', title, bold)
	columntitles = [
		'Id',
		'Active',
		':modified',
		':login',
		'Last name',
		'First name',
		'Username',
		'E-Mail',
		'Phone number',
		'Address',
		'Affiliation',
		'Position',
		'Personnel number',
		'Badge number',
		'User type',
		'Deposit',
		'Mentor',
		'Training required',
		'Access expiration',
		'Staff',
		'Technician',
		'Account manager',
		]
	columntitles += [ '[G] '+g.name for g in Group.objects.all() ]
	columntitles += [
		'Joined/Introday',
		'Mentor training',
		'Equiresp training',
		'Firefighting training',
		'Projects'
		]
	physicalaccess = PhysicalAccessLevel.objects.all()
	for a in physicalaccess:
		columntitles += [ '[A] '+a.name ]
		columntitles += [ ':modified' ]
	columntitles += [ 'Remarks' ]
	sheet.write_row('A2', columntitles, italic)

	# get content type ids for User and PhysicalAccessLevel objects (required for history)
	uctype = ContentType.objects.get_for_model(User.objects.first()).id
	pctype = ContentType.objects.get_for_model(PhysicalAccessLevel.objects.first()).id

	rownum = 3
	for u in User.objects.all().exclude(type__in=settings.USERTYPES_EXPORT_SUPPRESS).order_by('-is_active', 'last_name', 'first_name'):
		try:
			mentor = u.mentor.first_name+' '+u.mentor.last_name
		except:
			mentor = ''
		try:
			accexp = u.access_expiration.strftime("%Y-%m-%d")
		except:
			accexp = ''
		try:
			affiliation = u.affiliation.name
		except:
			affiliation = ''
		try:
			if Account.objects.filter(manager__in=[u]):
				accountmanager = True
			else:
				accountmanager = False
		except:
			accountmanager = False
		row = [ u.id, u.is_active ]
		# last activity change of this user
		try:
			lastact = ActivityHistory.objects.filter(object_id=u.id, content_type__id__exact=uctype).order_by('date').last()
			activitydate = lastact.date.strftime("%Y-%m-%d")
			if lastact.action != u.is_active:
				activitydate += ' ('+str(lastact.action)+')'
		except:
			activitydate = ''
		try:
			lastlogin = u.last_login.strftime('%Y-%m-%d')
		except:
			lastlogin = '(never)'
		row += [ activitydate, lastlogin ]
		row += [ u.last_name, u.first_name, u.username,
			u.email, u.phone, u.address, affiliation,
			u.position, u.personnel_number, u.badge_number,
			u.type.name, u.deposit, mentor,
			u.training_required, accexp,
			u.is_staff, u.is_technician, accountmanager,
			]
		row += [ g in u.groups.all() for g in Group.objects.all() ]
		try:
			mentortrained = u.mentor_trained.strftime("%Y-%m-%d")
		except:
			mentortrained = ''
		try:
			equitrained = u.equiresp_trained.strftime("%Y-%m-%d")
		except:
			equitrained = ''
		try:
			firetrained = u.fire_trained.strftime("%Y-%m-%d")
		except:
			firetrained = ''
		pjts = ''
		for p in Project.objects.filter(user=u,active=True):
			if p.name[0:1] not in settings.PROJECTNAME_BEGIN_SUPPRESS:
				pjts += p.name+' '
		row += [ u.date_joined.strftime("%Y-%m-%d"),
			mentortrained, equitrained, firetrained, pjts ]
		# membership activities of this user
		memberships = MembershipHistory.objects.filter(child_object_id=u.id, child_content_type__id__exact=uctype)
		for a in physicalaccess:
			has_it = a in u.physical_access_levels.all()
			row += [ has_it ]
			try:
				lastpact = memberships.filter(parent_object_id=a.id, parent_content_type__id__exact=pctype).order_by('date').last()
				activitydate = lastpact.date.strftime("%Y-%m-%d")
				if lastpact.action != has_it:
					activitydate += ' ('+str(lastpact.action)+')'
			except:
				activitydate = ''
			row += [ activitydate ]
		row += [ u.remarks ]
		sheet.write_row(rownum,0,row)
		rownum += 1
	book.close()
	return response
