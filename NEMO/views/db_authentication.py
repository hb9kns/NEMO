# /home/nemo/python/lib/python3.6/site-packages/NEMO/views/
# settings.py: AUTHENTICATION_BACKENDS = ['NEMO.views.db_authentication.DbAuthenticationBackend']

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import ModelBackend
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from NEMO.models import UserAuth

class DbAuthenticationBackend(ModelBackend):

    @method_decorator(sensitive_post_parameters('password'))
    def authenticate(self, request, username=None, password=None, **keyword_arguments):
        User = get_user_model()
        try:
            user_auth = UserAuth.objects.get(username=username)
            if user_auth.validate_password(password):
                user = User.objects.get(username=username)
                return user
        except:
            return None
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
