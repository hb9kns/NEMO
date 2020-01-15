from django.contrib.auth.decorators import login_required
from django.shortcuts import render


from NEMO.models import User
from NEMO.views.customization import get_customization

@login_required
def directory(request):
# exclude user types Test and Contact
	user_exclude = [2,7]
	projects_to_exclude = []
	exclude=get_customization('exclude_from_billing')
	if exclude:
		projects_to_exclude = [int(s) for s in exclude.split() if s.isdigit()]
	users = User.objects.filter(is_active=True).exclude(type__in=user_exclude).order_by('last_name')
	people = []
	for user in users:
		try:
			group = user.active_projects().exclude(id__in=projects_to_exclude).values_list('account__name', flat=True)[0]
		except:
			group = "unknown"
#		access =  user.physical_access_levels.filter(id=1).exists()
# staff/equiresp status is more useful
		access =  user.is_staff
		user_info = {'user':user, 'group':group, 'special':access }
		people.append(user_info)
	dictionary = {
		'people': people
	}
	return render(request, 'directory.html', dictionary)
