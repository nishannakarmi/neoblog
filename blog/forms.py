from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from blog.models import Profile


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class UserProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('age', 'birth_date', 'sex', 'image')

    def save(self, commit=True, user=None):
        profile = super(UserProfileForm, self).save(commit=False)
        profile.user = user
        profile.save()

        return profile
