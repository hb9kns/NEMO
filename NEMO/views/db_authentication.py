# /home/nemo/python/lib/python3.6/site-packages/NEMO/views/
# settings.py: AUTHENTICATION_BACKENDS = ['NEMO.views.db_authentication.DbAuthenticationBackend']

from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import ModelBackend
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from NEMO.models import User, UserAuth

class DbAuthenticationBackend(ModelBackend):

	@method_decorator(sensitive_post_parameters('password'))
	def authenticate(self, request, username=None, password=None, **keyword_arguments):
		if not username or not password:
			return None
		try:
			user = User.objects.get(username=username)
			user_auth = UserAuth.objects.get(username=username)
		except User.DoesNotExist:
			#logger.warning(f"Username {username} attempted to authenticate with LDAP, but that username does not exist in the NEMO database. The user was denied access.")
			return None

		if not user.is_active:
			#logger.warning(f"User {username} successfully authenticated with LDAP, but that user is marked inactive in the NEMO database. The user was denied access.")
			return None

		try:
			if check_password(password, user_auth.hash):
				return user
		except:
			return None
		return None
