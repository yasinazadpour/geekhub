from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MyUser as User


class JoinForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

class UpdateUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'image')