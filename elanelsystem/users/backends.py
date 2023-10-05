from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend,BaseBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None

class UserBackend(BaseBackend):
    model = get_user_model()
    def authenticate(
        self, request, username=None, password=None):
        try:
            user = self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None
        if user.check_password(password) and user is not None:
            return user

    def get_user(self, user_id):
        try:
            return self.model.objects.get(pk=user_id)
        except self.model.DoesNotExist:
            return None
        
