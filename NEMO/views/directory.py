from django.contrib.auth.decorators import login_required
from django.shortcuts import render


from NEMO.models import User
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
		access =  user.is_staff
		introday = user.date_joined.date()
		user_info = {'user':user, 'phone':user.phone, 'email':user.email, 'group':group, 'special':access, 'intro':introday }
		people.append(user_info)
	dictionary = {
		'people': people
	}
	return render(request, 'directory.html', dictionary)
