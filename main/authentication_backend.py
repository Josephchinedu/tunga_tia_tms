from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailAndUsernameBackend(ModelBackend):
    """
    Authenticate using e-mail address or username.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        User = get_user_model()

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            return user

        elif user and not user.check_password(password):
            raise Exception("Invalid Credentials")

        elif not user:
            user = User.objects.filter(username=email).first()
            if user and user.check_password(password):
                return user

            elif user and not user.check_password(password):
                raise Exception("Invalid Credentials")

            elif not user:
                raise Exception("User does not exist")
