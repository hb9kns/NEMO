from NEMO.views.customization import get_customization

def show_logout_button(request):
	return {'logout_allowed': True}


def hide_logout_button(request):
	return {'logout_allowed': False}


def device(request):
	return {'device': request.device}

def facility_name(request):
	try:
		facility_name = get_customization('facility_name')
	except:
		facility_name = 'Facility'
	if facility_name == '':
		facility_name = 'Facility'
	return {'facility_name': facility_name}
