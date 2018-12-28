from django_filters import FilterSet, IsoDateTimeFilter, BooleanFilter
from django_filters.widgets import BooleanWidget

from NEMO.models import Reservation, UsageEvent, AreaAccessRecord, User


class ReservationFilter(FilterSet):
	start_gte = IsoDateTimeFilter('start', lookup_expr='gte')
	start_lt = IsoDateTimeFilter('start', lookup_expr='lt')
	missed = BooleanFilter('missed', widget=BooleanWidget())

	class Meta:
		model = Reservation
		fields = []


class UserFilter(FilterSet):
	class Meta:
		model = User
		fields = {
			'type': ['exact'],
			'physical_access_levels': ['exact'],
			'date_joined': ['month', 'year'],
		}

class UsageEventFilter(FilterSet):
	start_gte = IsoDateTimeFilter('start', lookup_expr='gte')
	start_lt = IsoDateTimeFilter('start', lookup_expr='lt')

	class Meta:
		model = UsageEvent
		fields = ['tool', 'user']


class AreaAccessRecordFilter(FilterSet):
	start_gte = IsoDateTimeFilter('start', lookup_expr='gte')
	start_lt = IsoDateTimeFilter('start', lookup_expr='lt')

	class Meta:
		model = AreaAccessRecord
		fields = ['area']
