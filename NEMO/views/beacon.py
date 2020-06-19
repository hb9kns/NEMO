from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

@require_GET
def beacon(request):
	return render(request, 'beacon.html')
