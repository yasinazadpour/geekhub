from django.contrib.auth.forms import UserCreationForm
from .models import MyUser as User


class JoinForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email')
