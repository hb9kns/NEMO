from xlsxwriter.workbook import Workbook
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from django.http import HttpResponse

from django.shortcuts import render

from NEMO.models import User, Tool, Project, Account, PhysicalAccessLevel
from NEMO.views.customization import get_customization

@login_required
def directory(request):
# exclude user types Test and Contact -- this should be defined in settings!
	user_exclude = [2,7]
	users = User.objects.filter(is_active=True).exclude(type__in=user_exclude).order_by('last_name')
	people = []
	for user in users:
		try:
			group = user.affiliation
		except:
			group = "unknown"
		staffperms = user.is_staff
		introday = user.date_joined.date()
		projects = [pjt.name for pjt in Project.objects.filter(user=user,active=True) if pjt.name[0:1] not in settings.PROJECTNAME_BEGIN_SUPPRESS]
		if staffperms:
			owning_all = Tool.objects.filter(primary_owner=user.id)
			owning = [tool for tool in owning_all if tool.name[0:1] not in settings.TOOLNAME_BEGIN_SUPPRESS]
			backup_all = [""]
			backup_all = Tool.objects.filter(backup_owners__in=[user.id])
			backup = [tool for tool in backup_all if tool.name[0:1] not in settings.TOOLNAME_BEGIN_SUPPRESS]
		else:
			owning = []
			backup = ["(none)"]
		user_info = {'user':user, 'phone':user.phone, 'email':user.email, 'group':group, 'special':staffperms, 'intro':introday, 'primary_owning':owning, 'backup_owning':backup, 'projects':projects }
		people.append(user_info)
	dictionary = {
		'people': people
	}
	return render(request, 'directory.html', dictionary)

@staff_member_required(login_url=None)
@permission_required('NEMO.change_user', raise_exception=True)
def userlist(request):
	""" return user list in XLSX format """
# exclude user type Test -- this should be defined in settings!
	user_exclude = [2]
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
		'Technician'
		]
	columntitles += [ g.name for g in Group.objects.all() ]
	columntitles += [
		'Joined/Introday',
		'Mentor training',
		'Equiresp training',
		'Firefighting training',
		'Projects'
		]
	columntitles += [ a.name+' access' for a in PhysicalAccessLevel.objects.all() ]
	columntitles += [ 'Remarks' ]
	sheet.write_row('A2', columntitles, italic)
	rownum = 3
	for u in User.objects.all().exclude(type__in=user_exclude).order_by('-is_active', 'last_name', 'first_name'):
#		try:
#			mentor = u.mentor.first_name+u.mentor.last_name
#		except:
#			mentor = ''
		mentor = ''
		try:
			accexp = u.access_expiration.strftime("%Y-%m-%d")
		except:
			accexp = ''
		try:
			affiliation = u.affiliation.name
		except:
			affiliation = ''
		row = [ u.id, u.is_active,
			u.last_name, u.first_name, u.username,
			u.email, u.phone, u.address, affiliation,
			u.position, u.personnel_number, u.badge_number,
			u.type.name, u.deposit, mentor,
			u.training_required, accexp,
			u.is_staff, u.is_technician
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
		row += [ a in u.physical_access_levels.all() for a in PhysicalAccessLevel.objects.all() ]
		row += [ u.remarks ]
		sheet.write_row(rownum,0,row)
		rownum += 1
	book.close()
	return response
