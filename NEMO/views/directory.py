from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from NEMO.models import User, Tool
from NEMO.views.customization import get_customization

@login_required
def directory(request):
# exclude user types Test and Contact
	user_exclude = [2,7]
	users = User.objects.filter(is_active=True).exclude(type__in=user_exclude).order_by('last_name')
	people = []
	for user in users:
		try:
			group = user.affiliation
		except:
			group = "unknown"
#		access =  user.physical_access_levels.filter(id=1).exists()
# staff/equiresp status is more useful
		staffperms = user.is_staff
		introday = user.date_joined.date()
		if staffperms:
			owning_all = Tool.objects.filter(primary_owner=user.id)
			owning = [tool for tool in owning_all if tool.name[0:1] not in settings.TOOLNAME_BEGIN_SUPPRESS]
			backup_all = [""]
			backup_all = Tool.objects.filter(backup_owners__in=[user.id])
			backup = [tool for tool in backup_all if tool.name[0:1] not in settings.TOOLNAME_BEGIN_SUPPRESS]
		else:
			owning = []
			backup = ["(none)"]
		user_info = {'user':user, 'phone':user.phone, 'email':user.email, 'group':group, 'special':staffperms, 'intro':introday, 'primary_owning':owning, 'backup_owning':backup }
		people.append(user_info)
	dictionary = {
		'people': people
	}
	return render(request, 'directory.html', dictionary)
