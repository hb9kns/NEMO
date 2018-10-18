from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from NEMO.forms import StockroomWithdrawForm
from NEMO.models import StockroomItem, User


@staff_member_required(login_url=None)
@require_http_methods(['GET', 'POST'])
def stockroom(request):
	form = StockroomWithdrawForm(request.POST or None, initial={'quantity': 1})

	dictionary = {
		'users': User.objects.filter(is_active=True),
		'stock': StockroomItem.objects.filter(visible=True).order_by('category', 'name'),
	}

	if form.is_valid():
		withdraw = form.save(commit=False)
		withdraw.merchant = request.user
		withdraw.save()
		withdraw.stock.quantity -= withdraw.quantity
		withdraw.stock.save()
		dictionary['success'] = 'The withdraw for {} was successfully logged.'.format(withdraw.customer)
		form = StockroomWithdrawForm(initial={'quantity': 1})
	else:
		if hasattr(form, 'cleaned_data') and 'customer' in form.cleaned_data:
			dictionary['projects'] = form.cleaned_data['customer'].active_projects()

	dictionary['form'] = form
	return render(request, 'stockroom.html', dictionary)
